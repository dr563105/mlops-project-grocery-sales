terraform {
  backend "s3" {
    bucket = "s3-for-terraform-state-mlops"
    key = "mlops-grocery-sales_stg.tfstate2"
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

module "ecr_image" {
  source = "./modules/ecr"
  ecr_repo_name = "${var.ecr_repo_name}_${var.project_id}"
  account_id = local.account_id
  //path of the lambda_function.py
  lambda_function_local_path = var.lambda_function_local_path
  //path of dockerfile to create docker image
  docker_image_local_path = var.docker_image_local_path
}

module "lambda_function" {
  source = "./modules/lambda"
  lambda_function_name = var.lambda_function_name
  image_uri = module.ecr_image.image_uri
  artifact_bucket = var.artifact_bucket
  mlflow_run_id = var.mlflow_run_id
  dbtable_name = var.dynamodb_tablename
  dynamodb_accountid = local.account_id
  dynamodb_region = var.aws_region
  depends_on = [
    module.ecr_image
  ]
}

module "dynamo_db" {
  source = "./modules/dynamodb"
  dynamodb_tablename = var.dynamodb_tablename
  dynamodb_hashkey = var.dynamodb_hashkey
  dynamodb_rangekey = var.dynamodb_rangekey
  depends_on = [ 
    module.lambda_function
  ]
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

output "run_id" {
  value = var.mlflow_run_id
}

output "lambda_function" {
  value = var.lambda_function_name
}

output "ecr_repo" {
  value = "${var.ecr_repo_name}_${var.project_id}"
}

