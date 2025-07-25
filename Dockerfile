# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with trusted hosts to avoid SSL issues
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy application code
COPY . .

# Create directory for data persistence
RUN mkdir -p /app/data

# Expose Streamlit port
EXPOSE 8501

# Add healthcheck as recommended by Streamlit documentation
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Set environment variable for Streamlit
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Set home directory for the app user so .autodidact folder is created correctly
ENV HOME=/app/data

# Add build argument for debug mode
ARG DEBUG_MODE=false
ENV AUTODIDACT_DEBUG=${DEBUG_MODE}

# Run the application using ENTRYPOINT as recommended by Streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]