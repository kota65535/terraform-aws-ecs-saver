import json
import logging
import os
from datetime import datetime

import boto3
from pytz import timezone

# ========== Environment Variables to be configured ==========
TIMEZONE = os.getenv("TIMEZONE", "UTC")

# ========== Logger ==========
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Boto3 client
ecs = boto3.client("ecs")


def lambda_handler(event: dict, context: dict):
    logger.info(f"Input: {json.dumps(event)}")

    if "action" in event:
        # Force start/stop a service

        action = event["action"]
        if action not in ["start", "stop"]:
            raise Exception(f"unsupported action: {action}")

        if "cluster" in event and "services" in event:
            cluster = event["cluster"]
            services = event["services"]
            if action == "stop":
                stop_ecs_services_by_name(cluster, services)
            if action == "start":
                start_ecs_services_by_name(cluster, services)
        elif "tags" in event:
            tags = event["tags"]
            if action == "stop":
                stop_ecs_services_by_tags(tags)
            if action == "start":
                start_ecs_services_by_tags(tags)
        else:
            raise Exception("either cluster/service or tags must be specified")
    else:
        # Scheduled start/stop

        now = datetime.now(tz=timezone(TIMEZONE))
        current_hour = now.hour
        current_weekday = now.isoweekday()

        # For debug
        if "hour" in event:
            current_hour = event["hour"]
        if "weekday" in event:
            current_weekday = event["weekday"]

        logger.info(f"hour: {current_hour}, weekday: {current_weekday}")

        stop_ecs_services_by_schedule(current_hour, current_weekday)
        start_ecs_services_by_schedule(current_hour, current_weekday)


def stop_ecs_services_by_name(cluster: str, services: list[str]):
    res = ecs.describe_services(cluster=cluster, services=services, include=["TAGS"])
    services = res["services"]
    stop_ecs_services(services)


def start_ecs_services_by_name(cluster: str, service: list[str]):
    res = ecs.describe_services(cluster=cluster, services=service, include=["TAGS"])
    services = res["services"]
    start_ecs_services(services)


def stop_ecs_services_by_tags(tags: list):
    services = get_ecs_services_by_tag(tags)
    stop_ecs_services(services)


def start_ecs_services_by_tags(tags: list):
    services = get_ecs_services_by_tag(tags)
    start_ecs_services(services)


def stop_ecs_services_by_schedule(current_hour: int, current_weekday: int):
    current_hour = str(current_hour)
    current_weekday = str(current_weekday)

    services = get_ecs_services_by_tag([{"key": "AutoStopTime", "value": current_hour}])
    # Check day of the week matches
    target_services = []
    for s in services:
        weekdays_str = next((t["value"] for t in s["tags"] if t["key"] == "AutoStopWeekday"), None)
        if weekdays_str:
            weekdays = weekdays_str.split()
            if current_weekday not in weekdays:
                continue
        target_services.append(s)

    stop_ecs_services(target_services)


def start_ecs_services_by_schedule(current_hour: int, current_weekday: int):
    current_hour = str(current_hour)
    current_weekday = str(current_weekday)

    services = get_ecs_services_by_tag([{"key": "AutoStartTime", "value": current_hour}])
    # Check day of the week matches
    target_services = []
    for s in services:
        weekdays_str = next((t["value"] for t in s["tags"] if t["key"] == "AutoStartWeekday"), None)
        if weekdays_str:
            weekdays = weekdays_str.split()
            if current_weekday not in weekdays:
                continue
        target_services.append(s)

    start_ecs_services(target_services)


def stop_ecs_services(services: list):
    target_services = []
    for s in services:
        # Check if the service is already stopped
        stopped_count = next((int(t["value"]) for t in s["tags"] if t["key"] == "AutoStopCount"), 0)
        if s["runningCount"] <= stopped_count:
            continue
        target_services.append((s, stopped_count))

    if target_services:
        info = "\n".join([f'arn: {s[0]["serviceArn"]}, count: {s[1]}' for s in target_services])
        logger.info(f"stopping {len(target_services)} services:\n{info}")
    else:
        logger.info("no services to stop")

    for s, c in target_services:
        # Save the current desired task count as tag
        ecs.tag_resource(
            resourceArn=s["serviceArn"],
            tags=[{"key": "LastDesiredCount", "value": str(s["desiredCount"])}],
        )
        # Stop service
        ecs.update_service(cluster=s["clusterArn"], service=s["serviceArn"], desiredCount=c)


def start_ecs_services(services: list):
    target_services = []
    for s in services:
        # Check if the service is already started
        desired_count = next((int(t["value"]) for t in s["tags"] if t["key"] == "LastDesiredCount"), 1)
        if s["runningCount"] >= desired_count:
            continue
        target_services.append((s, desired_count))

    if target_services:
        info = "\n".join([f'arn: {s[0]["serviceArn"]}, count: {s[1]}' for s in target_services])
        logger.info(f"starting {len(target_services)} services:\n{info}")
    else:
        logger.info("no services to start")

    for s, c in target_services:
        # Remove the last desired task count tag
        ecs.untag_resource(resourceArn=s["serviceArn"], tagKeys=["LastDesiredCount"])
        # Start service
        ecs.update_service(cluster=s["clusterArn"], service=s["serviceArn"], desiredCount=c)


def get_ecs_services_by_tag(tags):
    res = ecs.list_clusters()
    cluster_arns = res["clusterArns"]
    while "nextToken" in res:
        res = ecs.list_clusters(nextToken=res["nextToken"])
        cluster_arns += res["clusterArns"]

    services = []
    for ca in cluster_arns:
        res = ecs.list_services(cluster=ca)
        service_arns = res["serviceArns"]
        while "nextToken" in res:
            res = ecs.list_services(cluster=ca, nextToken=res["nextToken"])
            service_arns += res["serviceArns"]

        for sas in chunks(service_arns, 10):
            res = ecs.describe_services(cluster=ca, services=sas, include=["TAGS"])
            for s in res["services"]:
                service_tags = s.get("tags", [])
                if all((t in service_tags) for t in tags):
                    services.append(s)
    return services


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


if __name__ == "__main__":
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(name)s %(levelname)s %(message)s"))
    logger.addHandler(handler)

    lambda_handler({"hour": 22, "weekday": 2}, {})
    # lambda_handler({"action": "start", "tags": [{"key": "Project", "value": "sample-ts"}]}, {})
    # lambda_handler(
    #     {"action": "start", "tags": [{"key": "Project", "value": "sample-ts"}, {"key": "Island", "value": "01"}]}, {}
    # )
    # lambda_handler({"action": "stop", "cluster": "sample-ts", "service": "sample-ts-server-01"}, {})
    # lambda_handler({"action": "start", "cluster": "sample-ts", "service": "sample-ts-server-01"}, {})
