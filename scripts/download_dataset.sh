#!/bin/bash

cd ~/mlops-project-grocery-sales && mkdir -p input logs output models predictions
pipenv shell
cd input/
kaggle datasets download littlesaplings/grocery-sales-forecasting-parquet
unzip grocery-sales-forecasting-parquet.zip
rm grocery-sales-forecasting-parquet.zip