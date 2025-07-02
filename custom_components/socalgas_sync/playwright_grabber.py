from datetime import datetime, timedelta
import re
from playwright.async_api import async_playwright

LOGIN_URL = "https://myaccount.socalgas.com/login"

async def fetch_therms(username: str, password: str):
    """
    Login to SoCalGas, navigate to the hourly usage table,
    scrape the rows and return the most recent non-zero entry:
      - date (str): 'MM/DD/YYYY'
      - time (str): 'HH:MM AM/PM'
      - usage (float): Usage (Therms)
      - cost (float): Cost ($)
      - avg_temp (float): Avg. Temp (F)
      - timestamp (datetime)
    """

    # Prepare date range strings
    today = datetime.now()
    end   = today.strftime("%m/%d/%Y")

    async with async_playwright() as p:
        browser = await p.webkit.launch(headless=True)
        page = await browser.new_page()

        # 1. Log in
        await page.goto(LOGIN_URL)
        await page.fill("input[name='email']", username)
        await page.fill("input[name='password']", password)
        await page.click("button.primary.large[aria-label='Log In']")
        await page.wait_for_load_state("networkidle")

        # 2. Navigate to the usage page
        await page.wait_for_selector("button[aria-label='Analyze Usage']", state="visible", timeout=30000)
        await page.click("button[aria-label='Analyze Usage']")
        await page.wait_for_load_state("networkidle")

        # 3. Switch to Table + Hourly view inside the iframe
        await page.wait_for_selector("iframe[data-testid='sew-iframe']", timeout=30000)
        gb_frame = page.frame_locator("iframe[data-testid='sew-iframe']")

        # Click the "Table" view button
        await gb_frame.locator("a#table[title='Click to view  usage in Table']").wait_for(state="visible", timeout=30000)
        await gb_frame.locator("a#table").click()

        # Click the "Hourly" view button
        await gb_frame.locator("a#hourly[title='Click to view Hourly Usage data']").wait_for(state="visible", timeout=30000)
        await gb_frame.locator("a#hourly").click()

        # Wait for the hourly table to render
        await gb_frame.locator("table.MuiTable-root.tblhourly tbody tr").first.wait_for(state="visible", timeout=30000)

        # 4. Scrape all rows from the table
        rows = gb_frame.locator("table.MuiTable-root.tblhourly tbody tr")
        count = await rows.count()
        entries = []
        for i in range(count):
            row = rows.nth(i)
            cells = await row.locator("td").all_text_contents()
            # cells → [ time, cost, usage, avg_temp ]
            time_str, cost_str, usage_str, avg_temp_str = [c.strip() for c in cells]
            
            # Skip rows that aren't hourly times (e.g. date rows like "11/06/2025")
            if not re.match(r"^\d{1,2}:\d{2} [AP]M$", time_str):
                continue

            # Clean and convert values
            cost     = float(cost_str.replace("$", ""))
            usage    = float(usage_str)
            # Remove all non-digit and non-dot characters from the temperature string
            temp_num = re.sub(r"[^\d.]", "", avg_temp_str)
            avg_temp = float(temp_num) if temp_num else 0.0

            # Combine date and time into a timestamp
            timestamp = datetime.strptime(f"{end} {time_str}", "%m/%d/%Y %I:%M %p")

            entries.append({
                "date":     end,
                "time":     time_str,
                "usage":    usage,
                "cost":     cost,
                "avg_temp": avg_temp,
                "timestamp": timestamp
            })

        await browser.close()

    # 5. Compare against the system clock (always floored to the current hour)
    now = datetime.now()
    # Floor the time down to the top of the hour, e.g. 23:58 → 23:00
    ref_timestamp = now.replace(minute=0, second=0, microsecond=0)

    # Look for an entry whose timestamp exactly matches ref_timestamp
    # Note: each entry’s timestamp is constructed as today’s date + the hour
    match = next((e for e in entries if e["timestamp"] == ref_timestamp), None)

    if match:
        chosen = match
    else:
        # If no matching entry is found, return a “blank” record with zero values
        # but keep the timestamp set to ref_timestamp
        chosen = {
            "date":      ref_timestamp.strftime("%m/%d/%Y"),
            "time":      ref_timestamp.strftime("%I:%M %p"),
            "usage":     0.0,
            "cost":      0.0,
            "avg_temp":  0.0,
            "timestamp": ref_timestamp
        }

    return chosen
