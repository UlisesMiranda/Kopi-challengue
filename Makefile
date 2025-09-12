SHELL := /bin/bash

IMAGE_NAME := kopi-chatbot

.PHONY: help install test run down clean

.DEFAULT_GOAL := help

help: ## Display this help message.
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# This target checks for docker-compose, then builds the 'chatbot-api' service image
# using docker-compose and a separate test image from Dockerfile.test.
install: ## Builds the production and test Docker images.
	@command -v docker-compose >/dev/null 2>&1 || { \
		echo -e "\033[31mError: The 'docker-compose' command was not found.\033[0m"; \
		echo "Please install it to continue."; \
		exit 1; \
	}
	@echo "Building production image with Docker Compose..."
	@docker-compose build chatbot-api
	@echo "Building test image..."
	@docker build -t $(IMAGE_NAME):test -f Dockerfile.test .
	@echo "Installation completed."

# This target executes the tests using the previously built test image.
test: ## Runs the tests inside a Docker container.
	@echo "Running tests..."
	@docker run --rm $(IMAGE_NAME):test

# run: ## Starts the services defined in docker-compose.yml.
# This target builds (if necessary) and starts the Docker containers in detached mode.
run: ## Starts the services defined in docker-compose.yml.
	@echo "Starting services with Docker Compose..."
	@echo "Press Ctrl+C to stop."
	@docker-compose up --build

# This target stops the running Docker containers.
down: ## Stops and removes the Docker containers.
	@echo "Stopping the containers..."
	@docker-compose down

# This target stops all services and removes containers and associated volumes.
clean: ## Stops and removes Docker containers and volumes.
	@echo "Stopping and deleting containers and volumes..."
	@docker-compose down --volumes
	@echo "Cleaning completed."