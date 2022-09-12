# Grocery Sales Forcasting

This repository contains the final capstone project for
[Mlops-zoomcamp course](https://github.com/DataTalksClub/mlops-zoomcamp) from [DataTalks.Club](https://datatalks.club).

## Project Statement

Predict unit sales given store number, item number and date.

In Machine Learning Operations(MLOPS) expands the scope beyond just training the model using machine learning. It focuses on making sure trained models work in production. With time both models and data drift from optimal performance. At the time based on the problem, models have to be retrained or business ideas rethought. In MLOPS the emphasis is on the avalibility and reliability of the services.

In order to achieve that a MLOPS engineer has to take the model, make a pipeline to facilitate smooth flow of data end-to-end using the model.
The pipeline approach allows to introduce/replace technologies without major rework or service downtime. This approach also allows to retrain models regularly and importantly reproducibility.

The objective of this project is to use aspects of MLOPS such as experiment tracking, workflow orchestration and model deployment and build a robust pipeline while following best practices of code engineering.

## Dataset

The data comes from Kaggle competition - [Corporación Favorita Grocery Sales
Forecasting](https://www.kaggle.com/competitions/favorita-grocery-sales-forecasting/overview).

Since the compressed dataset when uncompressed becomes too slow to read, I have created
parquet equivalent of all files in
[Kaggle](https://www.kaggle.com/datasets/littlesaplings/grocery-sales-forecasting-parquet/settings?select=holiday_events.parquet)(660MB).
The parquet format allows for fasting file reading time into memory. You would need a Kaggle account to download the files.

To know more about parquet files [databricks has a nice summary](https://www.databricks.com/glossary/what-is-parquet).

**Note**: Though the loading time is faster, the training dataset needs about 6GB RAM.

## Machine Learning Model

Though sale prediction is often a time-series problem, we treat as a regression problem. We create features as often seen in time-series problems. Then use them to compute the unit sales for a future range.

I heavily borrow ideas from the [1st place solution](https://www.kaggle.com/code/shixw125/1st-place-lgb-model-public-0-506-private-0-511/script)

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
1. Clone the repo locally:
```
$ git clone https://github.com/dr563105/mlops-project-grocery-sales.git
```
2. Instal the pre-requisites:
```
$ cd maternal-health-risk
$ sudo apt install make
$ make prerequisites
```
3. To avoid using `sudo` for docker:
```
$ sudo groupadd docker
$ sudo usermod -aG docker $USER
```
Logout, restart instance.
4. Insert Kaggle credentials in .env file to download from my kaggle dataset repo:
```
# Kaggle credentials
KAGGLE_USERNAME=*****
KAGGLE_KEY=*****
```
5. Create input directory and download Kaggle dataset into it:
```
mkdir -p input
cd input/
pipenv install --dev kaggle
kaggle datasets download littlesaplings/grocery-sales-forecasting-parquet
unzip grocery-sales-forecasting-parquet.zip
```
6. Run data_processing:
```
cd src/
python data_process.py
```
7. Follow aws-rds [guide](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/02-experiment-tracking/mlflow_on_aws.md) to setup AWS EC2 instance, AWS RDS
8. Run MLflow remote tracking and S3 artifact store:
```
mlflow server -h 0.0.0.0 -p 5000 --backend-store-uri postgresql://DB_USER:DB_PASSWORD@DB_ENDPOINT:5432/DB_NAME --default-artifact-root s3://S3_BUCKET_NAME
```
Info about variables are described in that guide.
9. Run Prefect orion server:
```
prefect config set PREFECT_API_URL="http://<external-ip>:4200/api" # external ip is from AWS EC2
prefect config view #check if it has changed
prefect orion start --host 0.0.0.0
```
MLFlow dashboard can be found here:
```
http://<EC2_PUBLIC_DNS>:5000
```
Note: Make sure port 4200 and 5000 are added in inbound rules

10. Run model training:
```
cd src
python model_train.py
```
# Deployment
## Flask:
Basic setup
```
cd deployment/deploy-flask
pipenv install
pipenv shell
```
Run test_predict.py and test_requests.py:
```
python flask_sales_predictor.py # in one tab
python test_predict.py # in another tab
python test_predict.py # in another tab
```
## Lambda
Test lambda deployment:
```
cd ../deploy_lambda
python lambda_function.py # in one tab
python test_lambda.py # in another tab
```
## Docker
To containerise
```
docker build -t lambda-sales-predictor:v1 .
```
To run it
```
docker run -it --rm -p 9696:9696 lambda-sales-predictor:v1
```
In another tab
```
python test_lambda.py
```

## Docker, ECR and Lambda
We can upload the created, built docker image into AWS ECR. The guide is covered in ML Zoomcamp[here](https://github.com/alexeygrigorev/aws-lambda-docker/blob/main/guide.md#preparing-the-docker-image). Follow the guide till the end where API gateway created.

When testing at lambda and API use this JSON dict:
```
{"find": {"date1": "2022-09-15", "store_nbr": 19}}
```
The variable date1 can be a date between 2022-09-10 and 2022-09-25.

If you questions, please don't hesitate to contact me. If email is in github profile. Thanks for evaluating.
