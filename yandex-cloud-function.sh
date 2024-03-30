#!/usr/bin/env bash
# install required dependencies
sudo apt install zip

# $FOLDER_ID and $SERVICE_ACCOUNT_ID environment variables can be defined as follows:
# $FOLDER_ID: yc resource-manager folder list
# $SERVICE_ACCOUNT_ID: yc iam service-account list

# assign role 'editor' to created service account
yc resource-manager folder add-access-binding $FOLDER_ID \
  --subject serviceAccount:$SERVICE_ACCOUNT_ID \
  --role editor

# define serverless cloud function
yc serverless function create --name github-api-parser

# packing project into .zip file to follow Yandex Cloud requirements
cd scheduled_parser && zip github_api_parser.zip ./ -r -i '*.py' 'services/*.py' 'requirements.txt'

# create serverless cloud function
yc serverless function version create \
  --function-name github-api-parser \
  --memory 256m \
  --execution-timeout 600s \
  --runtime python312 \
  --entrypoint index.handler \
  --service-account-id $SERVICE_ACCOUNT_ID \
  --source-path github_api_parser.zip \
  --environment GITHUB_TOKEN=$GITHUB_TOKEN \
  --environment DB_USER=$DB_USER \
  --environment DB_PASSWORD=$DB_PASSWORD \
  --environment DB_HOST=$DB_HOST \
  --environment DB_PORT=$DB_PORT \
  --environment DB_NAME=$DB_NAME

# create timer trigger
yc serverless trigger create timer \
  --name github-api-parser-timer-trigger \
  --cron-expression '0 * ? * * *' \
  --payload '' \
  --invoke-function-name github-api-parser \
  --invoke-function-service-account-id $SERVICE_ACCOUNT_ID \
  --retry-attempts 1 \
  --retry-interval 10s