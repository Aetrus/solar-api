"""
SolarMetric API - A Micro-SaaS for Solar Energy Potential Analysis

This API provides instant solar irradiance data and financial ROI estimates
for any US address by leveraging NREL PVWatts and US Census Bureau data.
"""

import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
# The API key is pulled from the environment variables for security.
# If not found, it defaults to 'DEMO_KEY' which has very low rate limits.
NREL_API_KEY = os.environ.get("NREL_API_KEY", "DEMO_KEY")

# --- HELPER FUNCTIONS ---

def get_coordinates(address):
    """
    Step 1: Geocoding
    Takes a text address (e.g., "1600 Pennsylvania Ave") and asks the
    US Census Bureau for the Latitude and Longitude.
    Source: https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html
    """
    base_url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
    params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "format": "json"
    }
    try:
        # We use a User-Agent to identify ourselves politely to the Census API
        headers = {'User-Agent': 'SolarMetric-API/1.0'}
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        data = response.json()
        
        # Parse the nested JSON response to find coordinates
        matches = data.get("result", {}).get("addressMatches", [])
        if matches:
            coords = matches[0].get("coordinates", {})
            return coords.get("y"), coords.get("x")  # Returns Lat, Lon
        return None, None
    except Exception as e:
        print(f"Geocoding Error: {e}")
        return None, None


def get_solar_data(lat, lon):
    """
    Step 2: Solar Irradiance Query
    Takes Lat/Lon and asks NREL PVWatts V8 for energy data.
    We inject standard defaults for a typical residential roof.
    Source: https://developer.nrel.gov/docs/solar/pvwatts/v8/
    """
    base_url = "https://developer.nrel.gov/api/pvwatts/v8.json"
    params = {
        "api_key": NREL_API_KEY,
        "lat": lat,
        "lon": lon,
        "system_capacity": 5,     # Standard 5kW residential system
        "azimuth": 180,           # Facing South (Optimal in Northern Hemisphere)
        "tilt": 20,               # Standard roof pitch
        "array_type": 1,          # Fixed (Roof Mounted)
        "module_type": 0,         # Standard Panel
        "losses": 14              # Standard system losses (dust, wiring)
    }
    try:
        response = requests.get(base_url, params=params, timeout=30)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


# --- API ENDPOINTS ---

@app.route('/api/v1/solar-estimate', methods=['GET'])
def solar_estimate():
    """
    Main endpoint: Get solar potential and financial estimates for a US address.
    
    Query Parameters:
        address (str, required): A valid US street address
        
    Returns:
        JSON with solar potential and financial estimates
    """
    # 1. Get Address from Query String
    address = request.args.get('address')
    
    if not address:
        return jsonify({
            "status": "error",
            "message": "Missing required parameter: address"
        }), 400

    # 2. Convert Address to Coordinates
    lat, lon = get_coordinates(address)
    if not lat:
        return jsonify({
            "status": "error",
            "message": "Could not locate address. Ensure it is a valid US address."
        }), 404

    # 3. Fetch Solar Data from NREL
    solar_data = get_solar_data(lat, lon)
    
    # Check for NREL errors (e.g., outside coverage area)
    if "errors" in solar_data and solar_data["errors"]:
        return jsonify({
            "status": "error", 
            "message": "NREL Data Unavailable", 
            "details": solar_data["errors"]
        }), 500

    # 4. Process Data & Calculate Financials
    outputs = solar_data.get("outputs", {})
    ac_annual = outputs.get("ac_annual", 0)  # Total kWh per year
    solrad_annual = outputs.get("solrad_annual", 0)  # Daily solar radiation (kWh/m2/day)
    
    # Financial Model:
    # We use a conservative US average of $0.16/kWh. 
    # In future versions, this could be dynamic based on state.
    estimated_rate = 0.16
    annual_savings = ac_annual * estimated_rate
    monthly_savings = annual_savings / 12

    # 5. Construct the Value-Added Response
    response_payload = {
        "status": "success",
        "input_address": address,
        "derived_location": {
            "latitude": lat,
            "longitude": lon
        },
        "solar_potential": {
            "suitability": "Excellent" if solrad_annual > 4.5 else "Moderate" if solrad_annual > 3.5 else "Low",
            "daily_sun_hours": round(solrad_annual, 2),
            "annual_energy_production_kwh": round(ac_annual, 0),
            "system_spec": "5kW Residential System (South Facing)"
        },
        "financial_estimate": {
            "estimated_annual_savings_usd": round(annual_savings, 2),
            "estimated_monthly_savings_usd": round(monthly_savings, 2),
            "electricity_rate_assumed": f"${estimated_rate}/kWh"
        },
        "disclaimer": "Estimates are based on NREL data and standard assumptions. Actual savings vary."
    }

    return jsonify(response_payload)


# Health Check Endpoint (Required by Render)
@app.route('/', methods=['GET'])
def home():
    """Health check endpoint for monitoring and Render deployment."""
    return jsonify({
        "service": "SolarMetric API",
        "status": "Operational",
        "version": "1.0.0",
        "docs": "/api/v1/solar-estimate?address=<US_ADDRESS>"
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
