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

    if "current_hour" in event:
        # for debug purpose
        current_hour = event["current_hour"]
    else:
        current_hour = str(datetime.now(tz=timezone(TIMEZONE)).hour)

    logger.info(f"current hour: {current_hour}")

    stop_ecs_services(current_hour)
    start_ecs_services(current_hour)


def stop_ecs_services(current_hour: str):
    services = get_ecs_services_by_tag("AutoStopTime", current_hour)

    services_to_stop = []
    for s in services:
        stopped_count = next((int(t["value"]) for t in s["tags"] if t["key"] == "AutoStopCount"), 0)
        if s["runningCount"] <= stopped_count:
            continue
        services_to_stop.append((s, stopped_count))

    logger.info(f"{len(services_to_stop)} ECS services to stop.")
    for s, c in services_to_stop:
        logger.info(f'arn: {s["serviceArn"]}, name: {s["serviceName"]}, count: {c}')

    for s, c in services_to_stop:
        ecs.tag_resource(
            resourceArn=s["serviceArn"],
            tags=[{"key": "LastDesiredCount", "value": str(s["desiredCount"])}],
        )
        ecs.update_service(cluster=s["clusterArn"], service=s["serviceArn"], desiredCount=c)


def start_ecs_services(current_hour: str):
    services = get_ecs_services_by_tag("AutoStartTime", current_hour)

    services_to_start = []
    for s in services:
        desired_count = next((int(t["value"]) for t in s["tags"] if t["key"] == "LastDesiredCount"), 1)
        if s["runningCount"] >= desired_count:
            continue
        services_to_start.append((s, desired_count))

    logger.info(f"{len(services_to_start)} ECS services to start.")
    for s, c in services_to_start:
        logger.info(f'arn: {s["serviceArn"]}, name: {s["serviceName"]}, desiredCount: {c}')

    for s, c in services_to_start:
        ecs.untag_resource(resourceArn=s["serviceArn"], tagKeys=["LastDesiredCount"])
        ecs.update_service(cluster=s["clusterArn"], service=s["serviceArn"], desiredCount=c)


def get_ecs_services_by_tag(name, value):
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
                tags = s.get("tags", [])
                if next((t for t in tags if t["key"] == name and t["value"] == value), None):
                    services.append(s)
    return services


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


if __name__ == '__main__':
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(name)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    lambda_handler({"current_hour": ""}, {})