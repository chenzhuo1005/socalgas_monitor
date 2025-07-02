# main.py
import os
import asyncio
from getpass import getpass
from datetime import datetime
from custom_components.socalgas_sync.playwright_grabber import fetch_therms

async def main():
    # 1. Read credentials (env vars fall back to prompt)
    username = os.getenv("SOCALGAS_USER") or input("SoCalGas Username: ")
    password = os.getenv("SOCALGAS_PASS") or getpass("SoCalGas Password: ")

    try:
        # 2. Fetch the data
        result = await fetch_therms(username, password)

        # 3. Unpack and display
        if isinstance(result, dict):
            date      = result["date"]
            time      = result["time"]
            usage     = result["usage"]
            cost      = result["cost"]
            avg_temp  = result["avg_temp"]
            timestamp = result["timestamp"]
            print(f"Date:            {date}")
            print(f"Time:            {time}")
            print(f"Usage (Therms):  {usage}")
            print(f"Cost ($):        {cost}")
            print(f"Avg Temp (F):    {avg_temp}")
            print(f"Parsed TS:       {timestamp}")
        else:
            # fallback if fetch_therms returns a tuple
            usage, timestamp = result
            print(f"Usage (Therms): {usage}")
            print(f"Timestamp:      {timestamp}")
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    asyncio.run(main())
