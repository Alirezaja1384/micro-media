#!/usr/bin/env bash
set -e

# Go to project root
DIR=$(dirname $0)

# Delete all containers if running
echo "> Stopping containers ..."
docker compose --file "${DIR}/docker-compose.yml" down

# Build and start containers
echo "> Building and starting containers ..."
docker compose --file "${DIR}/docker-compose.yml" up --build -d

# Follow logs
echo "> Gathering API logs ..."
echo "> Press CTRL+C to exit ..."
sleep 2 && docker compose --file "${DIR}/docker-compose.yml" logs --follow api