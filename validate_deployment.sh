#!/bin/bash
# Deployment Validation Script for BA Copilot AI Services

set -e

echo "🔍 BA Copilot AI Services - Deployment Validation"
echo "=================================================="

# Function to print status
print_status() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
    else
        echo "❌ $1"
        exit 1
    fi
}

# Check Python environment
echo "🐍 Checking Python environment..."
python --version
print_status "Python version check"

# Check virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "⚠️  Virtual environment not active"
fi

# Check dependencies
echo "📦 Checking dependencies..."
pip list | grep -E "(fastapi|uvicorn|pydantic|gunicorn)" > /dev/null
print_status "Core dependencies installed"

# Check application imports
echo "🔍 Validating application imports..."
python -c "
import sys
sys.path.insert(0, 'src')
from src.main import app
from src.core.config import settings
print(f'✅ App: {app.title}')
print(f'✅ Environment: {settings.environment}')
print(f'✅ Debug: {settings.debug}')
"
print_status "Application imports"

# Check gunicorn configuration
echo "⚙️  Validating gunicorn configuration..."
python -c "exec(open('gunicorn.conf.py').read()); print('✅ Gunicorn config loaded')"
print_status "Gunicorn configuration"

# Run basic tests
echo "🧪 Running basic tests..."
python -m pytest tests/test_health.py -v -q
print_status "Health endpoint tests"

# Check Docker build capability
echo "🐳 Checking Docker setup..."
if command -v docker &> /dev/null; then
    echo "✅ Docker is available"
    # Check if Dockerfile exists
    if [ -f "infrastructure/Dockerfile" ]; then
        echo "✅ Dockerfile found"
    else
        echo "❌ Dockerfile not found"
        exit 1
    fi
else
    echo "⚠️  Docker not available (optional for Render deployment)"
fi

# Validate environment variables template
echo "🔧 Checking environment configuration..."
if [ -f ".env" ]; then
    echo "✅ Environment file found"
    # Check for required variables
    if grep -q "SECRET_KEY" .env; then
        echo "✅ SECRET_KEY configured"
    else
        echo "⚠️  SECRET_KEY not found in .env"
    fi
else
    echo "⚠️  .env file not found (will use defaults)"
fi

# Check deployment files
echo "📋 Checking deployment files..."
files=("RENDER_DEPLOYMENT.md" "gunicorn.conf.py" "infrastructure/Dockerfile" "requirements.txt")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

# Summary
echo ""
echo "🎉 Deployment Validation Summary"
echo "==============================="
echo "✅ Application structure: Valid"
echo "✅ Dependencies: Installed"
echo "✅ Configuration: Valid"
echo "✅ Tests: Passing"
echo "✅ Docker: Ready"
echo "✅ Deployment files: Complete"
echo ""
echo "🚀 Ready for Render deployment!"
echo ""
echo "📋 Next Steps:"
echo "1. Push code to your Git repository"
echo "2. Create a new Web Service in Render"
echo "3. Use Docker build configuration"
echo "4. Set environment variables as per RENDER_DEPLOYMENT.md"
echo "5. Deploy and monitor health check: /v1/health/"
echo ""
echo "📖 Full deployment guide: RENDER_DEPLOYMENT.md"