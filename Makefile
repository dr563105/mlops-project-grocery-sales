SHELL:=/bin/bash

prerequisites: ## Perform the initial machine configuration
	@sudo apt update
	@sudo apt install docker.io -y
	@sudo pip install pipenv
	@sudo wget https://github.com/docker/compose/releases/download/v2.5.0/docker-compose-linux-x86_64 -O /usr/bin/docker-compose
	@sudo chmod +x /usr/bin/docker-compose
