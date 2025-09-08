import boto3

from function import lambda_handler

ecs = boto3.client("ecs")


def test_scheduled_start():
    lambda_handler({"hour": 10, "weekday": 0}, {})
    res = ecs.describe_services(cluster="test", services=["test"])
    service = res["services"][0]
    assert service["desiredCount"] == 1


def test_scheduled_stop():
    lambda_handler({"hour": 11, "weekday": 0}, {})
    res = ecs.describe_services(cluster="test", services=["test"])
    service = res["services"][0]
    assert service["desiredCount"] == 0


def test_start_by_name():
    lambda_handler({"action": "start", "cluster": "test", "services": ["test"]}, {})
    res = ecs.describe_services(cluster="test", services=["test"])
    service = res["services"][0]
    assert service["desiredCount"] == 1


def test_stop_by_name():
    lambda_handler({"action": "stop", "cluster": "test", "services": ["test"]}, {})
    res = ecs.describe_services(cluster="test", services=["test"])
    service = res["services"][0]
    assert service["desiredCount"] == 0


def test_start_by_tags():
    lambda_handler({"action": "start", "tags": [{"key": "Project", "value": "test"}]}, {})
    res = ecs.describe_services(cluster="test", services=["test"])
    service = res["services"][0]
    assert service["desiredCount"] == 1


def test_stop_by_tags():
    lambda_handler({"action": "stop", "tags": [{"key": "Project", "value": "test"}]}, {})
    res = ecs.describe_services(cluster="test", services=["test"])
    service = res["services"][0]
    assert service["desiredCount"] == 0


def teardown_module():
    res = ecs.describe_services(cluster="test", services=["test"])
    service = res["services"][0]
    ecs.update_service(cluster=service["clusterArn"], service=service["serviceArn"], desiredCount=0)
