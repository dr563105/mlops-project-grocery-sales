SHELL:=/bin/bash

docker_install: ## Perform the initial machine configuration
	@sudo apt update && sudo apt install docker.io -y
	@sudo wget https://github.com/docker/compose/releases/download/v2.5.0/docker-compose-linux-x86_64 -O /usr/bin/docker-compose
	@sudo chmod +x /usr/bin/docker-compose

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
