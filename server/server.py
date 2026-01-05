import os
from typing import List, Optional
import re
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import bigquery
from dotenv import load_dotenv
from pydantic import BaseModel
from google.oauth2 import service_account
import json

# Load env vars from parent directory or local
load_dotenv()
load_dotenv("../.env") # Try loading from root if exists

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ... (omitted imports)

app = FastAPI()

# Mount static files if directory exists (for production/docker)
if os.path.exists("static"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (rest of code)



# Configuration
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "bergfex-481612")
DATASET_ID = os.getenv("BQ_DATASET_ID", "bergfex_data")
TABLE_ID = os.getenv("BQ_TABLE_ID", "snow_reports")

# Initialize BigQuery Client
# Check for credentials JSON in env var (common for Render/Heroku)
credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
if credentials_json:
    try:
        credentials_info = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        client = bigquery.Client(project=PROJECT_ID, credentials=credentials)
        print("Initialized BigQuery client with credentials from env var.")
    except Exception as e:
        print(f"Failed to load credentials from env var: {e}")
        # Fallback to default (might fail if no other auth available)
        client = bigquery.Client(project=PROJECT_ID)
else:
    # Local dev or ADC
    client = bigquery.Client(project=PROJECT_ID)

class SkiResort(BaseModel):
    id: str
    name: str
    region: str
    country: str
    status: str
    snowValley: float
    snowMountain: float
    newSnow: float
    snowCondition: str
    lastSnowfall: str
    avalancheWarning: int
    avalancheText: str
    liftsOpen: int
    liftsTotal: int
    slopesOpenKm: float
    slopesTotalKm: float
    slopesOpen: int
    slopesTotal: int
    slopeCondition: str
    lastUpdate: str
    altitude: dict
    url: str

def parse_val(val):
    if val is None or val == "":
        return 0
    try:
        if isinstance(val, (int, float)):
            return val
        
        # Determine if it's a string
        s = str(val).strip()
        if not s: 
            return 0
            
        # Replace comma with dot
        s = s.replace(',', '.')
        
        # Extract number: match optional digits, dot, digits
        match = re.search(r'(\d+\.?\d*)', s)
        if match:
            # Check if original was int-like or float-like
            num = float(match.group(1))
            return int(num) if num.is_integer() else num
        return 0
    except:
        return 0

def map_country(country_name):
    if not country_name: return "AT"
    name = country_name.lower()
    if "österreich" in name: return "AT"
    if "deutschland" in name: return "DE"
    if "schweiz" in name: return "CH"
    if "italien" in name: return "IT"
    if "frankreich" in name: return "FR"
    if "slowenien" in name: return "SI"
    if "tschechien" in name: return "CZ"
    if "polen" in name: return "PL"
    if "slowakei" in name: return "SK"
    return "AT"

def map_status(status_val):
    if not status_val: return "Geschlossen"
    s = status_val.lower()
    if "open" in s: return "Geöffnet"
    if "closed" in s: return "Geschlossen"
    return "Teilweise geöffnet"

def map_avalanche(warning_str):
    """Map avalanche warning string to level (1-5) and text."""
    if not warning_str:
        return 0, "-"
    
    warning_str = warning_str.strip().lower()
    
    # Check for Roman numerals first (common in Bergfex)
    # Match "I", "II", "III", "IV", "V" followed by space or hyphen or end of string
    roman_map = {
        "i": 1,
        "ii": 2, 
        "iii": 3,
        "iv": 4, 
        "v": 5
    }
    
    # Split by space or hyphen to get the first part
    parts = re.split(r'[\s\-]+', warning_str)
    first_part = parts[0]
    
    level = 0
    if first_part in roman_map:
        level = roman_map[first_part]
    else:
        # Try to extract Arabic number
        match = re.search(r'(\d)', warning_str)
        if match:
            level = int(match.group(1))
            level = max(1, min(5, level))  # Clamp to 1-5
    
    # Map level to German text
    AVALANCHE_TEXT = {
        1: "Gering",
        2: "Mäßig",
        3: "Erheblich",
        4: "Groß",
        5: "Sehr groß"
    }
    text = AVALANCHE_TEXT.get(level, "-")
    
    return level, text

class ResortResponse(BaseModel):
    totalCount: int
    openCount: int
    avgSnowMountain: float
    totalNewSnow: float
    totalOpenKm: float
    resorts: List[SkiResort]
    topSnowResorts: List[SkiResort]
    topNewSnowResorts: List[SkiResort]
    avalancheDistribution: dict


@app.get("/api/resorts", response_model=ResortResponse)
async def get_resorts(
    sort: str = "slopesOpenKm",
    limit: int = 50,
    offset: int = 0
):
    # Use QUALIFY to get the latest snapshot for each resort (deduping within the same day)
    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        QUALIFY ROW_NUMBER() OVER (PARTITION BY resort_name ORDER BY scraped_at DESC) = 1
    """
    
    try:
        query_job = client.query(query)
        rows = query_job.result()
        
        BASE_BERG_URL = "https://www.bergfex.at"
        
        resorts = []
        for i, row in enumerate(rows):
            # Mapping fields from DB
            snow_valley = parse_val(row.snow_valley)
            snow_mountain = parse_val(row.snow_mountain)
            new_snow = parse_val(row.new_snow)
            
            mapped_country = map_country(row.country)
            avalanche_level, avalanche_text = map_avalanche(str(row.avalanche_warning) if row.avalanche_warning is not None else None)
            
            # Construct URL
            area_url = row.area_url or ""
            full_url = f"{BASE_BERG_URL}{area_url}" if area_url.startswith("/") else area_url
            
            slopes_open_km = float(parse_val(getattr(row, 'slopes_open_km', 0)))
            
            resorts.append({
                "id": str(i + 1),
                "name": row.resort_name or "Unknown Resort",
                "region": "Tirol", # Region is not yet consistently in DB
                "country": mapped_country,
                "status": map_status(row.status),
                "snowValley": float(snow_valley),
                "snowMountain": float(snow_mountain),
                "newSnow": float(new_snow),
                "snowCondition": row.snow_condition or "-",
                "lastSnowfall": row.last_snowfall or "-",
                "avalancheWarning": avalanche_level,
                "avalancheText": avalanche_text,
                "liftsOpen": row.lifts_open_count or 0,
                "liftsTotal": row.lifts_total_count or 0,
                "slopesOpenKm": slopes_open_km,
                "slopesTotalKm": float(parse_val(getattr(row, 'slopes_total_km', 0))),
                "slopesOpen": parse_val(getattr(row, 'slopes_open_count', 0)),
                "slopesTotal": parse_val(getattr(row, 'slopes_total_count', 0)),
                "slopeCondition": row.slope_condition or "-",
                "lastUpdate": row.scraped_at.strftime("%Y-%m-%d %H:%M:%S") if row.scraped_at else "",
                "altitude": {"min": 1000, "max": 2000}, # Placeholder
                "url": full_url
            })
            
        # Calculate totals before limiting
        total_count = len(resorts)
        open_count = sum(1 for r in resorts if r["status"] == "Geöffnet" or r["status"] == "Teilweise geöffnet")
        
        # Calculate Global Aggregates (regardless of filter/sort)
        if total_count > 0:
            avg_snow_mountain = sum(r["snowMountain"] for r in resorts) / total_count
        else:
            avg_snow_mountain = 0
            
        total_new_snow = sum(r["newSnow"] for r in resorts)
        total_open_km = sum(r["slopesOpenKm"] for r in resorts)

        # Get top lists for charts (from full dataset)
        top_snow = sorted(resorts, key=lambda x: x["snowMountain"], reverse=True)[:5]
        top_new_snow = sorted(resorts, key=lambda x: x["newSnow"], reverse=True)[:5]
        
        # Calculate Avalanche Distribution (Full Dataset)
        avalanche_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in resorts:
            lvl = r["avalancheWarning"]
            if 1 <= lvl <= 5:
                avalanche_dist[lvl] = avalanche_dist.get(lvl, 0) + 1

        # Determine sort key and reverse flag based on sort parameter
        # Default: slopesOpenKm desc
        key_func = lambda x: x["slopesOpenKm"]
        reverse = True
        
        if sort == "snowMountain":
            key_func = lambda x: x["snowMountain"]
            reverse = True
        elif sort == "newSnow":
            key_func = lambda x: x["newSnow"]
            reverse = True
        elif sort == "liftsOpen":
            key_func = lambda x: x["liftsOpen"]
            reverse = True
        elif sort == "name":
            key_func = lambda x: x["name"].lower()
            reverse = False # Alphabetical ascending
            
        resorts.sort(key=key_func, reverse=reverse)
        
        # Apply Pagination
        resorts_slice = resorts[offset : offset + limit]
        
        return {
            "totalCount": total_count,
            "openCount": open_count,
            "avgSnowMountain": round(avg_snow_mountain),
            "totalNewSnow": total_new_snow,
            "totalOpenKm": round(total_open_km, 1),
            "avalancheDistribution": avalanche_dist,
            "resorts": resorts_slice,
            "topSnowResorts": top_snow,
            "topNewSnowResorts": top_new_snow
        }
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Catch-all route for SPA (must be last)
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if full_path.startswith("api"):
        raise HTTPException(status_code=404, detail="Not Found")
    
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    # In local dev without static build, just return 404 or handled by Vite proxy
    raise HTTPException(status_code=404, detail="Frontend not built/served")
