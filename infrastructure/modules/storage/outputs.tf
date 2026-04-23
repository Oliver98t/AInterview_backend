# Source Code Hash Output
output "dynamodb_table_name" {
    description = "Base64-encoded SHA256 hash of the Lambda deployment package"
    value       = aws_dynamodb_table.response_table.name
}

# Lambda Function URL Output
output "dynamodb_table_arn" {
    description = "The HTTP(S) URL endpoint for the Lambda function"
    value       = aws_dynamodb_table.response_table.arn
}