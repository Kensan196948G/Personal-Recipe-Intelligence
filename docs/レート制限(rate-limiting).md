# Rate Limiting Documentation

## Overview

Personal Recipe Intelligence API implements IP-based rate limiting using `slowapi` to protect against abuse and ensure fair resource allocation.

## Rate Limit Configuration

### Endpoint-Specific Limits

| Endpoint Category | Rate Limit | Reason |
|------------------|------------|--------|
| OCR (`/api/v1/ocr/*`) | 5 requests/minute | Expensive CPU/GPU operations |
| Video (`/api/v1/video/*`) | 5 requests/minute | Expensive processing operations |
| Scraper (`/api/v1/scraper/*`) | 10 requests/minute | Moderate external network requests |
| Recipes (`/api/v1/recipes/*`) | 100 requests/minute | Standard CRUD operations |
| Default (all others) | 100 requests/minute | General API operations |

## Implementation Details

### Architecture

```
Request → FastAPI → Rate Limiter Middleware → Route Handler → Response
                         ↓
                  (Check IP + Endpoint)
                         ↓
                  [Allow/Block Decision]
```

### Client Identification

Rate limits are applied per client IP address:
1. First checks `X-Forwarded-For` header (for proxy/load balancer scenarios)
2. Falls back to direct remote address

### Storage

- **In-Memory Storage**: Uses `memory://` storage URI
- **Strategy**: Fixed-window algorithm
- **Reset**: Limits reset every minute

## Response Headers

Successful requests include rate limit information in headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1234567890
```

## Error Responses

When rate limit is exceeded, API returns:

```json
{
  "status": "error",
  "data": null,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "detail": "5 per 1 minute"
  }
}
```

**Status Code**: `429 Too Many Requests`

**Additional Headers**:
- `Retry-After: 60` (seconds until limit resets)

## Usage Examples

### Python Client

```python
import requests
import time

API_BASE = "http://localhost:8001"

# OCR endpoint (5/min limit)
for i in range(6):
    response = requests.post(
        f"{API_BASE}/api/v1/ocr/extract",
        json={}
    )

    if response.status_code == 429:
        print("Rate limit exceeded!")
        retry_after = int(response.headers.get("Retry-After", 60))
        time.sleep(retry_after)
    else:
        print(f"Request {i+1} succeeded")
```

### JavaScript Client

```javascript
const API_BASE = "http://localhost:8001";

async function makeRequest() {
  try {
    const response = await fetch(`${API_BASE}/api/v1/recipes`, {
      method: 'GET',
    });

    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After');
      console.log(`Rate limited. Retry after ${retryAfter} seconds`);
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Request failed:', error);
  }
}
```

## Testing

Run rate limiting tests:

```bash
# All rate limiting tests
pytest tests/test_rate_limiter.py -v

# Specific test class
pytest tests/test_rate_limiter.py::TestRateLimiting -v

# Check rate limit status
curl http://localhost:8001/api/v1/rate-limit-status
```

## Configuration

### Modify Rate Limits

Edit `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/backend/middleware/rate_limiter.py`:

```python
# Change OCR limit from 5/min to 10/min
def ocr_rate_limit() -> Callable:
    return limiter.limit("10/minute")  # Changed from 5
```

### Change Storage Backend

For production with multiple servers, use Redis:

```python
limiter = Limiter(
    key_func=get_client_identifier,
    storage_uri="redis://localhost:6379",  # Changed from memory://
    strategy="fixed-window"
)
```

### Custom Rate Limit Strategies

Available strategies:
- `fixed-window`: Simple, fast (current)
- `fixed-window-elastic-expiry`: Better for bursty traffic
- `moving-window`: Most accurate, more resource intensive

## Monitoring

### Check Current Status

```bash
curl http://localhost:8001/api/v1/rate-limit-status
```

Response:
```json
{
  "status": "ok",
  "data": {
    "client_ip": "127.0.0.1",
    "limits": {
      "ocr": "5/minute",
      "video": "5/minute",
      "scraper": "10/minute",
      "default": "100/minute"
    },
    "strategy": "fixed-window"
  }
}
```

### Logs

Rate limit events are logged to `/mnt/Linux-ExHDD/Personal-Recipe-Intelligence/logs/api.log`:

```json
{
  "timestamp": "2025-12-11 10:30:45",
  "name": "backend.middleware.rate_limiter",
  "level": "WARNING",
  "message": "Rate limit exceeded for 192.168.1.100 on /api/v1/ocr/upload",
  "client_ip": "192.168.1.100",
  "path": "/api/v1/ocr/upload",
  "method": "POST"
}
```

## Best Practices

### For API Consumers

1. **Check Response Headers**: Monitor `X-RateLimit-Remaining` to know when you're approaching the limit
2. **Handle 429 Errors**: Implement exponential backoff with `Retry-After` header
3. **Batch Operations**: Combine multiple operations when possible
4. **Cache Responses**: Store frequently accessed data locally

### For API Developers

1. **Set Appropriate Limits**: Balance protection vs usability
2. **Document Limits Clearly**: Make limits visible in API documentation
3. **Monitor Usage Patterns**: Adjust limits based on actual usage
4. **Provide Rate Limit Status**: Allow clients to check their status

## Troubleshooting

### Rate Limit Too Strict

If legitimate users hit limits:
1. Increase limit in `rate_limiter.py`
2. Consider per-user authentication limits (higher for authenticated users)
3. Implement different tiers (free/paid users)

### Rate Limit Too Lenient

If experiencing abuse:
1. Decrease limit in `rate_limiter.py`
2. Add IP-based blocking for repeated violations
3. Implement CAPTCHA for suspicious patterns

### Rate Limits Not Working

Check:
1. `slowapi` is installed: `pip show slowapi`
2. Rate limiter is registered in `app.py`
3. Decorators are applied to routes
4. No proxy issues with IP detection

## Security Considerations

1. **IP Spoofing**: Use `X-Forwarded-For` carefully in production
2. **DDoS Protection**: Rate limiting is one layer; use additional protections
3. **Logging**: Monitor for patterns of abuse
4. **Updates**: Keep `slowapi` updated for security patches

## Performance Impact

- **Memory Usage**: In-memory storage scales with number of unique IPs
- **Response Time**: <1ms overhead per request
- **CPU Usage**: Minimal (simple counter operations)

For high-traffic scenarios, consider Redis backend for distributed rate limiting.

## References

- [slowapi Documentation](https://slowapi.readthedocs.io/)
- [IETF Rate Limiting Draft](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-ratelimit-headers)
- [CLAUDE.md](../CLAUDE.md) - Project development rules
