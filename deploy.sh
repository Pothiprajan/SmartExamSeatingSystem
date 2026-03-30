#!/bin/bash

cd ~/SmartExamSystem

git pull

sudo docker stop seating-app || true
sudo docker rm seating-app || true

sudo docker build -t seating-app .

sudo docker run -d -p 5000:5000 --name seating-app seating-app
