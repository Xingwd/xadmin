#! /usr/bin/env sh

# Exit in case of error
set -e
set -x

docker compose build
docker compose down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error
docker compose up -d
docker compose exec -T backend bash scripts/tests-start.sh "$@"
CI=1 docker compose run --rm playwright bun run test
docker compose down -v --remove-orphans
