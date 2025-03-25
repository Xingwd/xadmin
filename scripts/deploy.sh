#! /usr/bin/env sh

# Exit in case of error
set -e

DOMAIN=${DOMAIN?Variable not set} \
STACK_NAME=${STACK_NAME?Variable not set} \
TAG=${TAG?Variable not set} \
docker compose \
-f docker-compose.yml \
config > docker-compose-deploy.yml

docker compose -f docker-compose-deploy.yml -p ${STACK_NAME?Variable not set} up -d --no-build
