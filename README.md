# Grocery Sales Forcasting

This repository contains the final capstone project for
[Mlops-zoomcamp course](https://github.com/DataTalksClub/mlops-zoomcamp) from [DataTalks.Club](https://datatalks.club).

## Project Statement

In Machine Learning Operations(MLOPS) expands the scope beyond just training the model using machine learning. It focuses on making sure trained models work in production. It takes elements from DevOPS and makes certain the production infrastructure is available and reliable.  

Ideally a MLOPS engineer takes the model, makes a production pipeline to facilitate effective functioning of the model. The pipeline approach allows to introduce/replace new/old technologies without major rework or service downtime. This approach also allows to retrain models regularly and importantly reproducibility.

The usual MLOPS stages involve model tracking, workflow orchestration, model deployment, model monitoring along with best software development practices such as CI/CD. 

In this project, we will however go from data sourcing phase till deployment(end-to-end). At the end we will be able to easily deploy and monitor out model's performance.

## Plan/tasks
- [x] Choose/collect dataset
- [x] Convert huge raw CSV to parquet file formats
- [x] Use Kaggle to store preprocessed datasets
- [x] Preprocess and feature engineer
    - [x] Implement logging
- [x] Prepare dataset for model training
- [x] Implement LGBM model
- [x] Validate and forecast predictions
- [ ] Prefect 2.0 Orion
    - [x] Do basic workflow orchestration with local API server
    - [x] Use a cloud(AWS) as API server
    - [x] Use local storage to store persisting flow code
    - [ ] Deploy workflow to production
- [ ] MLFlow 
    - [x] Track experiments local backend(sqlite)
    - [x] Track experiments with a cloud(AWS RDS) backend
    - [x] Store model artifacts in a cloud storage(S3)
    - [ ] Register best model to production stage
- [x] Deployment
    - [x] As a Flask application with an endpoint
    - [x] As a Lambda function with a handler
    - [x] As a docker container to deploy the lambda function
    - [x] Upload the docker container image to AWS ECR repository
        - [ ] Automate build and push process with docker-compose 
    - [x] Create an AWS Lambda function with ECR image source and test it manually
    - [ ] Create a Streamlit UI to test the application 
- [ ] Monitor model's performance using a service such as Evidently
    - [ ] Use Prometheus and Grafana
    - [ ] Use MongoDB to store monitoring logs, reports
    - [ ] Implement a prediction service 
    - [ ] Check for model or data drift
- [ ] Use a tool like Terraform to automate application infrastructure(IaC)
    - [ ] Use Terraform to deploy the model to production using AWS ECR, Lambda, S3 and API Gateway 
- [ ] CI/CD with Github actions
    - [ ] Continuous Integration
        - [x] Unit testing
        - [ ] Integration testing with docker-compose
        - [ ] Initialise Terraform and prepare for CD
    - [ ] Continuous Deployment to deploy the model using Terraform

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
The training dataset contains data from 2016. This data was used to predict the future sales in 2017. However, in our case we will use the same trained model to predict current(2022) sales.

Since in year 2016, the feature `onpromotion` contains lot of null values, we eliminate them and store only data from 2017. 

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
Since it is a regression problem, independent variables serve as input and the target variable is unit sales. As input we can supply the store number, a date between '2022-9-10' and '2022-9-25'. An item number is randomly chosen. With these three inputs, unit sales is computed.

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

## How to run
1. Install the pre-requisites:
### Miniconda3:
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
Logout, restart instance.

2. Setup virtual environment:
```bash
cd ~/mlops-project-grocery-sales 
make pipenv_setup # install Pipenv and other packages in Pipfile. 
```

3. Insert Kaggle credentials to download from my kaggle dataset repo:
```bash
cd ~ && mkdir ~/.kaggle
# Download kaggle.json from your kaggle account and place the file inside this directory
chmod +x kaggle.json
```

4. Create input directory and download Kaggle dataset into it:
```bash
cd ~/mlops-project-grocery-sales
mkdir -p input
cd input/
pipenv shell
kaggle datasets download littlesaplings/grocery-sales-forecasting-parquet
unzip grocery-sales-forecasting-parquet.zip
```

6. Run data_processing:
```bash
cd ~/mlops-project-grocery-sales 
mkdir -p logs # to store logs
mkdir -p output # to store train and valid datasets
# if not inside Pipenv shell, use `pipenv shell`
cd src/
python data_preprocess.py
```

7. Follow aws-rds [guide](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/02-experiment-tracking/mlflow_on_aws.md) to setup AWS EC2 instance and AWS RDS.

8. Run MLflow with remote tracking and S3 as artifact store:
### In terminal 1 
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

9. Run Prefect orion server:

### In terminal 2
```bash
cd ~/mlops-project-grocery-sales/
# if not inside Pipenv shell, use `pipenv shell`
prefect config set PREFECT_API_URL="http://<external-ip>:4200/api" # external ip is from AWS EC2
prefect config view # check if it has changed
prefect orion start --host 0.0.0.0
```

MLFlow dashboard can be found here:
```bash
# In a browser open this link
http://<EC2_PUBLIC_DNS>:5000
```
**Note:** Make sure port 4200 and 5000 are added to inbound rules

10. Run model training:
### In terminal 3
```bash
cd ~/mlops-project-grocery-sales/
mkdir -p models # to store models, if mlflow is run locally
mkdir -p predictions # to store prediction file, if mlflow is run locally
# if not inside Pipenv shell, use `pipenv shell`
cd src
python model_train.py
```

After completion, go inside `predictions` directory locally or in S3 bucket,
download it, copy it to both `deployment/deploy-flask` and `deployment/deploy-lambda` directories. Rename it as `lgb_predictions_wo_family.parquet`
# Deployment
## Flask:
Basic setup
```bash
cd deployment/deploy-flask
pipenv install # since this directory has a separate Pipfile
pipenv shell
```
Run test_predict.py and test_requests.py:
```bash
python flask_sales_predictor.py # in terminal 1
python test_predict.py # in terminal 2. To test as a normal python module
python test_requests.py # in terminal 2. To test with a request endpoint
```
## Lambda
Test lambda deployment:
```bash
cd ../deploy-lambda
python lambda_function.py # in terminal 1
python test_lambda.py # in terminal 2. To test with lambda handler before creating AWS Lambda resource
```
## Docker
To containerise:
```bash
cd ~/mlops-project-grocery-sales/deploy-lambda
docker build -t lambda-sales-predictor:v1 .
```
To run it:
```bash
docker run -it --rm -p 9696:9696 lambda-sales-predictor:v1 # in terminal 1
python test_lambda.py # in terminal 2
```

## Docker, ECR and Lambda
We can upload the created, built docker image into AWS ECR. The guide is covered in ML Zoomcamp [here](https://github.com/alexeygrigorev/aws-lambda-docker/blob/main/guide.md#preparing-the-docker-image). Follow the guide till the end where API gateway is created.

When testing at lambda and API use this JSON dict:
```json
{"find": {"date1": "2022-09-15", "store_nbr": 19}}
```
The variable `date1` can be a date between 2022-09-10 and 2022-09-25.


More updates to follow.s