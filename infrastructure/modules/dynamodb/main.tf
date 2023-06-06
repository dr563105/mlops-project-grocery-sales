resource "aws_dynamodb_table" "sales_preds_table_fromtf" {
  name = var.dynamodb_tablename
  billing_mode = "PAY_PER_REQUEST"
  table_class  = "STANDARD_INFREQUENT_ACCESS"
  hash_key = var.dynamodb_hashkey
  range_key = var.dynamodb_rangekey
  
  attribute {
    name = "store_id"#var.dynamodb_hash_key
    type = "N"
  }

  attribute {
    name ="item_id" # var.dynamodb_range_key
    type = "N"
  }
  
  # attribute {
  #   name = "item_family"
  #   type = "S"
  # } 
  # attribute {
  #   name = "prediction_date"
  #   type = "S"
  # }
  
  # attribute {
  #   name = "unit_sales"
  #   type = "S"
  # }
}