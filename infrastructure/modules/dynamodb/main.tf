resource "aws_dynamodb_table" "sales_preds_table_fromtf" {
  name = var.dynamodb_tablename
  billing_mode = "PAY_PER_REQUEST"
  table_class  = "STANDARD_INFREQUENT_ACCESS"
  hash_key = var.dynamodb_hashkey
  range_key = var.dynamodb_rangekey
  
  attribute {
    name = var.dynamodb_hashkey
    type = "N"
  }

  attribute {
    name = var.dynamodb_rangekey
    type = "N"
  }
}