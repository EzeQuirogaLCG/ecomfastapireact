#!/bin/bash

echo "🔧 Starting ecomfastapireact devcontainer setup..."

# Update package lists
sudo apt-get update

# Install uv (which provides uvx) for MCP server management
echo "📦 Installing uv (provides uvx) for MCP servers..."
python3 -m pip install --user uv

# Ensure uv/uvx is in PATH for current session
export PATH="$HOME/.local/bin:$PATH"

# Install Claude Code CLI
echo "🤖 Installing Claude Code CLI..."
npm install -g @anthropic-ai/claude-code

# Install MCP server packages using uv tool install
echo "🤖 Installing MCP servers..."

# Create shared MCP servers directory and setup Graphiti
echo "🧠 Setting up Graphiti MCP server in shared directory..."
sudo mkdir -p /mcp-servers
sudo chown dev /mcp-servers
git clone https://github.com/getzep/graphiti.git /mcp-servers/graphiti
cd /mcp-servers/graphiti && uv sync || echo "⚠️  Graphiti setup failed"

# Install Playwright browsers
echo "🎭 Installing Playwright browsers..."
npx --yes playwright install chromium firefox webkit
npx --yes playwright install-deps

# Install validation tools
echo "📊 Installing validation tools..."

# Database validation tools
pip install great_expectations sqlfluff pytest-django

# Install pgloader for PostgreSQL migration validation
sudo apt-get install -y pgloader

# Install Hadolint for Dockerfile linting
echo "🐳 Installing Hadolint..."
sudo wget -O /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64
sudo chmod +x /usr/local/bin/hadolint

# Install docker-bench-security
echo "🔒 Installing docker-bench-security..."
sudo git clone https://github.com/docker/docker-bench-security.git /opt/docker-bench-security
sudo chmod +x /opt/docker-bench-security/docker-bench-security.sh

# Add workspace alias to bashrc
echo "📁 Adding workspace alias..."
echo 'alias workspace="cd /workspaces/ecomfastapireact"' >> ~/.bashrc

# Install Jira Ticket Management CLI (jira-cli) - Python version
echo "🎫 Installing Jira Ticket Management CLI (jira-cli)..."

# Create a temporary copy to avoid WSL permission issues
cp -r /workspaces/ecomfastapireact/jira-cli /tmp/jira-cli-temp
cd /tmp/jira-cli-temp
python3 -m pip install .

# Clean up temporary copy
rm -rf /tmp/jira-cli-temp
echo "🎫 jira-cli tool installed and available globally"

# Install Python dependencies for the backend
echo "🐍 Installing Python dependencies for backend..."
cd /workspaces/ecomfastapireact/backend
pip install -r requirements.txt

# Install Node.js dependencies for the frontend
echo "📦 Installing Node.js dependencies for frontend..."
cd /workspaces/ecomfastapireact/frontend-1
npm install

echo "🚀 ecomfastapireact devcontainer is ready for development!"
