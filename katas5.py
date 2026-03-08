import requests
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- CONFIGURATION ---
CONFIG = {
    "url": "https://api.bls.gov/publicAPI/v1/timeseries/data/",
    "max_threads": 4,
    "timeout": 15,
    "output_file": "combined_results.json",
    "error_log": "errors.log"
}

SERIES_IDS = ["JTS540000000000000QUR", "JTS540000000000000JOR", "JTS540000000000000HIR"]


# Shared resource lock for thread-safe writing
log_lock = threading.Lock()

def fetch_series(series_id):
    """Worker function to fetch data for a single series."""
    payload = {
        "seriesid": [series_id],
        "startyear": "2025",
        "endyear": "2026"
    }
    
    try:
        response = requests.post(CONFIG["url"], json=payload, timeout=CONFIG["timeout"])
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "REQUEST_SUCCEEDED":
            raise Exception(f"API Alert: {data.get('message')}")

        return {"series_id": series_id, "data": data, "success": True}

    except Exception as e:
        # Thread-safe logging to the error file
        with log_lock:
            with open(CONFIG["error_log"], "a") as f:
                f.write(f"Failed {series_id}: {str(e)}\n")
        return {"series_id": series_id, "error": str(e), "success": False}