#!/bin/bash

pipenv run prefect config set PREFECT_API_URL="http://${EC2_IP}:4200/api"