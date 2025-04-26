resource "aws_cloudwatch_event_rule" "rule" {
  name                = var.lambda_name
  description         = "Kick ${var.lambda_name} lambda function every hour"
  schedule_expression = "cron(0,20,40 * * * ? *)"
}

resource "aws_cloudwatch_event_target" "target" {
  rule      = aws_cloudwatch_event_rule.rule.name
  target_id = "LambdaFunction"
  arn       = aws_lambda_function.main.arn
}
