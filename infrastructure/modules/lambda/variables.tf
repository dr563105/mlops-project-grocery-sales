variable "lambda_function_name" {
  type = string
  description = "The lambda function name"
}

variable "image_uri" {
  description = "ecr image uri"
}

# variable "bucket_name" {
#   type = string
#   description = "The s3 bucket name"
# }

variable "artifact_bucket" {
  type = string
}

variable "mlflow_run_id" {
  description = "Name of the run id of the artifact to download"
}

variable "dbtable_name" {
}

variable "dynamodb_accountid" {
}

variable "dynamodb_region" {
}