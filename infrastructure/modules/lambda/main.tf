resource "aws_lambda_function" "forecast-sales-lambda" {
  function_name = var.lambda_function_name
  # This can also be any base image to bootstrap the lambda config, unrelated to your Inference service on ECR
  # which would be anyway updated regularly via a CI/CD pipeline
  image_uri = var.image_uri   # required-argument
  package_type = "Image"
  role          = aws_iam_role.iam_lambda.arn
  tracing_config {
    mode = "Active"
  }
  timeout = 180
}