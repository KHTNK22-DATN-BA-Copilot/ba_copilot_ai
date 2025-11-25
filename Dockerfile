# Dockerfile for AI Service with Node.js Mermaid Validator
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Node.js and Puppeteer dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    gnupg \
    # Puppeteer/Chromium dependencies
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
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
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

# Create startup script to run both Node.js validator and FastAPI
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Starting Mermaid Validator Service..."\n\
cd /app/services/mermaid_validator/nodejs\n\
PORT=51234 HOST=localhost node server.js &\n\
VALIDATOR_PID=$!\n\
echo "Validator started with PID: $VALIDATOR_PID on port 51234"\n\
\n\
# Wait for validator to be ready\n\
echo "Waiting for validator to be ready..."\n\
for i in {1..30}; do\n\
    if curl -f http://localhost:51234/health >/dev/null 2>&1; then\n\
        echo "Validator is ready!"\n\
        break\n\
    fi\n\
    echo "Attempt $i/30: Validator not ready yet..."\n\
    sleep 1\n\
done\n\
\n\
cd /app\n\
echo "Starting FastAPI application..."\n\
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/bin/bash", "/app/start.sh"]
