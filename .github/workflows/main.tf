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

module "ec2-saver" {
  source  = "kota65535/ec2-saver/aws"
  version = "0.0.1"
}
