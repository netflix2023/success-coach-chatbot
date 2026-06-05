#!/bin/bash
# -------------------------------------------------------------------
# Aider & OpenRouter Startup Wrapper
# -------------------------------------------------------------------
# This script sets up the environment variables and runs Aider using
# OpenRouter. It will persist your OpenRouter API Key in a local .env
# file so you don't have to enter it multiple times.

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${WORKSPACE_DIR}/.env"
PARENT_ENV_FILE="$(dirname "${WORKSPACE_DIR}")/.env"

# 1. Load keys from parent .env or local .env
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment variables from local .env..."
    export $(grep -v '^#' "$ENV_FILE" | xargs)
elif [ -f "$PARENT_ENV_FILE" ]; then
    echo "Loading environment variables from parent .env..."
    export $(grep -v '^#' "$PARENT_ENV_FILE" | xargs)
fi

# 2. Check if OPENROUTER_API_KEY is set
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "==================================================================="
    echo "⚠️  OPENROUTER_API_KEY not found in environment or .env"
    echo "==================================================================="
    echo "Please paste your OpenRouter API Key (it will be saved to .env):"
    read -r user_key
    if [ -n "$user_key" ]; then
        echo "OPENROUTER_API_KEY=${user_key}" >> "$ENV_FILE"
        export OPENROUTER_API_KEY="${user_key}"
        echo "Saved key to ${ENV_FILE}"
    else
        echo "Error: API Key is required to run Aider with OpenRouter."
        exit 1
    fi
fi

# 3. Activate Python Virtual Environment
if [ -f "/venv/bin/activate" ]; then
    source /venv/bin/activate
fi

# 4. Launch Aider
echo "Starting Aider with OpenRouter (Model: Google Gemini 2.5 Flash)..."
aider "$@"
