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