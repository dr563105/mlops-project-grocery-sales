#!/bin/bash

cd ~
sudo apt install docker.io -y
mkdir soft && cd soft 
wget https://github.com/docker/compose/releases/download/v2.5.0/docker-compose-linux-x86_64 -O docker-compose
chmod +x docker-compose
export PATH="/home/ubuntu/soft:$PATH"
sudo groupadd docker
sudo usermod -aG docker $USER
