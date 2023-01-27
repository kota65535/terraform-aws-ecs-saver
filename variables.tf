variable "lambda_name" {
  description = "Lambda name"
  type        = string
  default     = "ecs-saver"
}

variable "lambda_iam_role_name" {
  description = "Lambda IAM role name"
  type        = string
  default     = "ecs-saver"
}

variable "time_zone" {
  type    = string
  default = "UTC"
}
