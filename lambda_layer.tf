module "lambda_layer" {
  source  = "kota65535/python-lambda-layer/aws"
  version = "0.2.0"

  name              = var.lambda_name
  python_version    = local.lambda_python_version
  requirements_path = "${path.module}/lambda/requirements.txt"
  output_path       = "${data.temporary_directory.lambda.id}/${var.lambda_name}-layer.zip"
}
