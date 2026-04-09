module "lambda_app" {
  source = "./modules/lambda"

  aws_region           = var.aws_region
  lambda_function_name = var.lambda_function_name
  lambda_role_name     = var.lambda_role_name
  lambda_runtime       = var.lambda_runtime
  lambda_handler       = var.lambda_handler
  lambda_source_file   = var.lambda_source_file
  environment          = var.environment
  log_level            = var.log_level
  application_name     = var.application_name
}