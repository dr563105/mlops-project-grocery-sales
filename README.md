# Grocery Sales Forcasting

This repository contains the final capstone project for
[Mlops-zoomcamp course](https://github.com/DataTalksClub/mlops-zoomcamp) from [DataTalks.Club](https://datatalks.club).

## Project Statement

Predict unit sales given store number, item number and date. 

In Machine Learning Operations(MLOPS) expands the scope beyond just training the model using machine learning. It focuses on making sure trained models work in production. With time both models and data drift from optimal performance. At the time based on the problem, models have to be retrained or business ideas rethought. In MLOPS the emphasis is on the avalibility and reliability of the services.

In order to achieve that a MLOPS engineer has

we target to connect each component in the pipeline to facilitate smooth flow of data end-to-end.
The pipeline approach allows to introduce/replace technologies without major rework or service downtime. This approach also allows to retrain models regularly and importantly reproducibility.

In this project some of the important aspects of MLOPS are covered -- experiment tracking, workflow orchestration, model deployment and monitoring. Also the best practices of code engineering is followed.

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

In an advanced model, family of items from a list is also given as input to compute unit sales.

## MLOPS pipeline(Planned. In progress.)

1. [Terraform](https://www.terraform.io) as Infrastructure as Code(IaC)
2. [MLFlow](https://www.mlflow.org) for experiment tracking
3. [Docker](https://www.docker.com) for deployment
4. [Prefect 2.0](https://orion-docs.prefect.io) as workflow orchestration tool
5. [AWS S3 bucket](https://aws.amazon.com/s3/) to store workflow artifacts
6. [Evidently](https://evidentlyai.com) and [Grafana](https://grafana.com) for model monitoring
