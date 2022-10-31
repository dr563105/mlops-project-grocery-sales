terraform {
  backend "s3" {
    bucket = "s3-for-terraform-state"
    key = "mlops-grocery-sales_stg.tfstate"
    region = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
}

data aws_caller_identity "current_identity" {}

locals {
  account_id = data.aws_caller_identity.current_identity.account_id
}

module "s3_bucket" {
  source = "./modules/s3"
  bucket_name = "${var.bucket_name}-${var.project_id}"
}

module "ecr_image" {
  source = "./modules/ecr"
  ecr_repo_name = "${var.ecr_repo_name}_${var.project_id}"
  account_id = local.account_id
  lambda_function_local_path = var.lambda_function_local_path
  docker_image_local_path = var.docker_image_local_path
}

module "api_gateway" {
  source = "./modules/gateway"
  rest_api_name = var.rest_api_name
  api_gateway_region = var.aws_region
  api_gateway_account_id = local.account_id
  lambda_function_name = module.lambda_function.lambda_function_name
  lambda_function_arn = module.lambda_function.lambda_function_arn

  depends_on = [
    module.lambda_function
  ]
}

module "lambda_function" {
  source = "./modules/lambda"
  lambda_function_name = var.lambda_function_name
  image_uri = module.ecr_image.image_uri
  bucket_name = module.s3_bucket.s3
  depends_on = [
    module.ecr_image
  ]
}

output "lambda_function" {
  value = var.lambda_function_name
}

output "model_bucket" {
  value = module.s3_bucket.s3
}

output "ecr_repo" {
  value = "${var.ecr_repo_name}_${var.project_id}"
}
