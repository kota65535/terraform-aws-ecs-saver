terraform {
  backend "s3" {
    bucket = "terraform-backend-561678142736"
    region = "ap-northeast-1"
    key    = "terraform-aws-ecs-saver.tfstate"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.48.0"
    }
  }
  required_version = "~> 1.3.0"
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

resource "aws_ecs_task_definition" "main" {
  family                   = local.qualified_service_name
  execution_role_arn       = aws_iam_role.ecs.arn
  task_role_arn            = aws_iam_role.ecs.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_task_size.cpu
  memory                   = var.ecs_task_size.memory
