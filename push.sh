#!/bin/bash

docker build -t microservices-demo-emailservice .
docker tag microservices-demo-emailservice:latest 159616352881.dkr.ecr.eu-west-1.amazonaws.com/microservices-demo-emailservice:latest
docker push 159616352881.dkr.ecr.eu-west-1.amazonaws.com/microservices-demo-emailservice:latest
