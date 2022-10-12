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

data "aws_caller_identity" "current_identity" {}

locals {
  account_id = data.aws_caller_identity.current_identity.account_id
}

#LGBM model bucket
module "s3_bucket" {
  source = "./modules/s3"
  bucket_name = "${var.model_bucket}-${var.project_id}"
}

# image registry
# module "ecr_image" {
#    source = "./modules/ecr"
#    ecr_repo_name = "${var.ecr_repo_name}-${var.project_id}"
#    account_id = local.account_id
#    lambda_function_local_path = var.lambda_function_local_path
#    docker_image_local_path = var.docker_image_local_path
# }

output "account_id" {
    value = data.aws_caller_identity.current_identity.account_id
}
