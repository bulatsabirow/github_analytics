#!/usr/bin/env bash
# install required dependencies
sudo apt install jq
sudo apt install zip

# define required environment variables
export SERVICE_ACCOUNT=$(yc iam service-account create \
  --name service-account-for-cf \
  --description 'Github API parsing service account' \
  --format json | jq -r .)
# $FOLDER_ID environment variable can be defined the following way:
# $FOLDER_ID: yc resource-manager folder list
yc resource-manager folder add-access-binding $FOLDER_ID \
  --subject serviceAccount:$SERVICE_ACCOUNT_ID \
  --role editor
# define serverless cloud function
yc serverless function create --name github-api-parser

# packing project into .zip file to obey Yandex Cloud requirements
zip -j github_api_parser.zip scheduled_parser/*
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

yc serverless trigger create timer \
  --name github-api-parser-timer-trigger \
  --cron-expression '0 * ? * * *' \
  --payload '' \
  --invoke-function-name github-api-parser \
  --invoke-function-service-account-id $SERVICE_ACCOUNT_ID \
  --retry-attempts 1 \
  --retry-interval 10s