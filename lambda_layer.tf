data "external" "lambda_layer" {
  program = ["${local.lambda_dir}/scripts/create_lambda_layer.sh", local.lambda_python_version, "${local.lambda_dir}/requirements.txt"]
}

data "archive_file" "layer_zip" {
  type             = "zip"
  output_path      = local.layer_zip_path
  source_dir       = data.external.lambda_layer.result.path
  output_file_mode = "0644"
}

resource "aws_lambda_layer_version" "main" {
  layer_name          = var.lambda_name
  filename            = data.archive_file.layer_zip.output_path
  compatible_runtimes = ["python${local.lambda_python_version}"]
  source_code_hash    = data.archive_file.layer_zip.output_base64sha256
}
