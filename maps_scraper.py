"""
Google Maps business scraper.

Usage:
    python maps_scraper.py "dentists in Bangalore" --max 50

Output: results.xlsx with name, phone, address, website, rating, reviews.

Setup (one-time):
    pip install playwright openpyxl
    playwright install chromium
"""

import argparse
import asyncio
import re
from pathlib import Path

from openpyxl import Workbook
from playwright.async_api import async_playwright, TimeoutError as PWTimeout


MAPS_URL = "https://www.google.com/maps/search/{query}"


async def scroll_results(page, max_results: int):
    """Scroll the left-hand results panel until we have enough listings or hit the end."""
    panel_selector = 'div[role="feed"]'
    await page.wait_for_selector(panel_selector, timeout=15000)

    seen = 0
    stagnant_rounds = 0
    while True:
        cards = await page.query_selector_all('div[role="feed"] > div > div[jsaction]')
        count = len(cards)

        if count >= max_results:
            break

        if count == seen:
            stagnant_rounds += 1
            if stagnant_rounds >= 4:
                break
        else:
            stagnant_rounds = 0
            seen = count

        await page.evaluate(
            '(sel) => { const el = document.querySelector(sel); '
            'if (el) el.scrollBy(0, el.scrollHeight); }',
            panel_selector,
        )
        await page.wait_for_timeout(1500)

    return await page.query_selector_all('div[role="feed"] > div > div[jsaction]')


async def extract_detail(page, card) -> dict:
    """Click a card and pull details from the right-hand info pane."""
    await card.scroll_into_view_if_needed()
    await card.click()
    # Wait for the detail pane header to render.
    try:
        await page.wait_for_selector('h1.DUwDvf', timeout=8000)
    except PWTimeout:
        return {}

    await page.wait_for_timeout(800)  # let buttons populate

    async def text_of(selector: str) -> str:
        el = await page.query_selector(selector)
        return (await el.inner_text()).strip() if el else ""

    name = await text_of("h1.DUwDvf")

    # Address, phone, website live in buttons with data-item-id attributes.
    address = ""
    phone = ""
    website = ""

    addr_btn = await page.query_selector('button[data-item-id="address"]')
    if addr_btn:
        address = (await addr_btn.get_attribute("aria-label") or "").replace("Address: ", "").strip()

    phone_btn = await page.query_selector('button[data-item-id^="phone:tel:"]')
    if phone_btn:
        phone = (await phone_btn.get_attribute("aria-label") or "").replace("Phone: ", "").strip()

    site_btn = await page.query_selector('a[data-item-id="authority"]')
    if site_btn:
        website = (await site_btn.get_attribute("href") or "").strip()

    rating = ""
    reviews = ""
    rating_el = await page.query_selector('div.F7nice span[aria-hidden="true"]')
    if rating_el:
        rating = (await rating_el.inner_text()).strip()
    reviews_el = await page.query_selector('div.F7nice span[aria-label$="reviews"]')
    if reviews_el:
        label = await reviews_el.get_attribute("aria-label") or ""
        m = re.search(r"[\d,]+", label)
        reviews = m.group(0) if m else ""

    return {
        "name": name,
        "phone": phone,
        "address": address,
        "website": website,
        "rating": rating,
        "reviews": reviews,
    }


async def scrape(query: str, max_results: int, out_path: Path, headless: bool):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            viewport={"width": 1400, "height": 900},
            locale="en-US",
        )
        page = await context.new_page()

        url = MAPS_URL.format(query=query.replace(" ", "+"))
        print(f"Opening {url}")
        await page.goto(url, wait_until="domcontentloaded")

        # Consent screen (EU/regional). Click any "Accept all" if present.
        try:
            await page.click('button:has-text("Accept all")', timeout=3000)
        except PWTimeout:
            pass

        cards = await scroll_results(page, max_results)
        print(f"Found {len(cards)} cards, extracting up to {max_results}.")

        rows = []
        seen_keys = set()
        dupes = 0
        for i, card in enumerate(cards[:max_results], start=1):
            try:
                data = await extract_detail(page, card)
                if not data.get("name"):
                    continue
                # Dedup key: prefer phone (most unique), fall back to name+address.
                key = data["phone"].strip() if data.get("phone") else f"{data['name']}|{data.get('address','')}".lower()
                if key in seen_keys:
                    dupes += 1
                    print(f"  [{i}] duplicate skipped: {data['name']}")
                    continue
                seen_keys.add(key)
                rows.append(data)
                print(f"  [{i}] {data['name']} | {data.get('phone','')}")
            except Exception as e:
                print(f"  [{i}] skipped: {e}")
                continue
        if dupes:
            print(f"\nRemoved {dupes} duplicate(s).")

        await browser.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "leads"
    headers = ["name", "phone", "address", "website", "rating", "reviews"]
    ws.append(headers)
    for r in rows:
        ws.append([r.get(h, "") for h in headers])
    wb.save(out_path)
    print(f"\nSaved {len(rows)} rows -> {out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", help='Search term, e.g. "dentists in Bangalore"')
    ap.add_argument("--max", type=int, default=30, help="Max results (default 30)")
    ap.add_argument("--out", default="results.xlsx", help="Output Excel file")
    ap.add_argument("--show", action="store_true", help="Show browser window (default headless)")
    args = ap.parse_args()

    asyncio.run(scrape(args.query, args.max, Path(args.out), headless=not args.show))


if __name__ == "__main__":
    main()
