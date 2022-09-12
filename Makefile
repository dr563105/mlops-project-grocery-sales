SHELL:=/bin/bash

prerequisites: ## Perform the initial machine configuration
	@sudo apt update
	@sudo apt install docker.io unzip make -y
	@sudo wget https://github.com/docker/compose/releases/download/v2.5.0/docker-compose-linux-x86_64 -O /usr/bin/docker-compose
	@sudo chmod +x /usr/bin/docker-compose

quality_checks:
	pipenv run isort .
	pipenv run black .
	pipenv run pylint --recursive=y .

run_tests:
	pipenv run pytest tests/

setup:
	pip install pipenv
	pipenv install --dev
	pipenv run pre-commit install
	pipenv shell
