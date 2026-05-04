output "speech_to_text_lambda_function_url" {
	description = "The HTTP(S) URL endpoint for the Lambda function"
	value       = module.speech_to_text_lambda_function.lambda_function_url
}

output "get_response_lambda_function_url" {
	description = "The HTTP(S) URL endpoint for the Lambda function"
	value       = module.get_response_lambda_function.lambda_function_url
}

output "response_lambda_function_url" {
	description = "The HTTP(S) URL endpoint for the Lambda function"
	value       = module.response_lambda_function.lambda_function_url
}