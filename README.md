# SoCalGas Sync Home Assistant Integration

**Custom Home Assistant integration** to scrape **hourly** gas usage and cost from your SoCalGas account.

## Features

- **Two sensors**:
  - `sensor.socalgas_usage` → latest hourly consumption in **therms**
  - `sensor.socalgas_cost`  → corresponding cost in **$**
- Shared fetch logic via Home Assistant’s **DataUpdateCoordinator** (only one HTTP/Playwright fetch per interval)
- Fully configurable **update interval** in **minutes**
- Exposes helpful attributes on each sensor:
  - `date` (MM/DD/YYYY)
  - `time` (HH:MM AM/PM)
  - `avg_temp` (°F)
  - `timestamp` (full ISO timestamp)
- Ready to drop into the **Energy dashboard** (usage & cost)

---

## Prerequisites

Because this integration uses Playwright to drive a headless browser, you must ensure that **playwright** and the **Chromium** browser binary are installed in your HA Python environment.

### If you’re running Home Assistant in Docker

Create a custom Docker image by adding a `Dockerfile` next to your `configuration.yaml`:

```dockerfile
# Use the official Home Assistant image as base
ARG HA_IMAGE=ghcr.io/home-assistant/home-assistant:stable
FROM ${HA_IMAGE}

# Install Playwright Python bindings
RUN pip install playwright

# Install the Chromium browser binary for Playwright
RUN playwright install chromium
```

Then rebuild and launch your container:

```bash
docker build -t home-assistant-custom .
docker run -d \
  --name home-assistant \
  --restart=unless-stopped \
  -v /path/to/your/config:/config \
  home-assistant-custom
```

### If you’re on Home Assistant OS / Supervised

1. Install the **Terminal & SSH** add-on (or any add-on that gives you a shell).  
2. Open the shell and run:

   ```bash
   pip install playwright
   playwright install chromium
   ```

To install **WebKit** instead of Chromium, just replace the last command with:

```bash
playwright install webkit
```


## Installation

1. **Clone** or **download** this repository’s `custom_components/socalgas_sync/` folder into your Home Assistant `config/custom_components/` directory.
2. In HACS → **Integrations** → **⋯** (three-dots menu) → **Custom repositories**:
   - **URL**: `https://github.com/chenzhuo1005/socalgas_sync`
   - **Category**: Integration  
3. Install **SoCalGas Sync** and **restart** Home Assistant.

---

## Configuration

Add the following to your **`configuration.yaml`**:

```yaml
sensor:
  - platform: socalgas_sync
    username: YOUR_SOCALGAS_USERNAME
    password: YOUR_SOCALGAS_PASSWORD
    update_interval: 5   # minutes between fetches; defaults to 5 if omitted
```