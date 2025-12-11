# Rate Limiting Quick Start Guide

## Installation

1. Install dependencies:
```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend
pip install -r requirements-test.txt
```

2. Make scripts executable:
```bash
chmod +x /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/dev.sh
chmod +x /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/test-rate-limit.sh
```

## Starting the API

```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
./dev.sh
```

The API will start at `http://localhost:8000`

## Testing Rate Limits

### Automated Test
```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
./test-rate-limit.sh
```

### Manual Test
```bash
# Check rate limit status
curl http://localhost:8000/api/v1/rate-limit-status

# Test OCR endpoint (5/min limit)
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/v1/ocr/extract \
    -H "Content-Type: application/json" \
    -d '{}' \
    -w "\nHTTP Status: %{http_code}\n\n"
  sleep 0.5
done
# 6th request should return 429 (Rate Limit Exceeded)
```

### Unit Tests
```bash
cd /mnt/Linux-ExHDD/Personal-Recipe-Intelligence
pytest tests/test_rate_limiter.py -v
```

## Rate Limits Summary

| Endpoint | Limit | Use Case |
|----------|-------|----------|
| `/api/v1/ocr/*` | 5/min | Image OCR processing |
| `/api/v1/video/*` | 5/min | Video processing |
| `/api/v1/scraper/*` | 10/min | Web scraping |
| `/api/v1/recipes/*` | 100/min | Recipe CRUD |
| All others | 100/min | General operations |

## Key Files

- **Middleware**: `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/middleware/rate_limiter.py`
- **Main App**: `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/app.py`
- **API Routes**:
  - OCR: `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/api/v1/ocr.py`
  - Video: `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/api/v1/video.py`
  - Scraper: `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/api/v1/scraper.py`
  - Recipes: `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/api/v1/recipes.py`
- **Tests**: `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/tests/test_rate_limiter.py`
- **Documentation**: `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/docs/RATE_LIMITING.md`

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Rate Limit Status
```bash
curl http://localhost:8000/api/v1/rate-limit-status | python3 -m json.tool
```

### OCR Endpoints (5/min)
```bash
# Upload image for OCR
curl -X POST http://localhost:8000/api/v1/ocr/upload \
  -F "file=@image.jpg"

# Extract text
curl -X POST http://localhost:8000/api/v1/ocr/extract \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Video Endpoints (5/min)
```bash
# Upload video
curl -X POST http://localhost:8000/api/v1/video/upload \
  -F "file=@video.mp4"

# Process video
curl -X POST http://localhost:8000/api/v1/video/process \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Scraper Endpoints (10/min)
```bash
# Parse URL
curl -X POST http://localhost:8000/api/v1/scraper/parse-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/recipe"}'

# Extract recipe from URL
curl -X POST http://localhost:8000/api/v1/scraper/extract-recipe \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/recipe"}'
```

### Recipe Endpoints (100/min)
```bash
# List recipes
curl http://localhost:8000/api/v1/recipes

# Get recipe by ID
curl http://localhost:8000/api/v1/recipes/1

# Create recipe
curl -X POST http://localhost:8000/api/v1/recipes \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Recipe",
    "ingredients": ["ingredient1", "ingredient2"],
    "instructions": ["step1", "step2"],
    "tags": ["tag1"]
  }'

# Update recipe
curl -X PUT http://localhost:8000/api/v1/recipes/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Recipe"
  }'

# Delete recipe
curl -X DELETE http://localhost:8000/api/v1/recipes/1
```

## Troubleshooting

### Rate limit not working
1. Check slowapi is installed: `pip show slowapi`
2. Verify app.py has rate limiter registered
3. Check logs: `tail -f /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/logs/api.log`

### Getting 429 too quickly
Rate limits reset every minute. Wait 60 seconds and try again.

### Need to change limits
Edit `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/middleware/rate_limiter.py`

## Interactive API Documentation

Visit `http://localhost:8000/api/docs` for Swagger UI with:
- All endpoints documented
- Try it out functionality
- Request/response schemas
- Rate limit information

## Monitoring

Watch logs in real-time:
```bash
tail -f /mnt/Linux-ExHDD/Personal-Recipe-Intelligence/logs/api.log | grep -i "rate"
```

## Next Steps

1. Implement actual OCR processing logic
2. Implement video processing logic
3. Implement web scraping logic
4. Add database integration for recipes
5. Add authentication (different rate limits for authenticated users)
6. Switch to Redis for distributed rate limiting in production

## References

- Full documentation: `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/docs/RATE_LIMITING.md`
- Project rules: `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/CLAUDE.md`
