terraform {
  backend "s3" {
    bucket       = "terraform-backend-561678142736"
    region       = "ap-northeast-1"
    key          = "terraform-aws-ecs-saver.tfstate"
    use_lockfile = true
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.96.0"
    }
    temporary = {
      source  = "kota65535/temporary"
      version = "1.0.1"
    }
  }
  required_version = "~> 1.11.0"
}

provider "aws" {
  region = "ap-northeast-1"
}

module "ecs_saver" {
  source = "../../"
}

resource "aws_ecs_cluster" "main" {
  name = "test"
}

resource "aws_iam_role" "ecs" {
  name               = "ecs-tasks-test"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_trust_relationship.json
}

resource "aws_iam_role_policy_attachment" "ecs" {
  role       = aws_iam_role.ecs.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

data "aws_iam_policy_document" "ecs_task_trust_relationship" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_ecs_service" "main" {
  name            = "test"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = ["subnet-0abaada26acb8894f"]
    assign_public_ip = true
  }
  tags = {
    Project       = "test"
    AutoStartTime = 10
    AutoStopTime  = 11
  }
}

resource "aws_ecs_task_definition" "main" {
  family                   = "test"
  execution_role_arn       = aws_iam_role.ecs.arn
  task_role_arn            = aws_iam_role.ecs.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  container_definitions = jsonencode([
    {
      name      = "ubuntu"
      image     = "public.ecr.aws/lts/ubuntu:20.04_stable"
      essential = true
      command   = ["tail", "-f"]
    },
  ])
}
