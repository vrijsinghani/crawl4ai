# Spider API Documentation

The Spider API provides functionality to recursively crawl websites while respecting site boundaries and crawl configurations. This document explains how to use the spider endpoint, its parameters, and response format.

## Endpoint

```
POST /spider
```

## Authentication

The endpoint requires the same authentication as other Crawl4AI endpoints. Include your API token in the Authorization header:

```
Authorization: Bearer your_api_token
```

## Request Body

The request body should be a JSON object with the following structure:

```json
{
    "url": "https://example.com",
    "max_depth": 3,
    "max_pages": 100,
    "batch_size": 10,
    "include_patterns": ["blog/", "products/"],
    "exclude_patterns": ["login/", "admin/"],
    "extraction_config": {
        "type": "basic",
        "params": {}
    },
    "crawler_params": {
        "timeout": 30,
        "screenshot": true
    }
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| url | string (HttpUrl) | Yes | - | The starting URL to spider |
| max_depth | integer | No | 3 | Maximum recursion depth (1-10) |
| max_pages | integer | No | 100 | Maximum total pages to crawl (1-1000) |
| batch_size | integer | No | 10 | Number of concurrent requests (1-50) |
| include_patterns | string[] | No | null | URL patterns to include (substring match) |
| exclude_patterns | string[] | No | null | URL patterns to exclude (substring match) |
| extraction_config | object | No | null | Extraction strategy configuration |
| crawler_params | object | No | {} | Additional crawler parameters |

### Extraction Config Types

The `extraction_config.type` can be one of:

- `"basic"`: Standard HTML extraction
- `"llm"`: LLM-based content extraction
- `"cosine"`: Cosine similarity-based extraction
- `"json_css"`: CSS selector-based structured extraction

## Response

The response is a JSON object containing:

```json
{
    "crawled_count": 42,
    "failed_count": 3,
    "max_depth_reached": 3,
    "results": {
        "https://example.com/": {
            "url": "https://example.com/",
            "html": "...",
            "success": true,
            "cleaned_html": "...",
            "links": {
                "internal": [
                    {"href": "/page1", "text": "Page 1"},
                    {"href": "/page2", "text": "Page 2"}
                ],
                "external": []
            },
            "media": {},
            "screenshot": "base64...",
            "extracted_content": "..."
        }
    },
    "failed_urls": {
        "https://example.com/broken": "404 Not Found",
        "https://example.com/timeout": "Request timed out"
    }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| crawled_count | integer | Number of successfully crawled pages |
| failed_count | integer | Number of failed crawl attempts |
| max_depth_reached | integer | Maximum depth reached in crawl |
| results | object | Map of URLs to their CrawlResults |
| failed_urls | object | Map of URLs to their error messages |

Each URL in `results` contains a standard CrawlResult object with all the usual fields (html, links, media, etc.).

## Example Usage

### Python Example

```python
import aiohttp
import asyncio

async def spider_example():
    request = {
        "url": "https://example.com",
        "max_depth": 2,
        "max_pages": 50,
        "include_patterns": ["/blog/"],
        "extraction_config": {"type": "basic"}
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11235/spider",
            json=request,
            headers={"Authorization": "Bearer your_api_token"}
        ) as response:
            results = await response.json()
            print(f"Crawled {results['crawled_count']} pages")

asyncio.run(spider_example())
```

### cURL Example

```bash
curl -X POST "http://localhost:11235/spider" \
     -H "Authorization: Bearer your_api_token" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://example.com",
       "max_depth": 2,
       "max_pages": 50
     }'
```

## Rate Limiting and Politeness

The spider endpoint automatically:

1. Respects robots.txt rules
2. Implements polite delays between requests
3. Uses concurrent requests carefully
4. Stays within the same domain
5. Respects server rate limits

## Error Handling

Common error responses:

- 401: Invalid or missing API token
- 400: Invalid request parameters
- 429: Too many requests
- 500: Server-side error

Failed individual page crawls are tracked in the `failed_urls` response field rather than failing the entire request.

## Best Practices

1. Start with small `max_depth` and `max_pages` values to test
2. Use `include_patterns` to focus crawls on relevant sections
3. Set appropriate `batch_size` based on site capabilities
4. Consider using `extraction_config` for focused content extraction
5. Monitor `failed_urls` for patterns indicating configuration issues

## Limitations

- Maximum depth: 10 levels
- Maximum pages: 1000 per request
- Maximum batch size: 50 concurrent requests
- Timeout: 10 minutes per spider request
- Domain restricted: Only crawls within starting domain