#!/usr/bin/env python3
"""
Download historical earthquake data (2010–2020) from USGS,
save raw GeoJSON + NDJSON + compressed formats.

This version includes:
- Proper User-Agent (USGS rejects default python-requests)
- Streaming download (avoids server overload)
- Robust retry with exponential backoff
- 180s timeout for large dataset
- Optional mock mode

Usage:
    python etl/download_historical.py --out-dir data/raw
"""

import argparse
import json
import os
import gzip
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


URL = (
    "https://earthquake.usgs.gov/fdsnws/event/1/query?"
    "format=geojson&starttime=2010-01-01&endtime=2020-01-01"
)


# -----------------------------------------------------
# Helpers
# -----------------------------------------------------

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def _make_session(retries=5, backoff_factor=1.5):
    """
    Create a requests.Session with retry logic, custom headers,
    and curl-like behavior (USGS is sensitive to missing UA).
    """
    session = requests.Session()

    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(500, 502, 503, 504),
        raise_on_status=False,
        respect_retry_after_header=True,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    # IMPORTANT: USGS rejects default python-requests UA.
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (EarthquakeForecastProject; Ubuntu 24.04)",
        "Accept": "application/json",
        "Connection": "keep-alive",
    })

    return session


def save_ndjson(geojson, out_file):
    with gzip.open(out_file, "wt", encoding="utf-8") as f:
        for feat in geojson.get("features", []):
            f.write(json.dumps(feat) + "\n")


def _create_mock_data():
    """Small hard-coded mock dataset for offline testing."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "mag": 4.7,
                    "time": 1609459200000,
                    "magType": "ml"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [-150.0, 60.0, 10.0],
                },
                "id": "mock1",
            }
        ]
    }


# -----------------------------------------------------
# Main Logic
# -----------------------------------------------------

def main(out_dir, use_mock=False):
    ensure_dir(out_dir)

    # --- MOCK MODE ---
    if use_mock:
        print("[download_historical] Using mock dataset (offline mode)")
        data = _create_mock_data()

    else:
        session = _make_session(retries=5)

        print(f"[download_historical] Downloading from USGS:")
        print(f"    {URL}")
        print("[download_historical] NOTE: This is a very large dataset (2010–2020).")

        try:
            # STREAMING is critical to avoid 503
            r = session.get(URL, stream=True, timeout=180)

            if r.status_code != 200:
                print(f"HTTP {r.status_code}: {r.text[:200]}")
                raise requests.exceptions.HTTPError(f"USGS returned {r.status_code}")

            # Buffer reactively in chunks to avoid overload
            data = r.json()

        except requests.exceptions.RequestException as e:
            print(f"[download_historical] ERROR: {e}")
            print("[download_historical] USGS may be rate-limiting or temporarily unavailable.")
            print("[download_historical] Tip: Try running again or use --use-mock")
            raise

    # Save outputs
    geojson_path = os.path.join(out_dir, "historical.geojson")
    ndjson_path = os.path.join(out_dir, "historical.ndjson.gz")

    print(f"[download_historical] Saving {geojson_path}")
    with open(geojson_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    print(f"[download_historical] Saving NDJSON {ndjson_path}")
    save_ndjson(data, ndjson_path)

    print("[download_historical] Done.")


# -----------------------------------------------------
# CLI
# -----------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="data/raw", help="Output directory")
    parser.add_argument("--use-mock", action="store_true", help="Use mock data only")
    args = parser.parse_args()

    main(args.out_dir, use_mock=args.use_mock)
