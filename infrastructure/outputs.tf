output "speech_to_text_lambda_function_url" {
	description = "The HTTP(S) URL endpoint for the Lambda function"
	value       = module.speech_to_text_lambda_function.lambda_function_url
}