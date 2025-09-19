#!/bin/bash

echo "🧹 Starting DevContainer cleanup process..."

# Function to kill processes using specific ports
kill_port_processes() {
    echo "🔫 Killing processes using devcontainer ports..."
    
    # List of ports to check
    local ports=(3000 8000 5432 5050 7474 7687)
    
    for port in "${ports[@]}"; do
        echo "   Checking port $port..."
        
        # Find PIDs using the port
        local pids=$(ss -tulpn | grep ":$port " | awk '{print $6}' | cut -d',' -f2 | cut -d'=' -f2 | sort -u)
        
        if [ ! -z "$pids" ]; then
            for pid in $pids; do
                if [ ! -z "$pid" ] && [ "$pid" != "0" ]; then
                    echo "   Killing process $pid on port $port"
                    kill -9 "$pid" 2>/dev/null || echo "   Could not kill process $pid"
                fi
            done
        fi
    done
}

# Function to check if ports are in use
check_ports() {
    echo "🔍 Checking for occupied ports..."
    local ports_in_use=$(ss -tulpn | grep -E ':(3000|8000|5432|5050|7474|7687)' | wc -l)
    if [ $ports_in_use -gt 0 ]; then
        echo "⚠️  Found $ports_in_use occupied ports"
        return 1
    else
        echo "✅ All ports are free"
        return 0
    fi
}

# Function to show current containers
show_containers() {
    echo "📋 Current containers:"
    docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "No containers found"
    echo ""
}

# Step 1: Show current state
echo "📊 Current state:"
show_containers

# Step 2: Stop and remove devcontainer compose
echo "🛑 Stopping devcontainer compose..."
docker compose -f .devcontainer/docker-compose.yml down 2>/dev/null || echo "No devcontainer compose running"

# Step 3: Stop and remove main compose
echo "🛑 Stopping main compose..."
docker compose down 2>/dev/null || echo "No main compose running"

# Step 4: Force remove all containers
echo "🗑️  Force removing all containers..."
docker ps -aq | xargs docker rm -f 2>/dev/null || echo "No containers to remove"

# Step 5: Kill processes using devcontainer ports
kill_port_processes

# Step 6: Clean up volumes (optional)
echo "🧹 Cleaning up unused volumes..."
docker volume prune -f 2>/dev/null || echo "No volumes to clean"

# Step 7: Clean up networks (optional)
echo "🌐 Cleaning up unused networks..."
docker network prune -f 2>/dev/null || echo "No networks to clean"

# Step 8: Clean up images (optional)
echo "🖼️  Cleaning up unused images..."
docker image prune -f 2>/dev/null || echo "No images to clean"

# Step 9: Verify ports are free
echo "🔍 Verifying ports are free..."
if check_ports; then
    echo "✅ All cleanup completed successfully!"
    echo ""
    echo "🚀 You can now try the devcontainer:"
    echo "   1. Close Cursor completely"
    echo "   2. Open a new WSL terminal"
    echo "   3. Run: cursor ."
    echo "   4. Select 'Reopen in Container'"
else
    echo "⚠️  Some ports are still in use. You may need to:"
    echo "   - Check for other Docker processes: docker ps -a"
    echo "   - Check for system services using those ports"
    echo "   - Restart Docker if necessary"
fi

echo ""
echo "📊 Final state:"
show_containers
