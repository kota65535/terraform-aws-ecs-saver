locals {
  lambda_python_version = "3.9"
  lambda_dir            = "${path.module}/lambda"
  terraform_tmp_dir     = "${path.root}/.terraform/tmp"
  lambda_zip_path       = "${local.terraform_tmp_dir}/lambda-${var.lambda_name}-${random_string.suffix.result}.zip"
  layer_zip_path        = "${local.terraform_tmp_dir}/layer-${var.lambda_name}-${random_string.suffix.result}.zip"
}

data "aws_caller_identity" "self" {}

data "aws_region" "current" {}
