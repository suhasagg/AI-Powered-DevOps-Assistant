terraform { required_providers { aws = { source = "hashicorp/aws" } } }
provider "aws" { region = var.region }
variable "region" { default = "us-east-1" }
# Skeleton deliberately avoids broad IAM grants. Add narrowly scoped roles per integration/action.
resource "aws_cloudwatch_log_group" "assistant" { name = "/ai-devops-assistant/app" retention_in_days = 30 }
