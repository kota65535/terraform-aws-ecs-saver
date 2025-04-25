resource "aws_iam_role" "lambda" {
  name               = var.lambda_iam_role_name
  assume_role_policy = data.aws_iam_policy_document.assume_role_lambda.json
}

resource "aws_iam_role_policy" "lambda_ecs" {
  role   = aws_iam_role.lambda.name
  policy = data.aws_iam_policy_document.ecs.json
}

resource "aws_iam_role_policy" "lambda_logs" {
  role   = aws_iam_role.lambda.name
  policy = data.aws_iam_policy_document.logs.json
}

data "aws_iam_policy_document" "ecs" {
  statement {
    resources = ["*"]
    actions = [
      "ecs:ListClusters",
      "ecs:ListServices",
      "ecs:DescribeServices",
      "ecs:UpdateService",
      "ecs:TagResource",
      "ecs:UntagResource",
      "ecs:ListTasks",
      "ecs:StopTask",
      "ecs:StartTask",
    ]
  }
}

data "aws_iam_policy_document" "logs" {
  statement {
    resources = [
      "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.self.account_id}:*"
    ]
    actions = [
      "logs:CreateLogGroup"
    ]
  }
  statement {
    resources = [
      "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.self.account_id}:log-group:/aws/lambda/${var.lambda_name}:*"
    ]
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
  }
}

data "aws_iam_policy_document" "assume_role_lambda" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com"
      ]
    }
  }
}
