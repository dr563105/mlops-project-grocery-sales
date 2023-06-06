variable "aws_region" {
  default = "us-east-1"
}

variable "artifact_bucket" {
  description = "s3 bucket where MLflow artifacts are stored"
  default = "mlops-project-sales-forecast-bucket"
}

variable "project_id" {
    default = "dr563105-mlops-project"
}

variable "lambda_function_local_path" {
  type = string
  description = "Local lambda_function.py path"
}

variable "docker_image_local_path" {
  type = string
  description = "Local dockerfile path."
}

variable "ecr_repo_name" {
  type = string
  description = "AWS ECR repository's name"
}

variable "lambda_function_name" {
  type = string
  description = "AWS Lambda function name"
}

variable "rest_api_name" {
  description = "AWS API gateway Rest api name"
}

variable "mlflow_run_id" {
  description = "Run id of the training run for which model artifact will be download"
}

variable "dynamodb_hashkey" {
}

variable "dynamodb_rangekey" {
}

variable "dynamodb_tablename" {

}