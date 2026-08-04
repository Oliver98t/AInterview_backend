# API Gateway URL Output
output "lambda_function_url" {
    description = "The HTTP(S) URL endpoint for the API Gateway"
    value       = aws_apigatewayv2_stage.default.invoke_url
}

output "cognito_user_pool_id" {
    description = "The ID of the Cognito User Pool"
    value       = aws_cognito_user_pool.main.id
}

output "cognito_user_pool_client_id" {
    description = "The ID of the Cognito User Pool Client"
    value       = aws_cognito_user_pool_client.main.id
}

output "cognito_user_pool_client_secret" {
    description = "The secret of the Cognito User Pool Client"
    value       = aws_cognito_user_pool_client.main.client_secret
    sensitive   = true
}

output "cognito_hosted_ui_url" {
    description = "The hosted UI URL for Cognito authentication"
    value       = "https://${aws_cognito_user_pool_domain.main.domain}.auth.${var.aws_region}.amazoncognito.com"
}
