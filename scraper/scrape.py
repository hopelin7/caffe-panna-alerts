import asyncio
from playwright.async_api import async_playwright

LOCATIONS = {
    "brooklyn": "https://order.toasttab.com/online/caffe-panna",
    "manhattan": "https://order.toasttab.com/online/caffe-panna-manhattan",  # verify this URL
}

ICE_CREAM_KEYWORDS = ["gelato", "ice cream", "sorbet", "flavor", "scoop", "soft serve"]


async def scrape_flavors(location: str) -> list[str]:
    url = LOCATIONS[location]

    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        await page.goto(url, wait_until="networkidle", timeout=45000)
        await page.wait_for_timeout(4000)  # extra wait for React to render

        flavors = []

        # Strategy 1: find sections whose heading contains ice cream keywords,
        # then pull item names from inside that section
        headings = await page.query_selector_all("h1, h2, h3, h4")
        for heading in headings:
            heading_text = (await heading.inner_text()).strip().lower()
            if any(kw in heading_text for kw in ICE_CREAM_KEYWORDS):
                # walk up to the nearest section container
                section = await heading.evaluate_handle(
                    """el => {
                        let node = el.parentElement;
                        for (let i = 0; i < 5; i++) {
                            if (!node) break;
                            if (node.tagName === 'SECTION' ||
                                /section|group|category/i.test(node.className)) return node;
                            node = node.parentElement;
                        }
                        return el.parentElement;
                    }"""
                )
                items = await section.query_selector_all("h3, h4, [class*='item'][class*='name'], [class*='Name']")
                for item in items:
                    text = (await item.inner_text()).strip()
                    if text and text.lower() != heading_text:
                        flavors.append(text)

        # Strategy 2: common Toast Tab data-testid and class patterns
        if not flavors:
            selectors = [
                "[data-testid='menu-item-name']",
                "[class*='menuItemName']",
                "[class*='menu-item-name']",
                "[class*='itemName']",
                "[class*='item-name']",
            ]
            for selector in selectors:
                items = await page.query_selector_all(selector)
                if items:
                    for item in items:
                        text = (await item.inner_text()).strip()
                        if text:
                            flavors.append(text)
                    break

        await browser.close()

    # dedupe while preserving order
    seen = set()
    unique = []
    for f in flavors:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    return unique


if __name__ == "__main__":
    async def main():
        for loc in LOCATIONS:
            print(f"\n--- {loc.upper()} ---")
            flavors = await scrape_flavors(loc)
            if flavors:
                for f in flavors:
                    print(f"  • {f}")
            else:
                print("  No flavors found — selectors may need adjustment")

    asyncio.run(main())
