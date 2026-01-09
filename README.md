# SolarMetric API

A **Micro-SaaS API** that provides instant solar irradiance data and financial ROI estimates for any US address. Built on NREL PVWatts and US Census Bureau data.

## Features

- 🏠 **Address-based queries** - No need for lat/lon coordinates
- ☀️ **Solar potential analysis** - Daily sun hours, annual energy production
- 💰 **Financial estimates** - Projected annual/monthly savings
- 🚀 **Simple REST API** - One endpoint, JSON response
- 🔒 **Free data sources** - NREL & Census Bureau (public domain)

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/solar-api.git
   cd solar-api
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your NREL API key
   ```

4. **Run the server**
   ```bash
   python main.py
   ```

5. **Test the API**
   ```bash
   # Health check
   curl http://localhost:5000/

   # Get solar estimate
   curl "http://localhost:5000/api/v1/solar-estimate?address=1600+Pennsylvania+Ave+NW,+Washington,+DC"
   ```

## API Reference

### `GET /api/v1/solar-estimate`

Get solar potential and financial estimates for a US address.

**Query Parameters:**
| Parameter | Type   | Required | Description           |
|-----------|--------|----------|-----------------------|
| address   | string | Yes      | Valid US street address |

**Example Response:**
```json
{
  "status": "success",
  "input_address": "1600 Pennsylvania Ave NW, Washington, DC",
  "derived_location": {
    "latitude": 38.8976763,
    "longitude": -77.0365298
  },
  "solar_potential": {
    "suitability": "Excellent",
    "daily_sun_hours": 4.52,
    "annual_energy_production_kwh": 6234,
    "system_spec": "5kW Residential System (South Facing)"
  },
  "financial_estimate": {
    "estimated_annual_savings_usd": 997.44,
    "estimated_monthly_savings_usd": 83.12,
    "electricity_rate_assumed": "$0.16/kWh"
  },
  "disclaimer": "Estimates are based on NREL data and standard assumptions. Actual savings vary."
}
```

## Deployment Guide

### Deploy to Render

1. **Push to GitHub** - Upload all project files to a new repository

2. **Create Render Web Service**
   - Go to [render.com](https://render.com) and create a new "Web Service"
   - Connect your GitHub repository
   - Set these options:
     - **Runtime:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn main:app`

3. **Add Environment Variable**
   - Key: `NREL_API_KEY`
   - Value: Your NREL API key from [developer.nrel.gov](https://developer.nrel.gov/signup/)

4. **Deploy** - Render will build and deploy automatically

### List on RapidAPI

1. Go to [RapidAPI Provider Dashboard](https://rapidapi.com/developer/dashboard)
2. Create a new API with your Render URL as the base
3. Set up pricing tiers:
   - **Basic (Free):** 50 requests/month
   - **Pro ($29/mo):** 5,000 requests/month
   - **Ultra ($99/mo):** 50,000 requests/month
   - **Mega ($499/mo):** Unlimited

## Environment Variables

| Variable      | Required | Default   | Description                    |
|---------------|----------|-----------|--------------------------------|
| NREL_API_KEY  | Yes*     | DEMO_KEY  | NREL API key for solar data   |

*DEMO_KEY works but has strict rate limits. Get a free key at [developer.nrel.gov](https://developer.nrel.gov/signup/)

## Tech Stack

- **Framework:** Flask 3.0
- **Server:** Gunicorn
- **Data Sources:**
  - [NREL PVWatts V8](https://developer.nrel.gov/docs/solar/pvwatts/v8/)
  - [US Census Bureau Geocoder](https://geocoding.geo.census.gov/)

## License

MIT License - Feel free to use commercially.

---

Built following the Data Arbitrage model: aggregating free public data, adding value through simplification, and reselling via API marketplace.
