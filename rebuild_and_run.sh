#!/bin/bash

# Bring down already running service
docker-compose down 
# Build the Docker image with no-cache
docker-compose build --no-cache

# Run the Docker Compose services
docker-compose up -d
