resource "aws_iam_role" "lambda_exec" {
  name = "iam_${var.lambda_function_name}"
  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Effect": "Allow",
        "Sid": ""
      }
    ]
  }
  EOF
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# IAM for S3

resource "aws_iam_policy" "lambda_s3_role_policy" {
  name = "lambda_s3_policy"
  description = "IAM Policy for s3"
policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:Get*",
                "s3:List*"
            ],
            "Resource": [
                "arn:aws:s3:::${var.bucket_name}",
                "arn:aws:s3:::${var.bucket_name}/*"
            ]
        }
    ]
}
EOF
}


resource "aws_iam_role_policy_attachment" "iam-policy-attach" {
  role = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_s3_role_policy.arn
}
