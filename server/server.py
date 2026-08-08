from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import bigquery
from dotenv import load_dotenv
from pydantic import BaseModel
from google.oauth2 import service_account
import json
import os
import re
from datetime import datetime

# Security & Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load env vars from parent directory or local
load_dotenv()
load_dotenv("../.env") # Try loading from root if exists

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


app = FastAPI()

# Register agent router if available (import is optional)
try:
    # Importing the router is optional; fail gracefully if something goes wrong.
    from server.agent import router as agent_router
    app.include_router(agent_router.router, prefix="/api/agent")
except Exception as _e:
    print("Agent router not loaded (this is fine for Phase 1 until branch is merged):", _e)

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

# The rest of server routes remain unchanged and live in the original file in the main branch.
