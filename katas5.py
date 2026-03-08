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
    

    def run_pipeline():
    """Main driver function to coordinate the threading and saving."""
    final_results = []
    
    print(f"Starting fetch for {len(SERIES_IDS)} series...")

    with ThreadPoolExecutor(max_workers=CONFIG["max_threads"]) as executor:
        # Submit tasks
        tasks = {executor.submit(fetch_series, s_id): s_id for s_id in SERIES_IDS}

        # Collect results as they finish
        for future in as_completed(tasks):
            res = future.result()
            if res["success"]:
                final_results.append(res)
                print(f"✔ Done: {res['series_id']}")
            else:
                print(f"✘ Fail: {res['series_id']} (logged to {CONFIG['error_log']})")

    # Save all successful results to one file
    with open(CONFIG["output_file"], "w") as f:
        json.dump(final_results, f, indent=4)
    
    print(f"\nFinished! Processed {len(final_results)} series successfully.")