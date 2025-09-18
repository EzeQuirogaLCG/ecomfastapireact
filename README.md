# Ecommerce React with Backend Fastapi

This is a simple project with Fastapi, sqlalchemy, react, redux, and Postgresql. The application has been containerized using Docker for easier deployment and development.

## Prerequisites

Before running this project, you need to install the following tools:

### 1. Node.js Installation
This project uses Claude Code agents that require Node.js. Install Node.js using NVM (Node Version Manager):

```bash
# Install NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Reload your terminal or run:
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Install the latest LTS version of Node.js
nvm install --lts
nvm use --lts
```

### 2. Claude Code Installation
After installing Node.js, install Claude Code globally:

```bash
npm install -g @anthropic-ai/claude-code
```

This will enable you to use the Claude Code agents and tools included in this project.

## Containerized Application

This application has been fully containerized using Docker and Docker Compose. All services (backend, frontend, and database) run in isolated containers, making it easier to:

- Deploy across different environments
- Maintain consistent development environments
- Scale individual services independently
- Avoid dependency conflicts

The containerization includes:
- **Backend**: FastAPI application with Python dependencies
- **Frontend**: React application with Node.js dependencies  
- **Database**: PostgreSQL database with persistent data storage
- **Reverse Proxy**: Nginx for routing and load balancing

## Routes Implement

url: http://localhost:8000/docs

<img src="./images/images8.png" alt="product"/>

## How to use My Project

### Option 1: Using Docker (Recommended)

1. **Prerequisites**: Make sure you have Docker and Docker Compose installed
2. **Clone the repository**:
   ```bash
   git clone https://github.com/renaldyhidayatt/ecomfastapireact
   cd ecomfastapireact
   ```
3. **Start all services with Docker Compose**:
   ```bash
   docker-compose up --build
   ```
4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Manual Installation (Development)

If you prefer to run the services manually for development:

1. **Install Prerequisites** (see Prerequisites section above)
2. **Clone the repository**:
   ```bash
   git clone https://github.com/renaldyhidayatt/ecomfastapireact
   cd ecomfastapireact
   ```
3. **Backend Setup**:
   ```bash
   cd backend
   pip install pipenv
   pipenv install
   pipenv shell
   uvicorn main:app --reload
   ```
4. **Frontend Setup** (in a new terminal):
   ```bash
   cd frontend
   npm install
   npm start
   ```
5. **Database Setup**:
   - Install PostgreSQL
   - Create a database and update connection settings in backend configuration

## Demo

Home

<img src="./images/images1.png" alt="Home" />

Show Product Byid

<img src="./images/images2.png" alt="ProductByid">

Cart Page

<img src="./images/images3.png" alt="CartImage" />

Order with Stripe

<img src="./images/images7.png" alt="Order" />

UserList page

<img src="./images/images4.png" alt="images" />

ProductList PAge

<img src="./images/images5.png" alt="images" />

OrderListPage

<img src="./images/images6.png" alt="Images" />
