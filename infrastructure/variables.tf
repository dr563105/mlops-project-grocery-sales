variable "aws_region" {
  description = "AWS region to create resources"
  default = "us-east-1"
}

variable "project_id" {
  description = "Place to provide project id"
  default = "mlops-grocery-sales"
}

variable "model_bucket" {
  description = "Name of the s3 bucket"
}

variable "lambda_function_local_path" {
  description = "location of local lambda function"
}

variable "docker_image_local_path" {
  description = "location of local dockerfile"
}

variable "ecr_repo_name" {
  description = "ECR repo name"
}

variable "lambda_function_name" {
  description = "lambda function name"
}

