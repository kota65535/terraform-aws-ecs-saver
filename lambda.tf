resource "aws_lambda_function" "main" {
  function_name    = var.lambda_name
  description      = "Start or stop ECS services at a specified time"
  handler          = "function.lambda_handler"
  filename         = data.archive_file.lambda_zip.output_path
  runtime          = "python${local.lambda_python_version}"
  role             = aws_iam_role.lambda.arn
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  layers           = [aws_lambda_layer_version.main.arn]
  timeout          = 30

  environment {
    variables = {
      TIMEZONE = var.timezone
    }
  }
}

resource "random_string" "suffix" {
  length  = 8
  special = false
}

resource "aws_lambda_permission" "events" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.main.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.rule.arn
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = local.lambda_zip_path

  source {
    content  = file("${path.module}/lambda/src/function.py")
    filename = "function.py"
  }
}
