import asyncio
import os
from scrape import scrape_flavors, LOCATIONS
from notify import get_subscribers, send_sms, format_message, get_supabase


def log_flavors(location: str, flavors: list[str]):
    """Save today's flavors to the DB for a history log."""
    try:
        sb = get_supabase()
        sb.table("flavor_log").insert({"location": location, "flavors": flavors}).execute()
    except Exception as e:
        print(f"  Warning: could not log flavors: {e}")


async def main():
    for location in LOCATIONS:
        print(f"\nScraping {location}...")
        flavors = await scrape_flavors(location)

        if not flavors:
            print(f"  No flavors found for {location}, skipping notifications")
            continue

        print(f"  Found {len(flavors)} flavors: {', '.join(flavors)}")
        log_flavors(location, flavors)

        subscribers = get_subscribers(location)
        print(f"  Notifying {len(subscribers)} subscribers")

        message = format_message(location, flavors)
        for sub in subscribers:
            try:
                send_sms(sub["phone"], message)
                print(f"    ✓ {sub['phone']}")
            except Exception as e:
                print(f"    ✗ {sub['phone']}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
