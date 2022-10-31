# Create a rest api gateway
resource "aws_api_gateway_rest_api" "rest_api" {
  name = var.rest_api_name
  description = "Terraform invoke lambda sales predictor function"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# Create a resource for prediction
resource "aws_api_gateway_resource" "rest_api_predict_resource" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  parent_id = aws_api_gateway_rest_api.rest_api.root_resource_id
  path_part = "predict"
}

# Create a POST method under the resource
resource "aws_api_gateway_method" "rest_api_post_method" {
  rest_api_id   = aws_api_gateway_rest_api.rest_api.id
  resource_id   = aws_api_gateway_resource.rest_api_predict_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# Create Gateway method response
resource "aws_api_gateway_method_response" "rest_api_post_method_response_200" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  resource_id = aws_api_gateway_resource.rest_api_predict_resource.id
  http_method = aws_api_gateway_method.rest_api_post_method.http_method
  status_code = "200"
}

# Create Integration for gateway with lambda
resource "aws_api_gateway_integration" "rest_api_post_method_integration" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  resource_id = aws_api_gateway_resource.rest_api_predict_resource.id
  http_method = aws_api_gateway_method.rest_api_post_method.http_method
  integration_http_method = "POST"
  type = "AWS"
  uri = var.lambda_function_arn #aws_lambda_function.lambda.invoke_arn
  timeout_milliseconds = 29000
}

# Create a integration response for the integration
resource "aws_api_gateway_integration_response" "post_method_integration_resp" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  resource_id = aws_api_gateway_resource.rest_api_predict_resource.id
  http_method = aws_api_gateway_method.rest_api_post_method.http_method
  status_code = aws_api_gateway_method_response.rest_api_post_method_response_200.status_code
  depends_on = [
    aws_api_gateway_integration.rest_api_post_method_integration
  ]
}

# Create API Gateway deployment
resource "aws_api_gateway_deployment" "sales_pred_deployment" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  depends_on = [
    aws_api_gateway_integration.rest_api_post_method_integration
  ]
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.rest_api_predict_resource.id,
      aws_api_gateway_method.rest_api_post_method.id,
      aws_api_gateway_integration.rest_api_post_method_integration.id
    ]))
  }
  lifecycle {
    create_before_destroy = true
  }
}

# Create a stage for the deployment
resource "aws_api_gateway_stage" "rest_api_stage" {
  deployment_id = aws_api_gateway_deployment.sales_pred_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.rest_api.id
  stage_name    = var.rest_api_stage_name
}

# Allow gateway to invoke lambda function
resource "aws_lambda_permission" "api_gateway_lambda" {
  statement_id = "AllowExecutionFromAPIGateway"
  action = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal = "apigateway.amazonaws.com"
  source_arn = "arn:aws:execute-api:${var.api_gateway_region}:${var.api_gateway_account_id}:${aws_api_gateway_rest_api.rest_api.id}/*/${aws_api_gateway_method.rest_api_post_method.http_method}${aws_api_gateway_resource.rest_api_predict_resource.path}"
}

# IAM for api
resource "aws_api_gateway_rest_api_policy" "api_allow_invoke" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  policy = <<EOF
  {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": [
        "execute-api:Invoke"
      ],
      "Resource": [
        "arn:aws:execute-api:${var.api_gateway_region}:${var.api_gateway_account_id}:${aws_api_gateway_rest_api.rest_api.id}/*/${aws_api_gateway_method.rest_api_post_method.http_method}${aws_api_gateway_resource.rest_api_predict_resource.path}"
      ]
    }
  ]
}
EOF
}
