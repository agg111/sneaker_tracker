import asyncio
import re
from urllib.parse import quote_plus
from playwright.async_api import async_playwright

async def scrape_amazon(product_name: str, limit: int = 3):
    search_url = f"https://www.amazon.com/s?k={quote_plus(product_name)}"
    sneakers = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/118.0.5993.90 Safari/537.36"
            )
        )
        page = await context.new_page()

        try:
            print(f"Navigating to: {search_url}")
            await page.goto(search_url, timeout=15000)
            await page.wait_for_selector('[data-component-type="s-search-result"]', timeout=10000)
            await page.screenshot(path="amazon_search.png")
            print("Saved screenshot as amazon_search.png")

            results = await page.query_selector_all('[data-component-type="s-search-result"]')
            print(f"Found {len(results)} results on page")

            for idx, result in enumerate(results[:limit]):
                try:
                    # Title is inside an <h2> with a <span> child
                    title_elem = await result.query_selector('h2.a-size-base-plus span')

                    # Price is inside <span class="a-offscreen"> within a <span class="a-price">
                    price_elem = await result.query_selector('span.a-price span.a-offscreen')

                    # Link is in the parent <a> with class a-link-normal
                    link_elem = await result.query_selector('a.a-link-normal')

                    image_elem = await result.query_selector('img.s-image')
                    image_url = await image_elem.get_attribute('src') if image_elem else ''

                    if not title_elem or not price_elem or not link_elem:
                        
                        print(f"Skipping result {idx} due to missing title, price, or link")
                        continue

                    title = (await title_elem.inner_text()).strip()
                    price_text = (await price_elem.inner_text()).strip().replace('$', '').replace(',', '')
                    link_suffix = await link_elem.get_attribute('href')
                    link = f"https://www.amazon.com{link_suffix}"

                    price = float(price_text)

                    sneakers.append({
                        'product_name': title,
                        'price': price,
                        'currency': 'USD',
                        'url': link,
                        'image_url': image_url
                    })

                except Exception as e:
                    print(f"Skipping result {idx} due to error: {e}")

            await browser.close()
            return sneakers

        except Exception as e:
            await browser.close()
            print("Error:", e)
            return {'error': str(e)}
