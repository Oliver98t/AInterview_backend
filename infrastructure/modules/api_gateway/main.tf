resource "aws_apigatewayv2_api" "api" {
    name          = "${var.application_name}_${var.environment}_api"
    protocol_type = "HTTP"

    cors_configuration {
        allow_credentials = false
        allow_origins     = ["*"]
        allow_methods     = ["GET", "POST", "OPTIONS"]
        allow_headers     = [
            "Content-Type",
            "Authorization",
            "X-Amz-Date",
            "X-Amz-Security-Token",
            "X-Amz-Content-Sha256",
            "X-Api-Key"
        ]
        expose_headers    = ["*"]
        max_age           = 86400
    }
}

resource "aws_apigatewayv2_stage" "default" {
    api_id      = aws_apigatewayv2_api.api.id
    name        = "$default"
    auto_deploy = true
}

resource "aws_apigatewayv2_integration" "lambda" {
    api_id                 = aws_apigatewayv2_api.api.id
    integration_type       = "AWS_PROXY"
    integration_uri        = var.lambda_invoke_arn
    payload_format_version = "2.0"
}

# Cognito User Pool
resource "aws_cognito_user_pool" "main" {
  name = "${var.application_name}_${var.environment}_user_pool"

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  user_attribute_update_settings {
    attributes_require_verification_before_update = ["email"]
  }

  tags = {
    Environment = var.environment
    Application = var.application_name
  }

  lifecycle {
    ignore_changes = [schema]
  }
}

# Cognito User Pool Client
resource "aws_cognito_user_pool_client" "main" {
  name            = "${var.application_name}_${var.environment}_client"
  user_pool_id    = aws_cognito_user_pool.main.id
  
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]

  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code", "implicit"]
  allowed_oauth_scopes                 = ["email", "openid", "profile"]
  
  callback_urls = var.callback_urls
  logout_urls   = var.logout_urls

  supported_identity_providers = ["COGNITO"]

  generate_secret = false
}

# Cognito User Pool Domain (for hosted UI)
resource "aws_cognito_user_pool_domain" "main" {
  domain       = "${lower(var.application_name)}-${var.environment}-${var.aws_region}"
  user_pool_id = aws_cognito_user_pool.main.id
}

# API Gateway Authorizer
resource "aws_apigatewayv2_authorizer" "cognito" {
  api_id           = aws_apigatewayv2_api.api.id
  authorizer_type  = "JWT"
  name             = "${var.application_name}_${var.environment}_cognito_auth"
  identity_sources = ["$request.header.Authorization"]

  jwt_configuration {
    audience = [aws_cognito_user_pool_client.main.id]
    issuer   = "https://cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.main.id}"
  }
}

resource "aws_apigatewayv2_route" "get" {
    api_id             = aws_apigatewayv2_api.api.id
    route_key          = "GET /response"
    authorization_type = "JWT"
    authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
    target             = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "post" {
    api_id             = aws_apigatewayv2_api.api.id
    route_key          = "POST /response"
    authorization_type = "JWT"
    authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
    target             = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_lambda_permission" "apigw" {
    statement_id  = "AllowAPIGatewayInvoke"
    action        = "lambda:InvokeFunction"
    function_name = var.lambda_function_name
    principal     = "apigateway.amazonaws.com"
    source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}