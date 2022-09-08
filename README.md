# Grocery Sales Forcasting
This repository contains the final capstone project for
[Mlops-zoomcamp course](https://github.com/DataTalksClub/mlops-zoomcamp) from [DataTalks.Club](https://datatalks.club).

## Project Statement
Given sales history and promotional information of stores' items, predict future product sales.
Since this is a MLOPS project, emphasis is given for overall pipeline.

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
I borrow ideas from the [1st place solution](https://www.kaggle.com/code/shixw125/1st-place-lgb-model-public-0-506-private-0-511/script)
in the competition. Unlike their solution, I use a simplified **LGBM** model with lesser
features to save time in training. Therefore the model wouldn't be as accurate as theirs.

## MLOPS pipeline(Planned. In progress.)
1. [Terraform](https://www.terraform.io) as Infrastructure as Code(IaC)
2. [MLFlow](https://www.mlflow.org) for experiment tracking
3. [Docker](https://www.docker.com) for deployment
4. [Prefect 2.0](https://orion-docs.prefect.io) as workflow orchestration tool
5. [AWS S3 bucket](https://aws.amazon.com/s3/) to store workflow artifacts
6. [Evidently](https://evidentlyai.com) and [Grafana](https://grafana.com) for model monitoring
