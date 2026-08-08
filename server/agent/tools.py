from typing import List, Dict, Any, Optional
from google.cloud import bigquery
from server import server as server_mod
from server.server import client, PROJECT_ID, DATASET_ID, VIEW_ID
from server.server import parse_val
import re

# Hard cap for results to avoid expensive queries
MAX_LIMIT = 50


def _sanitize_limit(limit: Optional[int]) -> int:
    if limit is None:
        return 10
    try:
        l = int(limit)
    except Exception:
        l = 10
    if l <= 0:
        l = 10
    return min(l, MAX_LIMIT)


def query_ski_resorts(min_snow_depth: int = 0, limit: Optional[int] = 10) -> Dict[str, Any]:
    """Controlled tool to query ski resorts from BigQuery.

    Parameters are explicit and constrained. The function constructs its
    own parametrized query and never executes LLM-provided SQL.
    """
    # Validate parameters
    try:
        min_snow_depth = int(min_snow_depth)
    except Exception:
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
            bigquery.ScalarQueryParameter("min_snow_depth", "INT64", int(min_snow_depth))
        ]
    )

    query_job = client.query(query, job_config=job_config)
    rows = query_job.result()

    resorts = []
    for row in rows:
        snow_mountain = parse_val(getattr(row, 'snow_mountain_raw', None))
        snow_valley = parse_val(getattr(row, 'snow_valley_raw', None))
        new_snow = parse_val(getattr(row, 'new_snow_raw', None))
        resorts.append({
            "id": str(row.resort_id),
            "name": row.resort_name or "Unknown",
            "snowMountain": float(snow_mountain),
            "snowValley": float(snow_valley),
            "newSnow": float(new_snow),
            "latitude": getattr(row, 'lat', None),
            "longitude": getattr(row, 'lon', None),
        })

    return {
        "total": len(resorts),
        "resorts": resorts,
        "min_snow_depth": min_snow_depth,
        "limit": limit,
    }
