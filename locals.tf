locals {
  lambda_python_version = "3.13"
  terraform_tmp_dir     = "${path.root}/.terraform/tmp"
  lambda_zip_path       = "${local.terraform_tmp_dir}/lambda-${var.lambda_name}-${random_string.suffix.result}.zip"
}

data "aws_caller_identity" "self" {}

data "aws_region" "current" {}
