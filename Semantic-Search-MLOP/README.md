# MLOPs with AWS

# Work flow that needs to be updated respectively
1. Update config.yaml
2. Update schema.yaml
3. Update params.yaml
4. Update the entity
5. Update the configuration manager in src config
6. Update the components
7. Update the pipeline
8. Update the main.py
9. Update the dvc.yaml


## AWS CI/CD Deployment with Github Action
# 1. Login to AWS Console
# 2. Create IAM user for deployment
1. Build docker image of the source code
2. Push your docker image to ECR
3. Launch your EC2
4. Pull your image from ECR in EC2
5. Launch your docker image in EC2

## Create ECR repo to store docker image
- Save the URI: 315865595366.dkr.ecr.us-east-1.amazonaws.com/"name"

## Create EC2 machine

## Open EC2 and install docker in EC2 Machine
sudo apt-get update -y
sudo apt-get upgrade
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker ubuntu
newgrp docker

## Configure EC2 as self-hosted runner in Github:
setting > actions > runner > new self hosted runner > choose os > run following command one by one

## Setup github secretes
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION= 
AWS_ECR_LOGIN_URI= demo>> 566373416292.dkr.ecr.ap-south-1.amazonaws.com
ECR_REPOSITORY_NAME=

