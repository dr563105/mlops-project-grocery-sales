
# Create a IAM role. Add trust policy to it.
resource "aws_iam_role" "lambda_exec" {
  name = "iam_${var.lambda_function_name}"
  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [{
        "Action": "sts:AssumeRole",
        "Principal": {
            "Service": "lambda.amazonaws.com"
    },
    "Effect": "Allow",
    "Sid": ""
    }]
  })
}

# IAM for Lambda to access S3 artifacts bucket
resource "aws_iam_policy" "lambda_s3artifact_role_policy" {
  name = "policy-s3-artifact-access-to-lambda"
  description = "IAM Policy for s3-artifact-access-to-lambda"
  policy = jsonencode({
"Version": "2012-10-17",
"Statement": [{
    "Sid": "VisualEditor0",
    "Effect": "Allow",
    "Action": [
        "s3:Get*",
        "s3:List*"
    ],
    "Resource": [
        "arn:aws:s3:::${var.artifact_bucket}",
        "arn:aws:s3:::${var.artifact_bucket}/*"
    ]}]
 })
}

#Policy for lambda to dynamodb
resource "aws_iam_policy" "lambda_dynamodb" {
  name = "policy_lambda_access_to_dynamodb"
  description = ""
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": [
            "dynamodb:BatchGetItem",
            "dynamodb:GetItem",
            "dynamodb:Query",
            "dynamodb:Scan",
            "dynamodb:BatchWriteItem",
            "dynamodb:PutItem",
            "dynamodb:UpdateItem",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
            "logs:CreateLogGroup" 
        ],
        "Resource": "arn:aws:dynamodb:${var.dynamodb_region}:${var.dynamodb_accountid}:table/${var.dbtable_name}"
    }]
  })
}

# iam_policy_arn = [
#    aws_iam_policy.lambda_s3artifact_role_policy.arn,
#    aws_iam_policy.lambda_dynamodb.arn,
#    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
# ]

# ## Attaching the policy to the role
# resource "aws_iam_role_policy_attachment" "lambda_exec_rolefromTF-policy-attachment" {
#     role = aws_iam_role.lambda_exec.name
#     count = "${length(iam_policy_arn)}"
#     policy_arn = "${iam_policy_arn[count.index]}"
# }

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
resource "aws_iam_role_policy_attachment" "iam-s3-policy-attach" {
  role = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_s3artifact_role_policy.arn
}
resource "aws_iam_role_policy_attachment" "iam-dynamodb-policy-attach" {
  role = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_dynamodb.arn
}