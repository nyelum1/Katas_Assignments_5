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