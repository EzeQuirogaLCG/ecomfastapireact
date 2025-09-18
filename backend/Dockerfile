# Dockerfile for Backend FastAPI
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for PostgreSQL and ML libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY Pipfile Pipfile.lock ./

# Install pipenv and dependencies
RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy

# Download necessary NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon'); nltk.download('stopwords')"

# Copy application code directly to working directory
COPY app/ ./

# Create directory for SQLite database (if used)
RUN mkdir -p /app

# Expose port
EXPOSE 8000

# Default environment variables
ENV PYTHONPATH=/app
ENV USE_SQLITE_DB=False

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
