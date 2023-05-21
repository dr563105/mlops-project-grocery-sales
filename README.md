# Grocery Sales Forcasting

## Problem Statement

The sales department of a grocery chain wants to build an unit sales prediction engine(a web service application). Their ML engineer has already a predictor ML model but they don't know how to bring that model into production. The task here is to use necessary MLOPS tools, design and manage production workflow.
## MLOPS model pipeline tools

1. [MLFlow](https://www.mlflow.org) for experiment tracking
2. [Prefect 2.0](https://orion-docs.prefect.io) as workflow orchestration tool
3. [AWS S3 bucket](https://aws.amazon.com/s3/) to store workflow artifacts
4. [Docker](https://www.docker.com) for deployment in a container locally
5. [AWS ECR](https://aws.amazon.com/ecr/) to store the built docker container
6. [AWS Lambda](https://aws.amazon.com/lambda/) to build a serverless deployment solution
7. [Terraform](https://www.terraform.io) to automate infrastructure

# Test the workflow

**Streamlit**

For a quick demo checkout the deployed Streamlit [app](https://dr563105-streamlit-predict-sales-predictor-0bd7p9.streamlitapp.com).

**AWS API Gateway triggering Lambda function**

Use REST API client. Set method as `post`. Give this [link](https://i3pdoqdr92.execute-api.us-east-1.amazonaws.com/stg/predict) for send request. Supply the following JSON object as `body`. You should receive a JSON object back as output(respose body) with prediction.
```
{"find": {"date1": "2017-08-17", "store_nbr": 20}}
```
> If you're looking for comprehensive testing of the workflow, then jump to ["how to run" section](#how-to-run).
## Dataset

The data comes from Kaggle competition - [Corporación Favorita Grocery Sales
Forecasting](https://www.kaggle.com/competitions/favorita-grocery-sales-forecasting/overview).

Since the compressed dataset when uncompressed becomes too slow to read, I create
parquet equivalent of all files in
[Kaggle](https://www.kaggle.com/datasets/littlesaplings/grocery-sales-forecasting-parquet/settings?select=holiday_events.parquet)(660MB).
The parquet format allows for fasting file reading time into memory. You would need a Kaggle account to download the files.

To know more about parquet files [databricks has a nice summary](https://www.databricks.com/glossary/what-is-parquet).

> **Note**: Though the loading time is faster, the training dataset needs about 6GB RAM.

## Machine Learning

### Data Cleaning/preprocessing
The training dataset contains data from 2016 to July, 2017. This data was used to predict the future sales in 2017.

### Feature Engineering
Using the preprocess data, we compute new features.

Basic features:

    - Categorical features - item, family
    - Promotion

Statistical features:

    - time windows
        - nearest days:[3, 7, 14]
    - key: store x item, item
    - target: unit_sales
    - method:
        - mean, median, max, min, std
        - difference of mean value between adjacent time windows(only for equal time windows)
### Model training
Since we have a bunch of features and single target variable in `unit_sales`, we can consider this as regression problem.

We use LightGBM as our model algorithm. We set the hyperparameters to a default setting and collect as baseline. Then we tune the parameters as needed till we get the best model.

The feature engineering ideas are heavily borrowed from the [1st place solution](https://www.kaggle.com/code/shixw125/1st-place-lgb-model-public-0-506-private-0-511/script) of the competition.

### Prediction
Since it is a regression problem, independent variables serve as input and the target variable is unit sales. As input we can supply the store number, a date between `2017-08-16` and `2017-08-31`. An item number is randomly chosen. With these three inputs, unit sales is computed.

## How to run
### System Requirements
*To download raw data, preprocess, model* -

Operating System: Ubuntu 20.04 x64 Linux

vCPU: minimum 4 cores(AWS EC2 instance `t2.xlarge` would be sufficient)

RAM: minimum 16GB

Storage: minimum 10GB

1. Install the pre-requisites:

**Miniconda3**:

```bash
cd ~ && git clone https://github.com/dr563105/mlops-project-grocery-sales.git # clone the repo
sudo apt update && sudo apt install make -y
cd mlops-project-grocery-sales
make conda_docker_install # downloads and installs miniconda3, docker, docker-compose
```
Logout and log in back to the instance. Now the `base` conda env would've been activated.
(Optional) Test if docker is working:
```
docker run --rm hello-world # show return hello world without errors
```
> **Note** - You can skip the next steps and directly skip to [deployment](#deployment). Just make sure add in environment variables whereever necessary.

2. Setup virtual environment:

```bash
cd ~/mlops-project-grocery-sales
make pipenv_setup # install Pipenv and other packages in Pipfile.
```

3. Export Kaggle secrets as env variables to download the dataset:

```
export KAGGLE_USERNAME=datadinosaur
export KAGGLE_KEY=xxxxxxxxxxxxxx
```

4. Create input directory and download Kaggle dataset into it:

```bash
cd ~/mlops-project-grocery-sales
make kaggle_dataset_download
```

5. Follow aws-rds [guide](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/02-experiment-tracking/mlflow_on_aws.md) to setup AWS EC2 instance, S3 bucket and AWS RDS for Mlflow tracking server.

> **Note:** Make sure ports 4200, 5000 and 5432 are added to the inbound rules. Security group of RDS must be linked with EC2 server instance to connect the server with the database. Port `4200` is for Prefect, `5000` Mlflow, `5432` PostgresDB.

![Inbound rules configuration!](/assets/images/inbound_rules.jpeg "EC2 instance inbound rules")

6. Run Prefect orion server:

**In terminal 1**

```bash
export EC2_IP="" # replace double quotes with the EC2 IP address
make setup_prefect && make start_prefect
```

7. Run data_processing:

**In terminal 2**

```bash
make run_data_preprocess # runs preprocessing script. Training, validation datasets are created.
```

8. Run MLflow with remote tracking and S3 as artifact store:

**In terminal 3**

Export DB secrets as environment variables. Replace double quotes with values got while setting up RDS into the variables.

```bash
export DB_USER=""
export DB_PASSWORD=""
export DB_ENDPOINT=""
export DB_NAME=""
export S3_BUCKET_NAME=""
export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""
export AWS_DEFAULT_REGION=us-east-1
```

Run MLFlow

```bash
make start_mlflow
```

![MLFlow with remote tracking server, backend and artifact stores!](assets/images/mlflow_scenario_4.png "MLFlow remote tracking server and artifact store")

MLFlow dashboard can be seen at `http://<EC2_PUBLIC_IP_DNS>:5000`

9. Run model training:

**In terminal 2**

```bash
export EC2_IP="" # replace double quotes with the EC2 IP address
export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""
export AWS_DEFAULT_REGION=us-east-1
make run_model_training
```

Copy predictions to both `deployment/webservice-flask` and `deployment/webservice-lambda` directories.
```
make copy_preds
```

# Deployment
As we move to deployment and it takes a separe `Pipfile`, it would be best all the opened terminal windows be closed and new ones opened for this section. If you want just test out deployment, run the above copy command. For [flask-mlflow app](/deployment/webservice-flask-mlflow/), the script automatically handles it.

## Flask:

Basic setup

```bash
cd ~/mlops-project-grocery-sales/deployment/webservice-flask
pipenv install --dev # since this directory has a separate Pipfile
```

Run test_predict.py and test_requests.py:

```bash
pipenv run python test_predict.py # in terminal 1. To test as a normal python module
pipenv run python flask_sales_predictor.py # in terminal 1
pipenv run python test_requests.py # in terminal 2. To test with a request endpoint
```

## Lambda

Test lambda deployment:

```bash
cd ~/mlops-project-grocery-sales/deployment/webservice-lambda
# Exit out of flask venv and create new one for lambda testing
pipenv install --dev
pipenv run python test_lambda.py # in terminal 1. To test with lambda handler before creating AWS Lambda resource
```

## Docker

**Containerise Flask application**:

```bash
cd ~/mlops-project-grocery-sales/deployment/webservice-flask
docker build -t flask-sales-predictor:v1 .
docker run -it --rm -p 9696:9696 flask-sales-predictor:v1 # Terminal 1
python test_requests.py # Terminal 2. No need for pipenv as docker is a container.
```

**Containerise Lambda function**:

To run and test lambda function locally, the AWS emulator allows a proxy to convert http requests to JSON events to pass to the lambda function in the container image. We don't expose any port inside Dockerfile when we build the image. Then expose port `9000` as `8080` while running it. Inside the `test_lambda_fn_docker.py`, we send in the event to this(`localhost:9000/2015-03-31/functions/function/invocations`). More info on this [here](https://docs.aws.amazon.com/lambda/latest/dg/images-test.html)

```bash
cd ~/mlops-project-grocery-sales/deployment/webservice-lambda
docker build -t lambda-sales-predictor:v1 .
docker run \
    -it --rm \
    -p 9000:8080 \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}\
    -e RUN_ID="5651db4644334361b10296c51ba3af3e" \
    -e S3_BUCKET_NAME=mlops-project-sales-forecast-bucket \
    lambda-sales-predictor:v1 # in terminal 1
python test_lambda_fn_docker.py # in terminal 2. No need for pipenv as docker is a container.
```

## Terraform - ECR, Lambda, API Gateway
Terraform keeps track of infrastructure as Github does for source code. We can version infrastructures as needed.

So, for our purpose we can use Terraform to deploy the built docker image into AWS ECR, use it in AWS Lambda, and link an API gateway to trigger the lambda function. All the setup for this is present inside [infrastructure](infrastructure/).

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




```json
{"find": {"date1": "2017-08-26", "store_nbr": 20}}
```

The variable `date1` can be a date between 2017-08-16 and 2017-08-31. Please follow the exact data format to avoid errors.


## Acknowledgements

This final capstone project was created as a part of the [Mlops-zoomcamp course](https://github.com/DataTalksClub/mlops-zoomcamp) from [DataTalks.Club](https://datatalks.club). I'd like to thank the staff for providing high quality learning resource. I appreciate their time, effort and assistance in helping me complete the project. I highly recommend any aspiring data scientists this course.

## Plan/tasks
- ### Data Pre-processing, Feature engineering, Model training, Validation and Prediction
    - :white_check_mark: Choose/collect dataset
    - :white_check_mark: Convert huge raw CSV to parquet file formats
    - :white_check_mark: Use Kaggle to store preprocessed datasets
    - :white_check_mark: Preprocess and feature engineer
        - :white_check_mark: Implement logging
    - :white_check_mark: Prepare dataset for model training
    - :white_check_mark: Implement LGBM model
    - :white_check_mark: Validate and forecast predictions
- ### Prefect 2.0 Orion
    - :white_check_mark: Do basic workflow orchestration with local API server
    - :white_check_mark: Use a cloud(AWS) as API server
    - :white_check_mark: Use local storage to store persisting flow code
- ### MLFlow
    - :white_check_mark: Track experiments local backend(sqlite)
    - :white_check_mark: Track experiments with a cloud(AWS RDS) backend
    - :white_check_mark: Store model artifacts in a cloud storage(S3)
- ### Deployment
    - :white_check_mark: As a Flask application with an endpoint
    - :white_check_mark: As a Lambda function with a handler
    - :white_check_mark: As a docker container to test lambda function locally
    - :white_check_mark: Use AWS ECR repository image as Lambda function source
    - :white_check_mark: Create an AWS Lambda function with ECR image source and test it manually
    - :white_check_mark: Connect API Gateway and lambda function using ECR image
    - :white_check_mark: Deploy model as Streamlit app
- ### Infrastructure as Code(IaC) with Terraform
    - :white_check_mark: Use Terraform to deploy the model to production using AWS ECR, Lambda, S3 and API Gateway
- ### CI/CD with Github actions
    - Continuous Integration
        - :white_check_mark: Unit testing
        <!-- - :o: Integration testing with docker-compose -->
        <!-- - :o: Initialise Terraform and prepare for CD -->
## Future developments
- [ ] Implement model monitoring
<!-- - ### Model Monitoring with Evidently
    - :o: Use Prometheus and Grafana
    - :o: Use MongoDB to store monitoring logs, reports
    - :o: Implement a prediction service
    - :o: Check for model or data drift -->
