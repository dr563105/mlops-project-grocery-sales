## Terraform - ECR, Lambda, API Gateway
Terraform keeps track of infrastructure as Github does for source code. We can version infrastructures as needed.

So, for our purpose we can use Terraform to deploy the built docker image into AWS ECR, use it in AWS Lambda, and link an API gateway to trigger the lambda function. All the setup for this is present inside [infrastructure](infrastructure).

1. Install terraform(for ubuntu)
```bash
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```
2. Create a S3 bucket to store Terraform state files. That name must go inside [main.tf](infrastructure/main.tf) as `bucket` name and the file as `key`.

3. Initialise and apply configurations
```
terraform init
terraform apply -var-file vars/stg.tfvars # Should see plan to add 20 components. Give `yes` to continue
```
4. Testing. Copy the `rest_api_url` displayed, use a REST API client, select `POST` as method and in the `body` supply the following JSON
```
{"find": {"date1": "2017-08-26", "store_nbr": 20}}
```
5. To destroy resource after testing
```
terraform apply -var-file vars/stg.tfvars # error may occur in deleting ECR repo as image is present. Manually delete the image before executing destroy command.
```