variable "aws_region" {
    description = "AWS region where resources will be created"
    type        = string
    default     = "eu-west-2"
}

variable "application_name" {
    description = "Name of the application"
    type        = string
}

variable "environment" {
    description = "Environment name (e.g., production, staging, development)"
    type        = string
}

# TODO make list of variables to feed into 
variable "lambda_invoke_arn" {
    description = "lambda invoke arn"
    type        = string
}

variable "lambda_function_name" {
    description = "lambda invoke arn"
    type        = string
}