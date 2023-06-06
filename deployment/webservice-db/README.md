## Instructions for ECR

aws ecr create-repository --repository-name lambda-images
docker build -t lambda-sales-predictor:v2 . # build docker image
docker tag lambda-sales-predictor:v2 ${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/lambda-images:sales-predictor # Tag it for ECR. Use `docker images` when in doubt.
docker push ${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/lambda-images:sales-predictor

### Permissions for Lambda function

The lambda function needs access to s3 bucket so we create a custom policy and attaching it to the function.

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:Get*",
                "s3:List*"
            ],
            "Resource": "*"
        }
    ]
}
```
Allocate at least 1024MB of Max memory and adjust the timeout to 30s. Add in the env variable as necessary.


Step 1: Create ECR repo and upload image to ECR. See [here](#instructions-for-ecr).

Step 2: Create Lambda function from ECR repo image. See [here](https://github.com/alexeygrigorev/aws-lambda-docker/blob/main/guide.md#creating-the-lambda-function).
For permissions go [here](#permissions-for-lambda-function).

Step 3: Create API Gateway.

We create a REST API gateway to invoke Lambda function.
Rest API->new resource->new POST method->Give permission to lambda->Test->Deploy API->Get the invoke URL->Append resource to it->Test it with a client(Postman, thunder client) or curl.

For instructions see [here](https://github.com/alexeygrigorev/aws-lambda-docker/blob/main/guide.md#creating-the-api-gateway).

Step 4: Testing. Use the following JSON object to test the API inside your favourite REST API client(Postman, Thunder Client)

Use this JSON object to test.
```
{"find": {"date1": "2017-08-26", "store_nbr": 20}}
```
