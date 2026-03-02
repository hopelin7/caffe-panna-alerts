import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

LOCATIONS = {
    "brooklyn": "https://order.toasttab.com/online/caffe-panna-brooklyn",
    "manhattan": "https://order.toasttab.com/online/caffe-panna",
}

STOP_SECTIONS = ["merchandise", "toppings", "add-ons", "extras"]


async def scrape_flavors(location: str) -> list[str]:
    url = LOCATIONS[location]

    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)

        await page.goto(url, wait_until="load", timeout=60000)
        await page.wait_for_timeout(8000)

        # Find all headings and collect items in the "TODAY'S PINTS" section
        flavors = await page.evaluate("""() => {
            const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4'));

            let inPintsSection = false;
            const flavors = [];

            for (const h of headings) {
                const text = h.innerText.trim();
                const lower = text.toLowerCase();

                if (lower === "today's pints") {
                    inPintsSection = true;
                    continue;
                }

                // Stop when we hit the next major section
                if (inPintsSection && ['merchandise', 'toppings', 'add-ons', 'extras'].includes(lower)) {
                    break;
                }

                if (inPintsSection && text) {
                    flavors.push(text);
                }
            }

            return flavors;
        }""")

        await browser.close()

    return flavors


if __name__ == "__main__":
    async def main():
        for loc in LOCATIONS:
            print(f"\n--- {loc.upper()} ---")
            flavors = await scrape_flavors(loc)
            if flavors:
                for f in flavors:
                    print(f"  • {f}")
            else:
                print("  No flavors found")

    asyncio.run(main())
