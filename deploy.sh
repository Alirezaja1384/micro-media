#!/usr/bin/env bash
set -e

# Go to project root
DIR=$(dirname $0)

# Delete all containers if running
echo "> Stopping containers ..."
docker compose --project-directory "${DIR}" down

# Build and start containers
echo "> Building and starting containers ..."
docker compose --project-directory "${DIR}" up --build -d

# Follow logs
echo "> Gathering API logs ..."
echo "> Press CTRL+C to exit ..."
sleep 2 && docker compose --project-directory "${DIR}" logs --follow api
