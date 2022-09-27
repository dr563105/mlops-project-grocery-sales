#!/bin/bash

cd ~/mlops-project-grocery-sales && mkdir -p input logs output models predictions
cd input/ && pipenv run kaggle datasets download littlesaplings/grocery-sales-forecasting-parquet
unzip grocery-sales-forecasting-parquet.zip
rm grocery-sales-forecasting-parquet.zip