#!/bin/bash
# Docker wrapper script for Zep MCP Server (Unix/macOS/Linux)

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load environment variables if .env exists
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again." >&2
    exit 1
fi

# Check if required environment variables are set
if [ -z "$ZEP_API_KEY" ] || [ "$ZEP_API_KEY" = "your_zep_api_key_here" ]; then
    echo "Error: ZEP_API_KEY not set. Please copy env.example to .env and set your API key." >&2
    exit 1
fi

# Build the image if it doesn't exist
IMAGE_NAME="zep-mcp-server"
if ! docker image inspect $IMAGE_NAME >/dev/null 2>&1; then
    echo "Building Docker image..."
    docker build -t $IMAGE_NAME "$PROJECT_DIR"
fi

# Run the container with stdio transport
docker run --rm -i \
    -e ZEP_API_KEY="$ZEP_API_KEY" \
    -e ZEP_USER_IDS="${ZEP_USER_IDS:-aaron_whaley,tech_knowledge_base}" \
    -e ZEP_DEFAULT_USER_ID="${ZEP_DEFAULT_USER_ID:-aaron_whaley}" \
    -e TRANSPORT=stdio \
    $IMAGE_NAME python run_stdio.py 