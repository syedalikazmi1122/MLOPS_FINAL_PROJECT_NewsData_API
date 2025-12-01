#!/usr/bin/env python3
"""
Download historical earthquake data from USGS in 2-year intervals,
save raw GeoJSON + NDJSON + compressed formats.

This version includes:
- Interval-based fetching (2-year chunks) to avoid timeouts
- Minimum magnitude filter (default: 3.0) to get meaningful earthquakes
- Proper User-Agent (USGS rejects default python-requests)
- Streaming download (avoids server overload)
- Robust retry with exponential backoff
- Per-interval error handling with continuation
- Timestamped files for each interval
- Optional aggregation into master dataset

Usage:
    python etl/download_historical.py --out-dir data/raw --start-year 2018 --end-year 2020
    python etl/download_historical.py --out-dir data/raw --start-year 2018 --end-year 2020 --combine
    python etl/download_historical.py --out-dir data/raw --minmagnitude 4.0  # Only magnitude 4.0+
"""

import argparse
import json
import os
import gzip
import platform
import time
from datetime import datetime, timedelta
from typing import List, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


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
    # Use platform detection for cross-platform compatibility
    os_name = platform.system()
    os_version = platform.release()
    user_agent = f"Mozilla/5.0 (EarthquakeForecastProject; {os_name} {os_version})"
    
    session.headers.update({
        "User-Agent": user_agent,
        "Accept": "application/json",
        "Connection": "keep-alive",
    })

    return session


def generate_date_intervals(start_year: int, end_year: int, interval_years: int = 2) -> List[Tuple[str, str]]:
    """
    Generate date intervals for fetching data in chunks.
    
    Args:
        start_year: Starting year (e.g., 2010)
        end_year: Ending year (e.g., 2020)
        interval_years: Number of years per interval (default: 2)
    
    Returns:
        List of (start_date, end_date) tuples in YYYY-MM-DD format
    """
    intervals = []
    current_start = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31, 23, 59, 59)
    
    while current_start < end_date:
        # Calculate end date for this interval
        interval_end = current_start + timedelta(days=365 * interval_years) - timedelta(seconds=1)
        current_end = min(interval_end, end_date)
        
        # Only add interval if it spans at least 1 day
        if (current_end - current_start).days >= 1:
            intervals.append((
                current_start.strftime("%Y-%m-%d"),
                current_end.strftime("%Y-%m-%d")
            ))
        
        # Move to next interval (start of next day)
        current_start = current_end + timedelta(seconds=1)
        # If we're at the end date, break
        if current_start > end_date:
            break
    
    return intervals


def build_url(start_date: str, end_date: str, minmagnitude: float = 3.0) -> str:
    """Build USGS API URL for a date range with minimum magnitude filter."""
    return f"{BASE_URL}?format=geojson&starttime={start_date}&endtime={end_date}&minmagnitude={minmagnitude}"


def save_ndjson(geojson, out_file, mode='wt'):
    """Save GeoJSON features as compressed NDJSON."""
    with gzip.open(out_file, mode, encoding="utf-8") as f:
        for feat in geojson.get("features", []):
            f.write(json.dumps(feat) + "\n")


def fetch_interval(session, start_date: str, end_date: str, minmagnitude: float = 3.0, retry_delay: float = 2.0) -> dict:
    """
    Fetch earthquake data for a single date interval.
    
    Args:
        session: requests.Session with retry logic
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        minmagnitude: Minimum magnitude filter (default: 3.0)
        retry_delay: Delay between retries in seconds
    
    Returns:
        GeoJSON FeatureCollection dict
    """
    url = build_url(start_date, end_date, minmagnitude)
    print(f"  Fetching {start_date} to {end_date} (min magnitude: {minmagnitude})...")
    
    try:
        r = session.get(url, stream=True, timeout=60)
        
        if r.status_code != 200:
            error_msg = f"HTTP {r.status_code}: {r.text[:200]}"
            print(f"  ERROR: {error_msg}")
            raise requests.exceptions.HTTPError(f"USGS returned {r.status_code}")
        
        data = r.json()
        feature_count = len(data.get("features", []))
        print(f"  ✓ Retrieved {feature_count} earthquakes")
        
        # Rate limiting: be polite to the API
        time.sleep(retry_delay)
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"  ERROR fetching {start_date} to {end_date}: {e}")
        raise


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

def main(out_dir, start_year=2010, end_year=2020, interval_years=2, minmagnitude=3.0, use_mock=False, combine=False):
    """
    Download earthquake data in intervals and optionally combine.
    
    Args:
        out_dir: Output directory for raw data
        start_year: Starting year
        end_year: Ending year
        interval_years: Years per fetch interval
        minmagnitude: Minimum magnitude filter (default: 3.0)
        use_mock: Use mock data instead of API
        combine: Combine all intervals into master files
    """
    ensure_dir(out_dir)
    
    # --- MOCK MODE ---
    if use_mock:
        print("[download_historical] Using mock dataset (offline mode)")
        data = _create_mock_data()
        
        geojson_path = os.path.join(out_dir, "historical_mock.geojson")
        ndjson_path = os.path.join(out_dir, "historical_mock.ndjson.gz")
        
        print(f"[download_historical] Saving {geojson_path}")
        with open(geojson_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        
        print(f"[download_historical] Saving NDJSON {ndjson_path}")
        save_ndjson(data, ndjson_path)
        print("[download_historical] Done.")
        return

    # Generate intervals
    intervals = generate_date_intervals(start_year, end_year, interval_years)
    print(f"[download_historical] Fetching data in {len(intervals)} intervals ({interval_years} years each)")
    print(f"[download_historical] Date range: {start_year}-01-01 to {end_year}-12-31")
    
    session = _make_session(retries=3, backoff_factor=1.5)
    
    all_features = []
    successful_intervals = []
    failed_intervals = []
    
    # Fetch each interval
    for i, (start_date, end_date) in enumerate(intervals, 1):
        print(f"\n[{i}/{len(intervals)}] Interval: {start_date} to {end_date}")
        
        try:
            data = fetch_interval(session, start_date, end_date, minmagnitude=minmagnitude, retry_delay=1.5)
            
            # Save individual interval files
            interval_suffix = f"{start_date}_{end_date}"
            geojson_path = os.path.join(out_dir, f"earthquakes_{interval_suffix}.geojson")
            ndjson_path = os.path.join(out_dir, f"earthquakes_{interval_suffix}.ndjson.gz")
            
            print(f"  Saving {geojson_path}")
            with open(geojson_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            
            print(f"  Saving {ndjson_path}")
            save_ndjson(data, ndjson_path)
            
            # Collect features for combination
            if combine:
                all_features.extend(data.get("features", []))
            
            successful_intervals.append((start_date, end_date, len(data.get("features", []))))
            
        except Exception as e:
            print(f"  ✗ Failed to fetch interval {start_date} to {end_date}: {e}")
            failed_intervals.append((start_date, end_date, str(e)))
            # Continue with next interval instead of failing completely
            continue
    
    # Summary
    print("\n" + "="*60)
    print("[download_historical] Download Summary")
    print("="*60)
    print(f"Successful intervals: {len(successful_intervals)}/{len(intervals)}")
    if successful_intervals:
        total_earthquakes = sum(count for _, _, count in successful_intervals)
        print(f"Total earthquakes retrieved: {total_earthquakes:,}")
    
    if failed_intervals:
        print(f"\nFailed intervals: {len(failed_intervals)}")
        for start, end, error in failed_intervals:
            print(f"  - {start} to {end}: {error}")
    
    # Combine all intervals if requested
    if combine and all_features:
        print("\n[download_historical] Combining all intervals...")
        combined_data = {
            "type": "FeatureCollection",
            "features": all_features,
            "metadata": {
                "total_features": len(all_features),
                "date_range": f"{start_year}-01-01 to {end_year}-12-31",
                "intervals_combined": len(successful_intervals),
                "collection_timestamp": datetime.now().isoformat()
            }
        }
        
        geojson_path = os.path.join(out_dir, "earthquakes_combined.geojson")
        ndjson_path = os.path.join(out_dir, "earthquakes_combined.ndjson.gz")
        
        print(f"  Saving combined dataset: {geojson_path}")
        with open(geojson_path, "w", encoding="utf-8") as f:
            json.dump(combined_data, f)
        
        print(f"  Saving combined NDJSON: {ndjson_path}")
        save_ndjson(combined_data, ndjson_path)
        print(f"  ✓ Combined {len(all_features):,} earthquakes into master dataset")
    
    print("\n[download_historical] Done.")


# -----------------------------------------------------
# CLI
# -----------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download USGS earthquake data in intervals"
    )
    parser.add_argument(
        "--out-dir",
        default="data/raw",
        help="Output directory for raw data files"
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=2018,
        help="Starting year (default: 2018)"
    )
    parser.add_argument(
        "--end-year",
        type=int,
        default=2020,
        help="Ending year (default: 2020)"
    )
    parser.add_argument(
        "--interval-years",
        type=int,
        default=2,
        help="Years per fetch interval (default: 2)"
    )
    parser.add_argument(
        "--minmagnitude",
        type=float,
        default=3.0,
        help="Minimum magnitude filter (default: 3.0)"
    )
    parser.add_argument(
        "--combine",
        action="store_true",
        help="Combine all intervals into master dataset files"
    )
    parser.add_argument(
        "--use-mock",
        action="store_true",
        help="Use mock data only (for testing)"
    )
    
    args = parser.parse_args()
    
    main(
        args.out_dir,
        start_year=args.start_year,
        end_year=args.end_year,
        interval_years=args.interval_years,
        minmagnitude=args.minmagnitude,
        use_mock=args.use_mock,
        combine=args.combine
    )
