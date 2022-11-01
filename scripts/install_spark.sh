#!/bin/bash

cd ~
wget -q https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz
tar xzf openjdk-11.0.2_linux-x64_bin.tar.gz
wget -q https://dlcdn.apache.org/spark/spark-3.3.1/spark-3.3.1-bin-hadoop3.tgz
tar xzf spark-3.3.1-bin-hadoop3.tgz
rm spark-3.3.1-bin-hadoop3.tgz openjdk-11.0.2_linux-x64_bin.tar.gz
