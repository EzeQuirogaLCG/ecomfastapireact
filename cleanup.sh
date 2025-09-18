#!/bin/bash

# Script to clean frontend and backend containers and images
# Only for this specific project
# Usage: ./cleanup.sh [f|b|fb]
# f: stop and delete frontend container and image
# b: stop and delete backend container and image  
# fb: stop and delete both containers and images

# Check if argument is provided
if [ $# -eq 0 ]; then
    echo "❌ Error: Argument required"
    echo "Usage: ./cleanup.sh [f|b|fb]"
    echo "  f:  frontend only"
    echo "  b:  backend only"
    echo "  fb: frontend and backend"
    exit 1
fi

ARG=$1

# Validate argument
if [[ "$ARG" != "f" && "$ARG" != "b" && "$ARG" != "fb" ]]; then
    echo "❌ Error: Invalid argument '$ARG'"
    echo "Usage: ./cleanup.sh [f|b|fb]"
    echo "  f:  frontend only"
    echo "  b:  backend only"
    echo "  fb: frontend and backend"
    exit 1
fi

echo "🧹 Cleaning containers and images..."

# Project container names
BACKEND_CONTAINER="ecommerce_backend"
FRONTEND_CONTAINER="ecommerce_frontend"

# Project image names
BACKEND_IMAGE="ecomfastapireact-backend"
FRONTEND_IMAGE="ecomfastapireact-frontend"

# Function to clean backend
clean_backend() {
    echo "🔄 Cleaning backend..."
    
    # Stop backend container
    if docker ps -q -f name=$BACKEND_CONTAINER | grep -q .; then
        echo "Stopping container: $BACKEND_CONTAINER"
        docker stop $BACKEND_CONTAINER
        echo "Container $BACKEND_CONTAINER stopped"
    else
        echo "Container $BACKEND_CONTAINER is not running"
    fi
    
    # Remove backend container
    if docker ps -aq -f name=$BACKEND_CONTAINER | grep -q .; then
        echo "Removing container: $BACKEND_CONTAINER"
        docker rm $BACKEND_CONTAINER
        echo "Container $BACKEND_CONTAINER removed"
    else
        echo "Container $BACKEND_CONTAINER does not exist"
    fi
    
    # Remove backend image
    if docker images -q $BACKEND_IMAGE | grep -q .; then
        echo "Removing image: $BACKEND_IMAGE"
        docker rmi $BACKEND_IMAGE
        echo "Image $BACKEND_IMAGE removed"
    else
        echo "Image $BACKEND_IMAGE does not exist"
    fi
    
    echo "✅ Backend cleaned"
}

# Function to clean frontend
clean_frontend() {
    echo "🔄 Cleaning frontend..."
    
    # Stop frontend container
    if docker ps -q -f name=$FRONTEND_CONTAINER | grep -q .; then
        echo "Stopping container: $FRONTEND_CONTAINER"
        docker stop $FRONTEND_CONTAINER
        echo "Container $FRONTEND_CONTAINER stopped"
    else
        echo "Container $FRONTEND_CONTAINER is not running"
    fi
    
    # Remove frontend container
    if docker ps -aq -f name=$FRONTEND_CONTAINER | grep -q .; then
        echo "Removing container: $FRONTEND_CONTAINER"
        docker rm $FRONTEND_CONTAINER
        echo "Container $FRONTEND_CONTAINER removed"
    else
        echo "Container $FRONTEND_CONTAINER does not exist"
    fi
    
    # Remove frontend image
    if docker images -q $FRONTEND_IMAGE | grep -q .; then
        echo "Removing image: $FRONTEND_IMAGE"
        docker rmi $FRONTEND_IMAGE
        echo "Image $FRONTEND_IMAGE removed"
    else
        echo "Image $FRONTEND_IMAGE does not exist"
    fi
    
    echo "✅ Frontend cleaned"
}

# Execute cleanup based on argument
case $ARG in
    "f")
        clean_frontend
        ;;
    "b")
        clean_backend
        ;;
    "fb")
        clean_backend
        echo ""
        clean_frontend
        ;;
esac

echo ""
echo "✅ Cleanup completed!"
echo "To rebuild: docker-compose up --build"
