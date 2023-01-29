import json
import logging
import os
from datetime import datetime

import boto3
from pytz import timezone

# ========== Environment Variables to be configured ==========
TIMEZONE = os.getenv("TIMEZONE", "UTC")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ecs = boto3.client("ecs")


def lambda_handler(event: dict, context: dict):
    logger.info(f"Input: {json.dumps(event)}")

    current_hour = str(datetime.now(tz=timezone(TIMEZONE)).hour)

    logger.info(f"current hour: {current_hour}")

    stop_ecs_services(current_hour)
    start_ecs_services(current_hour)


def stop_ecs_services(current_hour: str):
    services = get_ecs_services_by_tag("AutoStopTime", current_hour)
    services_to_stop = [s for s in services if s["desiredCount"] > 0]
    if not services_to_stop:
        logger.info("no services to stop.")
        return

    logger.info(f"{len(services_to_stop)} ECS services to stop.")
    for s in services_to_stop:
        logger.info(f'arn: {s["serviceArn"]}, name: {s["serviceName"]}')

    for s in services_to_stop:
        ecs.tag_resource(
            resourceArn=s["serviceArn"],
            tags=[{"key": "LastDesiredCount", "value": str(s["desiredCount"])}],
        )
        ecs.update_service(cluster=s["clusterArn"], service=s["serviceArn"], desiredCount=0)
        tasks = ecs.list_tasks(cluster=s["clusterArn"], serviceName=s["serviceArn"])
        for ta in tasks["taskArns"]:
            ecs.stop_task(cluster=s["clusterArn"], task=ta)


def start_ecs_services(current_hour: str):
    services = get_ecs_services_by_tag("AutoStartTime", current_hour)
    services_to_start = [s for s in services if s["desiredCount"] == 0]
    if not services_to_start:
        logger.info("no services to start.")
        return

    logger.info(f"{len(services_to_start)} ECS services to start.")
    desired_counts = []
    for s in services_to_start:
        desired_count = next((int(t["value"]) for t in s["tags"] if t["key"] == "LastDesiredCount"), 1)
        desired_counts.append(desired_count)
        logger.info(f'arn: {s["serviceArn"]}, name: {s["serviceName"]}, desiredCount: {desired_count}')

    for s, d in zip(services_to_start, desired_counts):
        ecs.untag_resource(resourceArn=s["serviceArn"], tagKeys=["LastDesiredCount"])
        ecs.update_service(cluster=s["clusterArn"], service=s["serviceArn"], desiredCount=d)


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
