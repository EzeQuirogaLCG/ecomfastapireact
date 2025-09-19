#!/bin/bash

echo "🔧 Starting ecomfastapireact devcontainer setup..."

# Detect environment
echo "🔍 Detecting environment..."

# Check if running in WSL2
if grep -qi microsoft /proc/version; then
    echo "🐧 WSL2 environment detected - applying WSL2 optimizations..."
    export WSL2_MODE=true
else
    echo "🐧 Standard Linux environment detected"
    export WSL2_MODE=false
fi

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

# Configure user groups and permissions
echo "🔧 Configuring user groups and permissions..."

# Get the current user and group
CURRENT_USER=$(whoami)
CURRENT_GROUP=$(id -gn)

# Ensure the dev group exists or use current group
if ! getent group dev > /dev/null 2>&1; then
    echo "📝 Creating dev group..."
    sudo groupadd dev
    sudo usermod -a -G dev $CURRENT_USER
fi

# Use the appropriate group
TARGET_GROUP="dev"
if ! groups | grep -q dev; then
    TARGET_GROUP=$CURRENT_GROUP
    echo "⚠️  Using current group: $TARGET_GROUP"
fi

# Install Node.js dependencies for the frontend
echo "📦 Installing Node.js dependencies for frontend..."
cd /workspaces/ecomfastapireact/frontend-1

# Fix permissions for frontend directory
echo "🔧 Fixing permissions for frontend directory..."
sudo chown -R $CURRENT_USER:$TARGET_GROUP /workspaces/ecomfastapireact/frontend-1
sudo chmod -R 755 /workspaces/ecomfastapireact/frontend-1

# Additional WSL2 permission fixes
if [ "$WSL2_MODE" = true ]; then
    echo "⚙️  Applying WSL2 specific configurations..."
    sudo chmod -R 777 /workspaces/ecomfastapireact/frontend-1
    
    # Set npm configuration for WSL2
    npm config set cache /tmp/.npm-cache
    mkdir -p /tmp/.npm-cache
    chmod 777 /tmp/.npm-cache
    
    # Alternative: use a different npm cache location
    export npm_config_cache=/tmp/.npm-cache
fi

# Clear npm cache and install with proper permissions
echo "🧹 Clearing npm cache..."
npm cache clean --force

# Configure npm for WSL2 compatibility (only in WSL2)
if [ "$WSL2_MODE" = true ]; then
    echo "⚙️  Configuring npm for WSL2..."
    npm config set unsafe-perm true
    npm config set no-bin-links true
    npm config set prefer-offline true
fi

# Install with environment-optimized flags
if [ "$WSL2_MODE" = true ]; then
    echo "📦 Installing dependencies with WSL2-optimized settings..."
    if ! npm install --unsafe-perm --no-optional --no-bin-links --prefer-offline; then
        INSTALL_FAILED=true
    fi
else
    echo "📦 Installing dependencies with standard settings..."
    if ! npm install --no-optional; then
        INSTALL_FAILED=true
    fi
fi

if [ "$INSTALL_FAILED" = true ]; then
    echo "⚠️  First install attempt failed, trying alternative approach..."
    
    # Remove node_modules if it exists and try again
    rm -rf node_modules package-lock.json
    
    # Fix permissions again before retry
    sudo chown -R $CURRENT_USER:$TARGET_GROUP /workspaces/ecomfastapireact/frontend-1
    if [ "$WSL2_MODE" = true ]; then
        sudo chmod -R 777 /workspaces/ecomfastapireact/frontend-1
    fi
    
    # Try with yarn instead of npm
    if command -v yarn &> /dev/null; then
        echo "📦 Trying with yarn..."
        if [ "$WSL2_MODE" = true ]; then
            yarn install --frozen-lockfile --no-bin-links
        else
            yarn install --frozen-lockfile
        fi
    else
        # Fallback to npm with different flags
        echo "📦 Trying npm with different flags..."
        if [ "$WSL2_MODE" = true ]; then
            npm install --no-bin-links --unsafe-perm --prefer-offline
        else
            npm install --unsafe-perm
        fi
    fi
fi

# Final permission fix
echo "🔧 Final permission adjustment..."
sudo chown -R $CURRENT_USER:$TARGET_GROUP /workspaces/ecomfastapireact/frontend-1

echo "🚀 ecomfastapireact devcontainer is ready for development!"
