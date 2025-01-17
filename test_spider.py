import asyncio
import aiohttp
import json
from urllib.parse import urljoin
from datetime import datetime
import os

async def test_spider(base_url: str, output_dir: str = "spider_results"):
    """
    Test the spider endpoint by crawling a website and saving results
    
    Args:
        base_url: The starting URL to spider
        output_dir: Directory to save results (will be created if doesn't exist)
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp for unique output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Spider request configuration
    request = {
        "url": base_url,
        "max_depth": 2,  # How deep to crawl
        "max_pages": 20,  # Maximum number of pages to crawl
        "batch_size": 5,  # Number of concurrent requests
        "include_patterns": [],  # Optional: ["blog", "products"]
        "exclude_patterns": [],  # Optional: ["login", "admin"]
        "extraction_config": {
            "type": "basic"  # Can be "basic", "llm", "cosine", or "json_css"
        },
        "crawler_params": {
            "timeout": 30,  # Seconds per request
            "screenshot": True,  # Take screenshots
        }
    }

    try:
        # Connect to the crawler service
        async with aiohttp.ClientSession() as session:
            # Make request to spider endpoint
            print(f"\nStarting spider crawl of {base_url}")
            print("This may take a while depending on the site size and configuration...")
            
            start_time = datetime.now()
            
            async with session.post(
                "http://localhost:11235/spider",
                json=request,
                headers={"Authorization": "Bearer test_api_code"},
                timeout=600  # 10 minute timeout for entire crawl
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Error: Spider request failed with status {response.status}")
                    print(f"Error details: {error_text}")
                    return
                
                results = await response.json()
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                # Print summary
                print("\nCrawl Summary:")
                print(f"Total pages crawled: {results['crawled_count']}")
                print(f"Failed pages: {results['failed_count']}")
                print(f"Max depth reached: {results['max_depth_reached']}")
                print(f"Duration: {duration:.2f} seconds")
                
                # Save full results
                results_file = os.path.join(output_dir, f"spider_results_{timestamp}.json")
                with open(results_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2)
                print(f"\nFull results saved to: {results_file}")
                
                # Generate a simple site map
                sitemap_file = os.path.join(output_dir, f"sitemap_{timestamp}.txt")
                with open(sitemap_file, 'w', encoding='utf-8') as f:
                    f.write(f"Sitemap for {base_url}\n")
                    f.write(f"Generated on: {datetime.now().isoformat()}\n\n")
                    
                    # Write successful URLs and their titles
                    f.write("Successfully crawled pages:\n")
                    for url, result in results['results'].items():
                        # Try to extract title from results
                        title = "Unknown Title"
                        if result.get('metadata') and result['metadata'].get('title'):
                            title = result['metadata']['title']
                        f.write(f"- {url}\n    Title: {title}\n")
                    
                    # Write failed URLs and their errors
                    if results['failed_urls']:
                        f.write("\nFailed pages:\n")
                        for url, error in results['failed_urls'].items():
                            f.write(f"- {url}\n    Error: {error}\n")
                
                print(f"Sitemap saved to: {sitemap_file}")
                
                # Save screenshots if any
                screenshot_dir = os.path.join(output_dir, f"screenshots_{timestamp}")
                os.makedirs(screenshot_dir, exist_ok=True)
                
                screenshot_count = 0
                for url, result in results['results'].items():
                    if result.get('screenshot'):
                        # Create a safe filename from the URL
                        safe_name = "".join(c if c.isalnum() else "_" for c in url)[-50:]
                        screenshot_file = os.path.join(screenshot_dir, f"{safe_name}.png")
                        
                        # Save base64 screenshot as PNG
                        import base64
                        screenshot_data = base64.b64decode(result['screenshot'])
                        with open(screenshot_file, 'wb') as f:
                            f.write(screenshot_data)
                        screenshot_count += 1
                
                if screenshot_count > 0:
                    print(f"Saved {screenshot_count} screenshots to: {screenshot_dir}")

    except aiohttp.ClientError as e:
        print(f"Network error occurred: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

def main():
    # Example URLs to test with
    test_urls = [
        "https://fastapi.tiangolo.com/",  # FastAPI docs - good for testing
        # "https://python.org",           # Python.org - medium size
        # "https://httpbin.org",          # Simple test site
    ]
    
    print("Spider Test Program")
    print("==================")
    
    # Let user pick a URL or enter their own
    print("\nChoose a URL to spider:")
    for i, url in enumerate(test_urls, 1):
        print(f"{i}. {url}")
    print("0. Enter custom URL")
    
    choice = input("\nEnter choice (0-{}): ".format(len(test_urls)))
    
    try:
        choice = int(choice)
        if choice == 0:
            url = input("Enter URL to spider (include http:// or https://): ")
        else:
            url = test_urls[choice - 1]
            
        # Run the spider test
        asyncio.run(test_spider(url))
        
    except (ValueError, IndexError):
        print("Invalid choice!")
    except KeyboardInterrupt:
        print("\nTest cancelled by user")

if __name__ == "__main__":
    main()