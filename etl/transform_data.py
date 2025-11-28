#!/usr/bin/env python3
"""
Transform raw earthquake GeoJSON data into formatted DataFrame for model training.

This script:
- Extracts features from GeoJSON format
- Creates time-series features (hour, day, month, etc.)
- Creates lag features (time since last earthquake, rolling statistics)
- Formats data for time-series prediction tasks

Usage:
    python etl/transform_data.py --input data/raw/earthquakes_combined.geojson --output data/processed/earthquakes_processed.parquet
"""

import argparse
import json
import os
from datetime import datetime
from typing import Optional
import pandas as pd
import numpy as np


def load_geojson(file_path: str) -> pd.DataFrame:
    """
    Load GeoJSON file and convert to DataFrame.
    
    Args:
        file_path: Path to GeoJSON file
    
    Returns:
        DataFrame with earthquake data
    """
    print(f"[transform_data] Loading {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    features = data.get('features', [])
    if not features:
        raise ValueError(f"No features found in {file_path}")
    
    print(f"[transform_data] Found {len(features)} earthquakes")
    
    # Extract data from GeoJSON features
    records = []
    for feat in features:
        props = feat.get('properties', {})
        geom = feat.get('geometry', {})
        coords = geom.get('coordinates', [])
        
        record = {
            'id': feat.get('id', ''),
            'magnitude': props.get('mag'),
            'time': props.get('time'),  # Unix timestamp in milliseconds
            'place': props.get('place', ''),
            'longitude': coords[0] if len(coords) > 0 else None,
            'latitude': coords[1] if len(coords) > 1 else None,
            'depth': coords[2] if len(coords) > 2 else None,
            'mag_type': props.get('magType', ''),
            'event_type': props.get('type', ''),
            'status': props.get('status', ''),
            'tsunami': props.get('tsunami', 0),
            'significance': props.get('sig', None),
            'gap': props.get('gap', None),
            'dmin': props.get('dmin', None),
            'rms': props.get('rms', None),
            'nst': props.get('nst', None),
        }
        records.append(record)
    
    df = pd.DataFrame(records)
    print(f"[transform_data] Created DataFrame with {len(df)} rows, {len(df.columns)} columns")
    
    return df


def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create time-based features from timestamp.
    
    Args:
        df: DataFrame with 'time' column (Unix milliseconds)
    
    Returns:
        DataFrame with additional time features
    """
    print("[transform_data] Creating time-based features...")
    
    # Convert timestamp to datetime
    df['datetime'] = pd.to_datetime(df['time'], unit='ms')
    
    # Extract time components
    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month
    df['day'] = df['datetime'].dt.day
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.dayofweek  # 0=Monday, 6=Sunday
    df['day_of_year'] = df['datetime'].dt.dayofyear
    df['week_of_year'] = df['datetime'].dt.isocalendar().week
    
    # Cyclical encoding for periodic features
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    
    return df


def create_lag_features(df: pd.DataFrame, sort_by_time: bool = True) -> pd.DataFrame:
    """
    Create lag features for time-series prediction.
    
    Args:
        df: DataFrame with earthquake data
        sort_by_time: Whether to sort by time before creating lags
    
    Returns:
        DataFrame with lag features
    """
    print("[transform_data] Creating lag features...")
    
    if sort_by_time:
        df = df.sort_values('datetime').reset_index(drop=True)
    
    # Set datetime as index for rolling operations
    df_indexed = df.set_index('datetime')
    
    # Time since last earthquake (in hours)
    df['time_since_last'] = df['datetime'].diff().dt.total_seconds() / 3600
    df['time_since_last'] = df['time_since_last'].fillna(0)
    
    # Lag features for magnitude
    df['mag_lag1'] = df['magnitude'].shift(1)
    df['mag_lag2'] = df['magnitude'].shift(2)
    df['mag_lag3'] = df['magnitude'].shift(3)
    
    # Rolling statistics (last 24 hours, 7 days, 30 days)
    # Using indexed dataframe for time-based rolling
    df['mag_rolling_24h'] = df_indexed['magnitude'].rolling(
        window=pd.Timedelta(hours=24),
        min_periods=1
    ).mean().values
    
    df['mag_rolling_7d'] = df_indexed['magnitude'].rolling(
        window=pd.Timedelta(days=7),
        min_periods=1
    ).mean().values
    
    df['mag_rolling_30d'] = df_indexed['magnitude'].rolling(
        window=pd.Timedelta(days=30),
        min_periods=1
    ).mean().values
    
    # Rolling counts (earthquake frequency) - use count() instead of size()
    df['count_rolling_24h'] = df_indexed['magnitude'].rolling(
        window=pd.Timedelta(hours=24),
        min_periods=1
    ).count().values
    
    df['count_rolling_7d'] = df_indexed['magnitude'].rolling(
        window=pd.Timedelta(days=7),
        min_periods=1
    ).count().values
    
    # Rolling standard deviation
    df['mag_std_24h'] = df_indexed['magnitude'].rolling(
        window=pd.Timedelta(hours=24),
        min_periods=1
    ).std().values
    
    return df


def create_location_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create location-based features.
    
    Args:
        df: DataFrame with longitude and latitude
    
    Returns:
        DataFrame with location features
    """
    print("[transform_data] Creating location features...")
    
    # Distance from equator (absolute latitude)
    df['abs_latitude'] = df['latitude'].abs()
    
    # Tectonic plate regions (simplified - can be enhanced with actual plate boundaries)
    # High activity regions
    df['pacific_ring'] = (
        ((df['longitude'] >= 120) & (df['longitude'] <= -70)) |
        ((df['latitude'] >= -60) & (df['latitude'] <= 60))
    ).astype(int)
    
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare data for modeling.
    
    Args:
        df: Raw DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    print("[transform_data] Cleaning data...")
    
    # Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates(subset=['id'], keep='first')
    if len(df) < initial_count:
        print(f"[transform_data] Removed {initial_count - len(df)} duplicate records")
    
    # Remove rows with missing critical features
    critical_cols = ['magnitude', 'time', 'longitude', 'latitude']
    df = df.dropna(subset=critical_cols)
    
    # Fill missing values for optional features
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isna().sum() > 0:
            df[col] = df[col].fillna(df[col].median())
    
    # Remove outliers (magnitude > 10 is unrealistic)
    df = df[df['magnitude'] <= 10]
    df = df[df['magnitude'] >= 0]
    
    # Ensure depth is positive
    if 'depth' in df.columns:
        df['depth'] = df['depth'].abs()
    
    print(f"[transform_data] Final dataset: {len(df)} rows, {len(df.columns)} columns")
    
    return df


def main(input_file: str, output_file: str, target_column: Optional[str] = None):
    """
    Main transformation pipeline.
    
    Args:
        input_file: Path to input GeoJSON file
        output_file: Path to output parquet file
        target_column: Optional target column name for prediction
    """
    # Load data
    df = load_geojson(input_file)
    
    # Create features
    df = create_time_features(df)
    df = create_lag_features(df)
    df = create_location_features(df)
    
    # Clean data
    df = clean_data(df)
    
    # Sort by time for time-series
    df = df.sort_values('datetime').reset_index(drop=True)
    
    # Save to parquet (efficient for large datasets)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    print(f"[transform_data] Saving to {output_file}...")
    df.to_parquet(output_file, index=False, compression='snappy')
    
    print(f"[transform_data] ✓ Transformation complete!")
    print(f"[transform_data] Final shape: {df.shape}")
    print(f"[transform_data] Columns: {list(df.columns)}")
    
    # Print basic statistics
    print("\n[transform_data] Basic Statistics:")
    print(df[['magnitude', 'depth', 'time_since_last']].describe())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transform earthquake GeoJSON to training-ready format"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input GeoJSON file path"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output parquet file path"
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Target column name for prediction (optional)"
    )
    
    args = parser.parse_args()
    
    main(args.input, args.output, args.target)

