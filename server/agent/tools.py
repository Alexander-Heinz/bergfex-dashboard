import json
import os
from typing import Any

from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account

# Load env vars (same pattern as server.py)
load_dotenv()
load_dotenv("../.env")

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "bergfex-481612")
DATASET_ID = os.getenv("BQ_DATASET_ID", "bergfex_data")
VIEW_ID = os.getenv("BQ_VIEW_ID", "vw_latest_snow_with_shred_score")

# Initialize BigQuery client (same logic as server.py to avoid importing it)
_credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
if _credentials_json:
    try:
        _cred_info = json.loads(_credentials_json)
        _credentials = service_account.Credentials.from_service_account_info(_cred_info)
        client = bigquery.Client(project=PROJECT_ID, credentials=_credentials)
    except (ValueError, TypeError, OSError) as _e:
        print(f"Agent tools: failed to load credentials from env var: {_e}")
        client = bigquery.Client(project=PROJECT_ID)
else:
    client = bigquery.Client(project=PROJECT_ID)


def _parse_val(val):
    """Parse a raw numeric string value, same helper as in server.py."""
    if val is None or val == "":
        return 0
    try:
        if isinstance(val, (int, float)):
            return val
        s = str(val).strip().replace(",", ".")
        if not s:
            return 0
        import re as _re

        match = _re.search(r"(\d+\.?\d*)", s)
        if match:
            num = float(match.group(1))
            return int(num) if num.is_integer() else num
        return 0
    except (ValueError, TypeError):
        return 0


# Hard cap for results to avoid expensive queries
MAX_LIMIT = 50


def _sanitize_limit(limit: int | None) -> int:
    if limit is None:
        return 10
    try:
        l = int(limit)
    except (TypeError, ValueError):
        l = 10
    if l <= 0:
        l = 10
    return min(l, MAX_LIMIT)


def query_ski_resorts(
    min_snow_depth: int = 0, limit: int | None = 10
) -> dict[str, Any]:
    """Controlled tool to query ski resorts from BigQuery.

    Parameters are explicit and constrained. The function constructs its
    own parametrized query and never executes LLM-provided SQL.
    """
    # Validate parameters
    try:
        min_snow_depth = int(min_snow_depth)
    except (TypeError, ValueError):
        raise ValueError("min_snow_depth must be an integer")

    limit = _sanitize_limit(limit)

    # We use REGEXP_EXTRACT to pull numeric parts from the raw column used in
    # the existing codebase (snow_mountain_raw). This keeps the SQL deterministic
    # and avoids executing arbitrary SQL from the LLM.
    query = f"""
    SELECT
      v.resort_id,
      v.resort_name,
      v.snow_mountain_raw,
      v.new_snow_raw,
      d.lat,
      d.lon
    FROM `{PROJECT_ID}.{DATASET_ID}.{VIEW_ID}` v
    LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.dim_resorts` d
      ON v.resort_id = d.resort_id
    WHERE SAFE_CAST(REGEXP_EXTRACT(COALESCE(v.snow_mountain_raw, ''), r'(\\d+\\.?\\d*)') AS FLOAT64) >= @min_snow_depth
    LIMIT {limit}
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "min_snow_depth", "INT64", int(min_snow_depth)
            )
        ]
    )

    query_job = client.query(query, job_config=job_config)
    rows = query_job.result()

    resorts = []
    for row in rows:
        snow_mountain = _parse_val(getattr(row, "snow_mountain_raw", None))
        snow_valley = _parse_val(getattr(row, "snow_valley_raw", None))
        new_snow = _parse_val(getattr(row, "new_snow_raw", None))
        resorts.append(
            {
                "id": str(row.resort_id),
                "name": row.resort_name or "Unknown",
                "snowMountain": float(snow_mountain),
                "snowValley": float(snow_valley),
                "newSnow": float(new_snow),
                "latitude": getattr(row, "lat", None),
                "longitude": getattr(row, "lon", None),
            }
        )

    return {
        "total": len(resorts),
        "resorts": resorts,
        "min_snow_depth": min_snow_depth,
        "limit": limit,
    }
