provider "aws" {
    region = var.aws_region
}

# IAM role for Lambda execution
data "aws_iam_policy_document" "assume_role" {
    statement {
        effect = "Allow"

        principals {
            type        = "Service"
            identifiers = ["lambda.amazonaws.com"]
        }

        actions = ["sts:AssumeRole"]
    }
}

resource "aws_iam_role" "example" {
    name               = var.lambda_role_name
    assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
    role       = aws_iam_role.example.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Package the Lambda function code
data "archive_file" "example" {
    type        = "zip"
    source_file = "${path.module}/${var.lambda_source_file}"
    output_path = "${path.module}/lambda/function.zip"
}

# Lambda function
resource "aws_lambda_function" "example" {
    filename         = data.archive_file.example.output_path
    function_name    = var.lambda_function_name
    role             = aws_iam_role.example.arn
    handler          = var.lambda_handler
    source_code_hash = data.archive_file.example.output_base64sha256

    runtime = var.lambda_runtime

    environment {
        variables = {
            ENVIRONMENT = var.environment
            LOG_LEVEL   = var.log_level
        }
    }

    tags = {
        Environment = var.environment
        Application = var.application_name
    }
}