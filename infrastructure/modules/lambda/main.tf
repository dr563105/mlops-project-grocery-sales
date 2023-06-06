resource "aws_lambda_function" "lambda_function" {
  function_name = var.lambda_function_name
  description = "Sales Forecast lambda function from ECR image from TF"
  image_uri = var.image_uri
  package_type = "Image"
  role = aws_iam_role.lambda_exec.arn
  tracing_config {
    mode = "Active"
  }
  memory_size = 1024
  timeout = 30
  environment {
    variables = {
      S3_BUCKET_NAME = var.artifact_bucket 
      RUN_ID = var.mlflow_run_id 
      DBTABLE_NAME = var.dbtable_name
    }
  }
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name = "/aws/lambda/${aws_lambda_function.lambda_function.function_name}"
  retention_in_days = 30
}
