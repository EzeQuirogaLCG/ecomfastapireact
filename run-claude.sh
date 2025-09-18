#!/bin/bash

# Script to load environment variables and execute claude code
# Author: Claude Assistant

# Check if credentials file exists
if [ ! -f "credentials-for-claude-code.env" ]; then
    echo "Error: credentials-for-claude-code.env file not found"
    echo "Please create the file with the following variables:"
    echo "OPENAI_API_KEY=your_api_key_here"
    echo "GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here"
    exit 1
fi

# Load environment variables from file
echo "Loading environment variables from credentials-for-claude-code.env..."
set -a  # Automatically export all variables
source credentials-for-claude-code.env
set +a  # Disable automatic export

# Check that required variables are defined
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY is not defined in credentials file"
    exit 1
fi

if [ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
    echo "Error: GITHUB_PERSONAL_ACCESS_TOKEN is not defined in credentials file"
    exit 1
fi

echo "Environment variables loaded successfully:"
echo "OPENAI_API_KEY: ${OPENAI_API_KEY:0:10}..." # Show only first 10 characters for security
echo "GITHUB_PERSONAL_ACCESS_TOKEN: ${GITHUB_PERSONAL_ACCESS_TOKEN:0:10}..." # Show only first 10 characters for security

# Execute claude code
echo "Executing claude code..."
claude code
