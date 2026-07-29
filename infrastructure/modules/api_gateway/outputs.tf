# API Gateway URL Output
output "lambda_function_url" {
    description = "The HTTP(S) URL endpoint for the API Gateway"
    value       = aws_apigatewayv2_stage.default.invoke_url
}
