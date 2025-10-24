# Quick Deploy Guide - BA Copilot AI Service

## Prerequisites
- Docker & Docker Compose installed
- Google AI API Key (get from https://makersuite.google.com/app/apikey)

## Deploy Steps

### 1. Configure Environment
```bash
cd AI_Implement

# Copy example env file
cp .env.example .env

# Edit .env and add your Google API key
nano .env  # or use any text editor
```

Update this line in `.env`:
```env
GOOGLE_API_KEY=your_actual_google_api_key_here
```

### 2. Build & Start Services
```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f ai-service
```

### 3. Verify Services Running
```bash
# Check containers status
docker-compose ps

# Test health endpoint
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "google_api_configured": true
}
```

### 4. Test API Endpoints

#### Test SRS Generation
```bash
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"message": "Tạo SRS cho hệ thống quản lý thư viện"}'
```

#### Test Wireframe Generation
```bash
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"message": "Tạo wireframe cho trang đăng nhập"}'
```

#### Test Diagram Generation
```bash
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"message": "Tạo ERD cho hệ thống bán hàng"}'
```

#### Or use test script
```bash
chmod +x test_api.sh
./test_api.sh
```

### 5. Access API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Stop Services
```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs ai-service

# Rebuild without cache
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Port already in use
Edit `docker-compose.yml` and change:
```yaml
ports:
  - "8001:8000"  # Change 8001 to any available port
```

### API returns error
1. Check if GOOGLE_API_KEY is set correctly in `.env`
2. Verify key is valid at https://makersuite.google.com/app/apikey
3. Restart container: `docker-compose restart ai-service`

## Production Deployment

For production, update:

1. **docker-compose.yml**
   - Remove `volumes` mapping (for code hot-reload)
   - Change `restart: unless-stopped` to `restart: always`
   - Update CORS origins in main.py

2. **Security**
   - Use strong DB passwords
   - Enable API authentication
   - Set up reverse proxy (nginx)
   - Enable HTTPS

3. **Monitoring**
   - Add logging service
   - Set up health checks
   - Configure alerts

## Quick Commands Cheatsheet

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart service
docker-compose restart ai-service

# Stop services
docker-compose down

# Rebuild
docker-compose build --no-cache

# Check status
docker-compose ps

# Enter container shell
docker-compose exec ai-service bash
```
