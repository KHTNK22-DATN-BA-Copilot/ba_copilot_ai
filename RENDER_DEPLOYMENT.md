# Render Deployment Configuration for BA Copilot AI Services

## 🚀 Render Web Service Configuration

### Service Settings

**Name:** `ba-copilot-ai-services`

- Choose a descriptive name that identifies your AI services backend
- This will be part of your service URL: `https://ba-copilot-ai-services.onrender.com`

**Language:** `Docker`

- Render will detect and use the Dockerfile for building the container
- Our multi-stage Dockerfile is optimized for production deployment

**Root Directory:** (Leave empty)

- Since our Dockerfile is in `infrastructure/Dockerfile` and properly configured
- The build context includes the entire repository root
- Do NOT set a root directory as we need access to the entire codebase

**Build Command:**

```bash
docker build -f infrastructure/Dockerfile -t ba-copilot-ai .
```

**Start Command:**

```bash
gunicorn -c /app/gunicorn.conf.py src.main:app
```

### Environment Variables

Set these environment variables in Render dashboard:

#### Required Variables

```bash
# Application Configuration
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Security
SECRET_KEY=NhUUNGKX_-23432_**kz
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration (JSON format)
ALLOWED_ORIGINS=["https://your-frontend-domain.com", "https://your-admin-panel.com"]

# Database Connection (Replace with your actual database credentials)
DATABASE_URL=postgresql://username:password@hostname:port/database_name

# Redis Connection (Replace with your actual Redis credentials)
REDIS_URL=redis://username:password@hostname:port/database_number

# Application Settings
MOCK_DATA_ENABLED=false
MAX_FILE_SIZE=10485760
UPLOAD_DIRECTORY=/tmp/uploads
```

#### Optional API Keys (Add when needed)

```bash
# AI Service API Keys
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-claude-api-key-here
```

### Advanced Settings

#### Health Check Path

```
/v1/health/
```

- This endpoint provides comprehensive health status
- Returns JSON with service status, uptime, and dependencies
- Render will use this to monitor service health

#### Secret Files

Create a secret file named `.env` with sensitive configuration:

```bash
# Content for .env secret file
SECRET_KEY=NhUUNGKX_-23432_**kz
DATABASE_URL=postgresql://username:password@hostname:port/database_name
REDIS_URL=redis://username:password@hostname:port/database_number
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-claude-api-key-here
```

#### Build Filters

Include paths:

```
src/**
infrastructure/**
requirements.txt
gunicorn.conf.py
README.md
```

Exclude paths:

```
tests/**
docs/**
.git/**
.venv/**
__pycache__/**
*.pyc
.env.template
.coverage
htmlcov/**
```

## 📊 Service Specifications

### Recommended Plan

- **Starter Plan** (Minimum): $7/month

  - 512 MB RAM
  - 0.1 CPU
  - Suitable for development/testing

- **Standard Plan** (Recommended): $25/month
  - 2 GB RAM
  - 1 CPU
  - Better for production workloads

### Resource Limits

The gunicorn configuration automatically scales workers based on available CPU cores:

- Workers = (CPU cores × 2) + 1
- Each worker uses ~50-100MB RAM
- Total memory usage scales with worker count

## 🗄️ External Dependencies

### Database Setup

You'll need to set up external PostgreSQL and Redis services:

#### PostgreSQL Options:

1. **Render PostgreSQL** (Recommended)

   - Create a PostgreSQL database in Render
   - Copy the `DATABASE_URL` to your environment variables

2. **External Providers:**
   - AWS RDS
   - Google Cloud SQL
   - Azure Database for PostgreSQL

#### Redis Options:

1. **Render Redis** (Recommended)

   - Create a Redis instance in Render
   - Copy the `REDIS_URL` to your environment variables

2. **External Providers:**
   - Redis Cloud
   - AWS ElastiCache
   - Google Cloud Memorystore

## 🚢 Deployment Process

### Step 1: Repository Setup

1. Ensure your code is in a Git repository (GitHub, GitLab, etc.)
2. Verify the Dockerfile builds successfully locally
3. Test the application runs correctly in Docker

### Step 2: Render Service Creation

1. Log into Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your Git repository
4. Fill in the configuration as specified above

### Step 3: Environment Configuration

1. Set all required environment variables
2. Upload the `.env` secret file if using sensitive data
3. Configure the health check path

### Step 4: Database & Redis Setup

1. Create PostgreSQL database service in Render
2. Create Redis service in Render
3. Update `DATABASE_URL` and `REDIS_URL` environment variables

### Step 5: Deploy & Monitor

1. Click "Create Web Service"
2. Monitor the build logs for any issues
3. Check the health endpoint once deployed
4. Verify API endpoints are working

## 🔍 Troubleshooting

### Common Issues

**Build Failures:**

- Check Docker build logs
- Ensure all dependencies are in requirements.txt
- Verify Dockerfile paths are correct

**Runtime Errors:**

- Check application logs in Render dashboard
- Verify environment variables are set correctly
- Ensure database/Redis connections are working

**Health Check Failures:**

- Verify `/v1/health/` endpoint is accessible
- Check if the application is starting on the correct port (8000)
- Review gunicorn worker status

### Log Monitoring

The application logs include:

- Application startup/shutdown events
- Request/response logs
- Error details with stack traces
- Health check status

## 🔐 Security Considerations

1. **Environment Variables:** Never commit sensitive data to Git
2. **Secret Keys:** Use strong, unique secret keys for production
3. **CORS Configuration:** Restrict allowed origins to your frontend domains
4. **Database Security:** Use SSL connections for database and Redis
5. **API Rate Limiting:** Consider implementing rate limiting for production

## 📈 Performance Optimization

1. **Worker Count:** Gunicorn automatically optimizes based on CPU
2. **Memory Usage:** Monitor memory usage and upgrade plan if needed
3. **Database Connections:** Use connection pooling (already configured)
4. **Caching:** Redis is configured for session and data caching
5. **Health Checks:** Optimized for fast response times

## 🔄 Continuous Deployment

Render automatically deploys when you push to your connected Git branch:

1. Push code changes to your repository
2. Render detects changes and starts build
3. Application is automatically updated
4. Health checks verify successful deployment

For production, consider:

- Using separate staging and production services
- Implementing proper Git workflow (main/develop branches)
- Testing deployments in staging before production
