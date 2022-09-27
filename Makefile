SHELL:=/bin/bash

conda_install:
	source ./scripts/install_conda.sh

docker_install: ## Perform the initial machine configuration
	source ./scripts/install_docker.sh

kaggle_dataset_download:
	source ./scripts/download_dataset.sh

run_data_process:
	cd ~/mlops-project-grocery-sales/src && python data_process.py

run_model_training:
	cd ~/mlops-project-grocery-sales/src && python model_train.py

terraform_install:
	wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
	echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
	sudo apt update && sudo apt install terraform

quality_checks:
	pipenv run isort .
	pipenv run black .
	pipenv run pylint --recursive=y .

run_tests:
	pipenv run pytest tests/

pipenv_setup:
	pip install pipenv
	pipenv install --dev
	pipenv run pre-commit install
