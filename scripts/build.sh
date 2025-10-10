#!/bin/bash
# Render Build Script for BA Copilot AI Services

set -e  # Exit on any error

echo "🚀 Starting BA Copilot AI Services build process..."

# Check Python version
echo "📋 Checking Python version..."
python --version

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Verify application can be imported
echo "🔍 Verifying application imports..."
python -c "
import sys
sys.path.insert(0, 'src')
try:
    from src.main import app
    print('✅ Application imports successfully')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

# Check if gunicorn configuration is valid
echo "⚙️  Validating gunicorn configuration..."
python -c "
import sys
try:
    exec(open('gunicorn.conf.py').read())
    print('✅ Gunicorn configuration is valid')
except Exception as e:
    print(f'❌ Gunicorn config error: {e}')
    sys.exit(1)
"

echo "✅ Build completed successfully!"
echo "🎯 Application ready for deployment"