import os
from typing import List, Optional
import re
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import bigquery
from dotenv import load_dotenv
from pydantic import BaseModel
from google.oauth2 import service_account
import json

# Security & Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load env vars from parent directory or local
load_dotenv()
load_dotenv("../.env") # Try loading from root if exists

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ... (omitted imports)

app = FastAPI()

# Rate Limiter Setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Mount static files if directory exists (for production/docker)
if os.path.exists("static"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

# Configure CORS (Secure)
# Production: Set FRONTEND_URL env var (e.g., "https://bergfex-dashboard.onrender.com")
frontend_url = os.getenv("FRONTEND_URL")
origins = [frontend_url] if frontend_url else ["*"]

if not frontend_url:
    print("WARNING: FRONTEND_URL not set. CORS is allowing all origins (*).")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (rest of code)



# Configuration
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "bergfex-481612")
DATASET_ID = os.getenv("BQ_DATASET_ID", "bergfex_data")
# Updated view with shred score
VIEW_ID = os.getenv("BQ_VIEW_ID", "vw_latest_snow_with_shred_score")

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
    # Updated SkiResort model with lat/lon
    altitude: dict
    url: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    # Shred Score Fields
    shredScore: Optional[float] = None
    scoreFreshness: Optional[float] = None
    scoreBaseSnow: Optional[float] = None
    scoreTerrain: Optional[float] = None
    scoreSnowFactor: Optional[float] = None
    scoreSlopeFactor: Optional[float] = None
    scoreCondition: Optional[float] = None
    scoreAvalanchePenalty: Optional[float] = None

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
    # Global stats (unaffected by filters)
    globalTotalCount: int
    globalOpenCount: int
    globalAvgSnowMountain: float
    globalTotalNewSnow: float
    globalTotalOpenKm: float
    # Available filter options
    availableCountries: List[str]
    availableRegions: dict  # {country: [region1, region2, ...]}"


@app.get("/api/resorts", response_model=ResortResponse)
@limiter.limit("60/minute") # Rate limit: 60 requests per minute per IP
async def get_resorts(request: fastapi.Request): # Request object needed for slowapi
    """
    Returns ALL resorts in one request. Filtering/sorting is done client-side for instant UX.
    """
    # Join with dim_resorts to get lat/lon
    query = f"""
        SELECT 
            v.*,
            d.lat,
            d.lon
        FROM `{PROJECT_ID}.{DATASET_ID}.{VIEW_ID}` v
        LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.dim_resorts` d ON v.resort_id = d.resort_id
    """
    
    try:
        query_job = client.query(query)
        rows = query_job.result()
        
        BASE_BERG_URL = "https://www.bergfex.at"
        
        all_resorts = []
        for i, row in enumerate(rows):
            snow_valley = parse_val(row.snow_valley_raw)
            snow_mountain = parse_val(row.snow_mountain_raw)
            new_snow = parse_val(row.new_snow_raw)
            
            mapped_country = map_country(row.country)
            avalanche_level, avalanche_text = map_avalanche(str(row.avalanche_warning) if row.avalanche_warning is not None else None)
            
            area_url = row.area_url or ""
            full_url = f"{BASE_BERG_URL}{area_url}" if area_url.startswith("/") else area_url
            
            slopes_open_km = float(parse_val(getattr(row, 'slopes_open_km_raw', 0)))
            
            all_resorts.append({
                "id": str(row.resort_id),
                "name": row.resort_name or "Unknown Resort",
                "region": getattr(row, 'region', None) or "Unbekannt",
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
                "lastUpdate": row.last_update.strftime("%Y-%m-%d %H:%M:%S") if row.scraped_at else "",
                "altitude": {
                    "min": parse_val(getattr(row, 'elevation_valley', 0)) or 0,
                    "max": parse_val(getattr(row, 'elevation_mountain', 0)) or 0
                },
                "url": full_url,
                "latitude": row.lat if getattr(row, 'lat', None) is not None else None,
                "longitude": row.lon if getattr(row, 'lon', None) is not None else None,
                # Shred Score Mappings (handle potential NULLs safely)
                "shredScore": float(row.shred_coefficient) if getattr(row, 'shred_coefficient', None) is not None else None,
                "scoreFreshness": float(row.freshness) if getattr(row, 'freshness', None) is not None else None,
                "scoreBaseSnow": float(row.base_snow) if getattr(row, 'base_snow', None) is not None else None,
                "scoreTerrain": float(row.terrain) if getattr(row, 'terrain', None) is not None else None,
                "scoreSnowFactor": float(row.snow_factor) if getattr(row, 'snow_factor', None) is not None else None,
                "scoreSlopeFactor": float(row.slope_factor) if getattr(row, 'slope_factor', None) is not None else None,
                "scoreCondition": float(row.conditions_factor) if getattr(row, 'conditions_factor', None) is not None else None,
                "scoreAvalanchePenalty": float(row.avalanche_penalty) if getattr(row, 'avalanche_penalty', None) is not None else None
            })

        # Calculate stats
        total_count = len(all_resorts)
        open_count = sum(1 for r in all_resorts if r["status"] in ["Geöffnet", "Teilweise geöffnet"])
        avg_snow_mountain = sum(r["snowMountain"] for r in all_resorts) / total_count if total_count > 0 else 0
        total_new_snow = sum(r["newSnow"] for r in all_resorts)
        total_open_km = sum(r["slopesOpenKm"] for r in all_resorts)

        # Top lists
        top_snow = sorted(all_resorts, key=lambda x: x["snowMountain"], reverse=True)[:5]
        top_new_snow = sorted(all_resorts, key=lambda x: x["newSnow"], reverse=True)[:5]
        
        # Avalanche distribution
        avalanche_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in all_resorts:
            lvl = r["avalancheWarning"]
            if 1 <= lvl <= 5:
                avalanche_dist[lvl] += 1

        # Build available countries and regions
        countries_set = set()
        regions_by_country = {}
        for r in all_resorts:
            c = r["country"]
            reg = r["region"]
            countries_set.add(c)
            if c not in regions_by_country:
                regions_by_country[c] = set()
            if reg and reg != "Unbekannt":
                regions_by_country[c].add(reg)
        
        available_countries = sorted(list(countries_set))
        available_regions = {c: sorted(list(regs)) for c, regs in regions_by_country.items()}
        
        return {
            "totalCount": total_count,
            "openCount": open_count,
            "avgSnowMountain": round(avg_snow_mountain),
            "totalNewSnow": total_new_snow,
            "totalOpenKm": round(total_open_km, 1),
            "avalancheDistribution": avalanche_dist,
            "resorts": all_resorts,  # Return ALL resorts
            "topSnowResorts": top_snow,
            "topNewSnowResorts": top_new_snow,
            # Global stats same as regular (no filtering on server now)
            "globalTotalCount": total_count,
            "globalOpenCount": open_count,
            "globalAvgSnowMountain": round(avg_snow_mountain),
            "globalTotalNewSnow": total_new_snow,
            "globalTotalOpenKm": round(total_open_km, 1),
            "availableCountries": available_countries,
            "availableRegions": available_regions
        }
        
    except Exception as e:
        print(f"Error fetching data: {e}") # Log internal detail
        # Return generic error to user to avoid leaking stack traces
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/resorts/{resort_id}/history")
@limiter.limit("60/minute")
async def get_resort_history(resort_id: str, request: fastapi.Request):
    """
    Fetch history for a specific resort.
    """

    # Table name for history view
    HISTORY_VIEW = "vw_resort_metrics_history"
    
    query = f"""
        SELECT 
            measurement_date,
            scraped_at,
            snow_mountain_cm,
            snow_valley_cm,
            new_snow_cm,
            lifts_open_count,
            lifts_total_count,
            slopes_open_km,
            slopes_total_km,
            shred_coefficient,
            raw_score,
            freshness,
            base_snow,
            terrain,
            conditions_factor,
            avalanche_penalty
        FROM `{PROJECT_ID}.{DATASET_ID}.{HISTORY_VIEW}`
        WHERE resort_id = @resort_id
        ORDER BY scraped_at ASC
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("resort_id", "STRING", str(resort_id))
        ]
    )

    try:
        query_job = client.query(query, job_config=job_config)
        rows = query_job.result()
        
        history = []
        for row in rows:
            history.append({
                "date": row.measurement_date.isoformat() if row.measurement_date else None,
                "timestamp": row.scraped_at.isoformat() if row.scraped_at else None,
                "snowMountain": float(row.snow_mountain_cm) if row.snow_mountain_cm is not None else 0,
                "snowValley": float(row.snow_valley_cm) if row.snow_valley_cm is not None else 0,
                "newSnow": float(row.new_snow_cm) if row.new_snow_cm is not None else 0,
                "liftsOpen": int(row.lifts_open_count) if row.lifts_open_count is not None else 0,
                "liftsTotal": int(row.lifts_total_count) if row.lifts_total_count is not None else 0,
                "slopesOpen": float(row.slopes_open_km) if row.slopes_open_km is not None else 0,
                "slopesTotal": float(row.slopes_total_km) if row.slopes_total_km is not None else 0,
                "shredScore": float(row.shred_coefficient) if row.shred_coefficient is not None else None,
                # Components
                "scoreFreshness": float(row.freshness) if row.freshness is not None else None,
                "scoreBaseSnow": float(row.base_snow) if row.base_snow is not None else None,
                "scoreTerrain": float(row.terrain) if row.terrain is not None else None,
                "scoreConditions": float(row.conditions_factor) if row.conditions_factor is not None else None,
                "scoreAvalanchePenalty": float(row.avalanche_penalty) if row.avalanche_penalty is not None else None
            })
            print(history)
        return history
        
    except Exception as e:
        print(f"Error fetching history for {resort_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Catch-all route for SPA (must be last)
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if full_path.startswith("api"):
        raise HTTPException(status_code=404, detail="Not Found")
    
    # Try to serve static file if it exists (e.g. favicon.ico, specific assets not in /assets)
    static_file_path = os.path.join("static", full_path)
    if os.path.exists("static") and os.path.isfile(static_file_path):
        return FileResponse(static_file_path)

    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    # In local dev without static build, just return 404 or handled by Vite proxy
    raise HTTPException(status_code=404, detail="Frontend not built/served")
