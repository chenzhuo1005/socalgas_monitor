from datetime import datetime, timedelta
import re

LOGIN_URL = "https://myaccount.socalgas.com/login"
CDP_URL   = "http://127.0.0.1:3000"  # or read from your config

async def fetch_therms(username: str, password: str):
    """
    Login to SoCalGas via a remote browser, scrape hourly usage,
    and return the most recent non-zero record (or a zeroed stub).
    """

    # Lazy-import Playwright so Home Assistant won't crash at startup
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise RuntimeError(
            "Playwright not installed in HA. "
            "Please install a Browserless Chrome add-on "
            "and use CDP_URL to connect to it."
        )

    # Prepare date strings
    today = datetime.now()
    end   = today.strftime("%m/%d/%Y")

    async with async_playwright() as p:
        # Connect to the headless browser exposed by your add-on
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        page = await browser.new_page()

        # 1. Log in
        await page.goto(LOGIN_URL)
        await page.fill("input[name='email']", username)
        await page.fill("input[name='password']", password)
        await page.click("button.primary.large[aria-label='Log In']")
        await page.wait_for_load_state("networkidle")

        # 2. Analyze Usage
        await page.wait_for_selector("button[aria-label='Analyze Usage']", state="visible", timeout=30000)
        await page.click("button[aria-label='Analyze Usage']")
        await page.wait_for_load_state("networkidle")

        # 3. Table → Hourly inside iframe
        await page.wait_for_selector("iframe[data-testid='sew-iframe']", timeout=30000)
        gb = page.frame_locator("iframe[data-testid='sew-iframe']")
        await gb.locator("a#table").click()
        await gb.locator("a#hourly").click()
        await gb.locator("table.tblhourly tbody tr").first.wait_for(state="visible", timeout=30000)

        # 4. Scrape rows
        rows = gb.locator("table.tblhourly tbody tr")
        entries = []
        for i in range(await rows.count()):
            cells = await rows.nth(i).locator("td").all_text_contents()
            time_str, cost_str, usage_str, avg_temp_str = [c.strip() for c in cells]
            if not re.match(r"^\d{1,2}:\d{2} [AP]M$", time_str):
                continue

            cost     = float(cost_str.replace("$", ""))
            usage    = float(usage_str)
            temp_num = re.sub(r"[^\d.]", "", avg_temp_str)
            avg_temp = float(temp_num) if temp_num else 0.0
            ts       = datetime.strptime(f"{end} {time_str}", "%m/%d/%Y %I:%M %p")

            entries.append({
                "date":      end,
                "time":      time_str,
                "usage":     usage,
                "cost":      cost,
                "avg_temp":  avg_temp,
                "timestamp": ts
            })

        await browser.close()

    # 5. Return the record matching the last full hour, or a zeroed stub
    ref = datetime.now().replace(minute=0, second=0, microsecond=0)
    match = next((e for e in entries if e["timestamp"] == ref), None)
    if match:
        return match

    return {
        "date":      ref.strftime("%m/%d/%Y"),
        "time":      ref.strftime("%I:%M %p"),
        "usage":     0.0,
        "cost":      0.0,
        "avg_temp":  0.0,
        "timestamp": ref
    }