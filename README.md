# Grocery Sales Forcasting

This repository contains the final capstone project for
[Mlops-zoomcamp course](https://github.com/DataTalksClub/mlops-zoomcamp) from [DataTalks.Club](https://datatalks.club). This is an end-to-end ML project which takes raw data as the first stage and delivers the model into production as the last stage with a lot of infrastructure interaction inbetween.

## Project Statement

The sale department of a grocery chain wants to build a unit sales prediction engine(a web service application). The engine will use past sales data from all its stores to forecast future item unit sales. The engine will provide the sales department necessary time to stock up on exhausting items or stock less on diminishing items. The grocery chain would then be able to allocate more/less resources to certain stores.

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
    - :o: Deploy workflow to production
- ### MLFlow
    - :white_check_mark: Track experiments local backend(sqlite)
    - :white_check_mark: Track experiments with a cloud(AWS RDS) backend
    - :white_check_mark: Store model artifacts in a cloud storage(S3)
    - :o: Register best model to production stage
- ### Deployment
    - :white_check_mark: As a Flask application with an endpoint
    - :white_check_mark: As a Lambda function with a handler
    - :white_check_mark: As a docker container to test lambda function locally
    - :white_check_mark: Use AWS ECR repository image as Lambda function source
        - :o: Automate build and push process with docker-compose
    - :white_check_mark: Create an AWS Lambda function with ECR image source and test it manually
    - :o: Create a Streamlit UI to test the application
- ### Model Monitoring with Evidently
    - :o: Use Prometheus and Grafana
    - :o: Use MongoDB to store monitoring logs, reports
    - :o: Implement a prediction service
    - :o: Check for model or data drift
- ### Infrastructure as Code(IaC) with Terraform
    - :o: Use Terraform to deploy the model to production using AWS ECR, Lambda, S3 and API Gateway
- ### CI/CD with Github actions
    - Continuous Integration
        - :white_check_mark: Unit testing
        - :o: Integration testing with docker-compose
        - :o: Initialise Terraform and prepare for CD
    - Continuous Deployment
        - :o: Automate deployment upon Git pull or push request

## MLOPS pipeline

1. [MLFlow](https://www.mlflow.org) for experiment tracking
2. [Prefect 2.0](https://orion-docs.prefect.io) as workflow orchestration tool
3. [AWS S3 bucket](https://aws.amazon.com/s3/) to store workflow artifacts
4. [Docker](https://www.docker.com) for deployment in a container locally
5. [AWS ECR](https://aws.amazon.com/ecr/) to store the built docker container
6. [AWS Lambda](https://aws.amazon.com/lambda/) to build a serverless deployment solution
7. Coding best practices include code linting, formatting, pre-commit checking
8. A makefile to help run multiple line command in one command
9. Unit testing especially while deploying models

## Dataset

The data comes from Kaggle competition - [Corporación Favorita Grocery Sales
Forecasting](https://www.kaggle.com/competitions/favorita-grocery-sales-forecasting/overview).

Since the compressed dataset when uncompressed becomes too slow to read, I have created
parquet equivalent of all files in
[Kaggle](https://www.kaggle.com/datasets/littlesaplings/grocery-sales-forecasting-parquet/settings?select=holiday_events.parquet)(660MB).
The parquet format allows for fasting file reading time into memory. You would need a Kaggle account to download the files.

To know more about parquet files [databricks has a nice summary](https://www.databricks.com/glossary/what-is-parquet).

**Note**: Though the loading time is faster, the training dataset needs about 6GB RAM.

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
Since it is a regression problem, independent variables serve as input and the target variable is unit sales. As input we can supply the store number, a date between '2017-08-16' and '2017-08-31'. An item number is randomly chosen. With these three inputs, unit sales is computed.

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
cd ~
sudo apt update && sudo apt install git wget make unzip -y
wget -q https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh
bash ~/Miniconda3-py39_4.12.0-Linux-x86_64.sh -b # installs python 3.9
~/miniconda3/bin/conda init $SHELL_NAME # initialises conda to bashrc
rm Miniconda3-py39_4.12.0-Linux-x86_64.sh # removes the download file
```
Logout of the shell and login to activate conda `base` env.

```bash
cd ~
git clone https://github.com/dr563105/mlops-project-grocery-sales.git # clone the repo
cd mlops-project-grocery-sales
make docker_install # install docker, docker-compose
```

To avoid using `sudo` for docker:

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
```
Logout and log in back to the instance.

2. Setup virtual environment:

```bash
cd ~/mlops-project-grocery-sales
make pipenv_setup # install Pipenv and other packages in Pipfile.
```

3. Insert Kaggle credentials to download from my kaggle dataset repo:

```bash
cd ~ && mkdir ~/.kaggle
# Download kaggle.json from your kaggle account and place the file inside this directory
cd ~/.kaggle
chmod 400 kaggle.json
```

Or export Kaggle secrets as env variable like so
```
export KAGGLE_USERNAME=datadinosaur
export KAGGLE_KEY=xxxxxxxxxxxxxx
```

4. Create input directory and download Kaggle dataset into it:

```bash
cd ~/mlops-project-grocery-sales && mkdir -p input logs output models predictions
pipenv shell
cd input/
kaggle datasets download littlesaplings/grocery-sales-forecasting-parquet
unzip grocery-sales-forecasting-parquet.zip
(optional) rm grocery-sales-forecasting-parquet.zip
```

5. Follow aws-rds [guide](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/02-experiment-tracking/mlflow_on_aws.md) to setup AWS EC2 instance, S3 bucket and AWS RDS for Mlflow tracking server.

**Note:** Make sure ports 4200, 5000 and 5432 are added to the inbound rules. Security group of RDS must be linked with EC2 server instance to connect the server with the database. Port `4200` is for Prefect, `5000` Mlflow, `5432` PostgresDB.

![Inbound rules configuration!](/assets/images/inbound_rules.jpeg "EC2 instance inbound rules")

6. Run Prefect orion server:

**In terminal 1**

```bash
cd ~/mlops-project-grocery-sales/
# if not inside Pipenv shell, use `pipenv shell`
prefect config set PREFECT_API_URL="http://<EC2_PUBLIC_IP>:4200/api" # EC2_PUBLIC_IP is from AWS EC2
prefect config view # check if it has changed
prefect orion start --host 0.0.0.0
```

MLFlow dashboard can be found here:

```bash
# In a browser open this link
http://<EC2_PUBLIC_IP_DNS>:5000 # EC2_PUBLIC_IP_DNS is from AWS EC2
```

7. Run data_processing:

**In terminal 2**

```bash
cd ~/mlops-project-grocery-sales
# if not inside Pipenv shell, use `pipenv shell`
cd src/
python data_preprocess.py
```

8. Run MLflow with remote tracking and S3 as artifact store:

**In terminal 3**

```bash
cd ~/mlops-project-grocery-sales/
# if not inside Pipenv shell, use `pipenv shell`
```

Export DB secrets as environment variables.

```bash
export DB_USER=""
export DB_PASSWORD=""
export DB_ENDPOINT="... .rds.amazonaws.com"
export DB_NAME=""
export S3_BUCKET_NAME=""
```

Run MLFlow

```bash
mlflow server -h 0.0.0.0 -p 5000 \
    --backend-store-uri=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_ENDPOINT}:5432/${DB_NAME} \
    --default-artifact-root=s3://${S3_BUCKET_NAME}
```

![MLFlow with remote tracking server, backend and artifact stores!](assets/images/mlflow_scenario_4.png "MLFlow remote tracking server and artifact store")


9. Run model training:

**In terminal 2**

```bash
cd ~/mlops-project-grocery-sales/
# if not inside Pipenv shell, use `pipenv shell`
cd src
python model_train.py
```

After completion, go inside `predictions` directory locally or in S3 bucket,
download it, copy it to both `deployment/deploy-flask` and `deployment/deploy-lambda` directories. Rename it as `lgb_preds.parquet`

# Deployment
As we move to deployment and it takes a separe `Pipfile`, it would be best all the opened terminal windows be closed and new ones opened for this section.

## Flask:

Basic setup

```bash
cd ~/mlops-project-grocery-sales/deployment/deploy-flask
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
cd ~/mlops-project-grocery-sales/deploy-lambda
# Exit out of flask venv and create new one for lambda testing
pipenv install --dev
pipenv run python test_lambda.py # in terminal 1. To test with lambda handler before creating AWS Lambda resource
```

## Docker

**Containerise Flask application**:

```bash
cd ~/mlops-project-grocery-sales/deploy-flask
docker build -t flask-sales-predictor:v1 .
docker run -it --rm -p 9696:9696 flask-sales-predictor:v1 # Terminal 1
python test_requests.py # Terminal 2. No need for pipenv as docker is a container.
```

**Containerise Lambda function**:

To run and test lambda function locally, the AWS emulator allows a proxy to convert http requests to JSON events to pass to the lambda function in the container image. We don't expose any port inside Dockerfile when we build the image. Then expose port `9000` as `8080` while running it. Inside the `test_lambda_fn.py`, we send in the event to this(`localhost:9000/2015-03-31/functions/function/invocations`). More info on this [here](https://docs.aws.amazon.com/lambda/latest/dg/images-test.html)

```bash
cd ~/mlops-project-grocery-sales/deploy-lambda
docker build -t lambda-sales-predictor:v1 .
docker run -it --rm -p 9000:8080 lambda-sales-predictor:v1 # in terminal 1
python test_lambda_fn_docker.py # in terminal 2. No need for pipenv as docker is a container.
```

## Docker, ECR and Lambda
We can upload the created, built docker image into AWS ECR, use it in AWS Lambda, and link an API gateway to trigger the lambda function.

A comprehensive guide is covered [here](https://github.com/alexeygrigorev/aws-lambda-docker/blob/main/guide.md#preparing-the-docker-image) in ML Zoomcamp.

Further instructions to follow. In the mean time if you know how to configure, go ahead test the pipeline with the following JSON dict

```json
{"find": {"date1": "2017-08-26", "store_nbr": 19}}
```
The variable `date1` can be a date between 2017-08-16 and 2017-08-31. Please follow the exact data format to avoid errors.

More updates to follow.
