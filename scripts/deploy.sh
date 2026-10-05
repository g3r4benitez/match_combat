#!/bin/bash
set -e

# =============================================================
# Deploy script: Build Docker image, push to ECR, deploy to App Runner
# Prerequisites:
#   - AWS CLI configured (aws config)
#   - Docker running
#   - Terraform applied (infra must exist first)
# =============================================================

PROJECT_NAME="match-combat"
AWS_REGION="${AWS_REGION:-us-east-1}"

echo "=== Building Docker image ==="
docker build -t ${PROJECT_NAME}/api -f Dockerfile .

echo "=== Getting ECR login ==="
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin ${PROJECT_NAME}/api

echo "=== Tagging and pushing to ECR ==="
ECR_URL=$(aws ecr describe-repositories --repository-names ${PROJECT_NAME}/api --query "repositories[0].repositoryUri" --output text --region $AWS_REGION)
docker tag ${PROJECT_NAME}/api:latest ${ECR_URL}:latest
docker push ${ECR_URL}:latest

echo "=== Deploying to App Runner ==="
# App Runner auto-deployments are disabled in Terraform
# We trigger a new deployment by calling StartDeployment
SERVICE_ARN=$(aws apprunner list-services --query "ServiceSummaries[?ServiceName=='${PROJECT_NAME}-service'].ServiceArn" --output text --region $AWS_REGION)

if [ -z "$SERVICE_ARN" ]; then
    echo "WARNING: App Runner service not found. Run 'terraform apply' first."
    exit 1
fi

echo "Triggering deployment on: $SERVICE_ARN"
aws apprunner start-deployment --service-arn "$SERVICE_ARN" --region $AWS_REGION

echo "=== Deployment triggered ==="
echo "Check status at:"
aws apprunner describe-service --service-arn "$SERVICE_ARN" --query "Service.ServiceUrl" --output text --region $AWS_REGION
