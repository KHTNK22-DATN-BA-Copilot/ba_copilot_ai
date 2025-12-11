# Dockerfile for AI Service with Node.js Mermaid Validator
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Node.js and Puppeteer dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    ca-certificates \
    gnupg \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libglib2.0-0 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Verify Node.js and npm installation
RUN node --version && npm --version

# Copy and install Node.js validator dependencies first (for better caching)
COPY services/mermaid_validator/nodejs/package*.json /app/services/mermaid_validator/nodejs/
WORKDIR /app/services/mermaid_validator/nodejs
RUN npm ci --only=production && npm cache clean --force

# Copy Node.js validator source code
COPY services/mermaid_validator/nodejs/ /app/services/mermaid_validator/nodejs/

# Create temp directory for validator
RUN mkdir -p /app/services/mermaid_validator/nodejs/temp

# Switch back to app root
WORKDIR /app

# Copy Python requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create models directory if not exists
RUN mkdir -p models

# Expose ports (8000 for FastAPI, validator runs on localhost only)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Copy and set up startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Run the startup script
CMD ["/bin/bash", "/app/start.sh"]

