SHELL:=/bin/bash

conda_docker_install:
	source ./scripts/install_conda.sh
	source ./scripts/install_docker.sh

pipenv_setup:
	pip install pipenv
	pipenv install --dev
	pipenv run pre-commit install

kaggle_dataset_download:
	source ./scripts/download_dataset.sh

setup_prefect:
	source ./scripts/setup_prefect.sh

start_prefect:
	pipenv run prefect orion start --host 0.0.0.0

start_mlflow:
	pipenv run mlflow server -h 0.0.0.0 -p 5000 \
	--backend-store-uri=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_ENDPOINT}:${DB_PORT}\
	/${DB_NAME} --default-artifact-root=s3://${S3_BUCKET_NAME}

run_data_preprocess:
	cd ~/mlops-project-grocery-sales/src && pipenv run python data_preprocess.py

run_model_training:
	cd ~/mlops-project-grocery-sales/src && pipenv run python model_train.py

copy_preds:
	cp -i ~/mlops-project-grocery-sales/predictions/lgb_preds.parquet ~/mlops-project-grocery-sales/deployment/webservice-flask/
	cp -i ~/mlops-project-grocery-sales/predictions/lgb_preds.parquet ~/mlops-project-grocery-sales/deployment/webservice-lambda/

quality_checks:
	pipenv run isort .
	pipenv run black .
	pipenv run pylint --recursive=y .

run_tests:
	pipenv run pytest tests/
