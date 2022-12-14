resource "aws_lambda_function" "lambda_function" {
  function_name = var.lambda_function_name
  description = "Sales Forecast lambda function from ECR image"
  image_uri = var.image_uri
  package_type = "Image"
  role = aws_iam_role.lambda_exec.arn
  tracing_config {
    mode = "Active"
  }
#  depends_on = [
#     null_resource.ecr_image # not working so far
#   ]
  memory_size = 1024
  timeout = 30
  environment {
    variables = {
      S3_BUCKET_NAME = var.bucket_name
      RUN_ID = "5651db4644334361b10296c51ba3af3e" #var.run_id
    }
  }
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name = "/aws/lambda/${aws_lambda_function.lambda_function.function_name}"
  retention_in_days = 30
}
