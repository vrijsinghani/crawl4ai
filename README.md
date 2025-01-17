# 🔥🕷️ Crawl4AI: Crawl Smarter, Faster, Freely. For AI.

[Previous content...]

## 🔬 Advanced Usage Examples 🔬

You can check the project structure in the directory [https://github.com/unclecode/crawl4ai/docs/examples](docs/examples). Over there, you can find a variety of examples; here, some popular examples are shared.

<details>
<summary>🕷️ <strong>Spider API: Recursive Website Crawling</strong></summary>

The Spider API allows you to recursively crawl an entire website while respecting domain boundaries and crawl configurations:

```python
import aiohttp
import asyncio

async def spider_example():
    request = {
        "url": "https://example.com",
        "max_depth": 2,          # How deep to crawl
        "max_pages": 50,         # Maximum pages to crawl
        "batch_size": 5,         # Concurrent requests
        "include_patterns": ["/blog/", "/products/"],  # Only crawl matching URLs
        "exclude_patterns": ["/admin/", "/login/"],    # Skip these URLs
        "extraction_config": {"type": "basic"}         # How to extract content
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11235/spider",
            json=request,
            headers={"Authorization": "Bearer your_api_token"}
        ) as response:
            results = await response.json()
            print(f"Crawled {results['crawled_count']} pages")
            print(f"Failed {results['failed_count']} pages")

asyncio.run(spider_example())
```

For more details, see our [Spider API Documentation](docs/spider.md).

</details>

[Rest of existing content...]