output "lambda_function_arn" {
	description = "The ARN of the Lambda function"
	value       = module.lambda_app.lambda_function_arn
}

output "lambda_function_name" {
	description = "The name of the Lambda function"
	value       = module.lambda_app.lambda_function_name
}

output "lambda_function_invoke_arn" {
	description = "The invoke ARN of the Lambda function"
	value       = module.lambda_app.lambda_function_invoke_arn
}

output "lambda_function_version" {
	description = "Latest published version of the Lambda function"
	value       = module.lambda_app.lambda_function_version
}

output "lambda_function_qualified_arn" {
	description = "The qualified ARN of the Lambda function"
	value       = module.lambda_app.lambda_function_qualified_arn
}

output "lambda_role_arn" {
	description = "The ARN of the Lambda execution IAM role"
	value       = module.lambda_app.lambda_role_arn
}

output "lambda_role_name" {
	description = "The name of the Lambda execution IAM role"
	value       = module.lambda_app.lambda_role_name
}

output "lambda_source_code_hash" {
	description = "Base64-encoded SHA256 hash of the Lambda deployment package"
	value       = module.lambda_app.lambda_source_code_hash
}

output "lambda_function_url" {
	description = "The HTTP(S) URL endpoint for the Lambda function"
	value       = module.lambda_app.lambda_function_url
}
