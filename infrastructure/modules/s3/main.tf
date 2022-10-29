resource "aws_s3_bucket" "s3_bucket" {
    bucket = var.bucket_name
    force_destroy = true
}

resource "aws_s3_bucket_acl" "s3_bucket_acl" {
    bucket = aws_s3_bucket.s3_bucket.id
    acl = "private"
}

output "s3" {
  value = aws_s3_bucket.s3_bucket.bucket
}
