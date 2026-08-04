output "speech_to_text_lambda_function_url" {
	description = "The HTTP(S) URL endpoint for the Lambda function"
	value       = module.speech_to_text_lambda_function.lambda_function_url
}

output "get_response_lambda_function_url" {
	description = "The HTTP(S) URL endpoint for the Lambda function"
	value       = module.get_response_lambda_function.lambda_function_url
}

output "response_lambda_function_url" {
	description = "The HTTP(S) URL endpoint for the response API Gateway"
	value       = module.api_gateway.lambda_function_url
}

output "cognito_hosted_ui_url" {
	description = "The hosted UI URL for Cognito authentication"
	value       = module.api_gateway.cognito_hosted_ui_url
}

output "cognito_user_pool_client_id" {
	description = "The ID of the Cognito User Pool Client"
	value       = module.api_gateway.cognito_user_pool_client_id
}

output "cognito_user_pool_id" {
	description = "The ID of the Cognito User Pool"
	value       = module.api_gateway.cognito_user_pool_id
}