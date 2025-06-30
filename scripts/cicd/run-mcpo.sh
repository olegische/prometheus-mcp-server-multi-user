#!/bin/bash

# This script runs the MCPO proxy in a Docker container.
# It sources its configuration for the target server (PORT, TRANSPORT)
# from the project's .env file.

# --- Script-specific constants ---
# The port on the host machine where the MCPO proxy will be exposed.
MCPO_HOST_PORT="8602"
# The specific, fixed version of the MCPO proxy Docker image to use.
MCPO_IMAGE="ghcr.io/olegische/mcpo-fixed-schema:0.0.15"
# The name for the running container, to prevent conflicts.
MCPO_CONTAINER_NAME="mcpo-proxy-runner"

# --- Load configuration from .env file ---
set -a
if [ -f .env ]; then
    source .env
else
    echo "FATAL: .env file not found. This script requires it to get PORT and TRANSPORT for the target server."
    exit 1
fi
set +a

# --- Pre-flight Checks ---
if [ -z "$PORT" ]; then
    echo "FATAL: PORT is not set in your .env file."
    exit 1
fi
if [ -z "$TRANSPORT" ]; then
    echo "FATAL: TRANSPORT is not set in your .env file."
    exit 1
fi
if [ -z "$HTTP_HEADER_X_OPENAI_API_KEY" ]; then
    echo "FATAL: The HTTP_HEADER_X_OPENAI_API_KEY environment variable is not set."
    echo "Please set it to the OpenAI API key you want to use for testing:"
    echo "export HTTP_HEADER_X_OPENAI_API_KEY=\"your_api_key_here\""
    exit 1
fi
if [ -z "$(docker ps -q -f name=^/${PROJECT_NAME}$)" ]; then
    echo "FATAL: The main MCP server container ('${PROJECT_NAME}') is not running."
    echo "Please start it first, for example with: docker-compose -f docker-compose.dev.yml up -d"
    exit 1
fi

echo "--- Starting MCPO Proxy ---"
echo "Proxy will be available at: http://localhost:${MCPO_HOST_PORT}"
echo "Targeting local MCP server at: http://host.docker.internal:${PORT} (Transport: ${TRANSPORT})"
echo "Using API Key: ${HTTP_HEADER_X_OPENAI_API_KEY:0:5}..."
echo "---------------------------"

# --- Execution ---
# First, check if a container with the same name is already running and kill it.
# This makes the script idempotent.
if [ "$(docker ps -q -f name=^/${MCPO_CONTAINER_NAME}$)" ]; then
    echo "Found and stopping existing MCPO proxy container..."
    docker stop "${MCPO_CONTAINER_NAME}"
fi

echo "Starting new MCPO proxy container..."
docker run --rm --name "${MCPO_CONTAINER_NAME}" -p "${MCPO_HOST_PORT}:8000" "${MCPO_IMAGE}" \
    --server-type "${TRANSPORT}" \
    --header "{\"X-OpenAI-API-Key\": \"$HTTP_HEADER_X_OPENAI_API_KEY\"}" \
    -- "http://host.docker.internal:${PORT}"
