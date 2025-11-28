#!/usr/bin/env python3
"""
Data Quality Check Module - Mandatory Quality Gate for MLOps Pipeline.

This module implements strict data quality checks:
- Null value checks (>1% threshold)
- Schema validation
- Data type validation
- Range validation for key columns

If quality check fails, the process must fail (for Airflow DAG integration).

Usage:
    python etl/data_quality_check.py --input data/raw/earthquakes_combined.geojson
    python etl/data_quality_check.py --input data/processed/earthquakes_processed.parquet --format parquet
"""

import argparse
import json
import sys
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np


# Quality thresholds
NULL_THRESHOLD = 0.01  # 1% maximum null values allowed
MIN_ROWS = 100  # Minimum number of rows required


def load_data(file_path: str, file_format: str = 'geojson') -> pd.DataFrame:
    """Load data from file."""
    if file_format == 'geojson':
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        features = data.get('features', [])
        
        records = []
        for feat in features:
            props = feat.get('properties', {})
            geom = feat.get('geometry', {})
            coords = geom.get('coordinates', [])
            
            record = {
                'id': feat.get('id', ''),
                'magnitude': props.get('mag'),
                'time': props.get('time'),
                'longitude': coords[0] if len(coords) > 0 else None,
                'latitude': coords[1] if len(coords) > 1 else None,
                'depth': coords[2] if len(coords) > 2 else None,
            }
            records.append(record)
        
        return pd.DataFrame(records)
    
    elif file_format == 'parquet':
        return pd.read_parquet(file_path)
    
    else:
        raise ValueError(f"Unsupported format: {file_format}")


def check_row_count(df: pd.DataFrame) -> Tuple[bool, str]:
    """Check if dataset has minimum required rows."""
    count = len(df)
    if count < MIN_ROWS:
        return False, f"Row count ({count}) is below minimum threshold ({MIN_ROWS})"
    return True, f"Row count check passed: {count} rows"


def check_null_values(df: pd.DataFrame, threshold: float = NULL_THRESHOLD) -> Tuple[bool, List[str]]:
    """
    Check for excessive null values in key columns.
    
    Returns:
        (is_valid, list_of_violations)
    """
    violations = []
    key_columns = ['magnitude', 'time', 'longitude', 'latitude']
    
    for col in key_columns:
        if col not in df.columns:
            violations.append(f"Missing required column: {col}")
            continue
        
        null_pct = df[col].isna().sum() / len(df)
        if null_pct > threshold:
            violations.append(
                f"Column '{col}' has {null_pct:.2%} null values "
                f"(threshold: {threshold:.2%})"
            )
    
    is_valid = len(violations) == 0
    return is_valid, violations


def check_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Validate data schema and types."""
    violations = []
    
    # Required columns
    required_cols = ['magnitude', 'time', 'longitude', 'latitude']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        violations.append(f"Missing required columns: {missing_cols}")
    
    # Type checks
    type_checks = {
        'magnitude': (float, int),
        'time': (int, float, np.int64),
        'longitude': (float, int),
        'latitude': (float, int),
    }
    
    for col, expected_types in type_checks.items():
        if col in df.columns:
            if not isinstance(df[col].iloc[0] if len(df) > 0 else None, expected_types):
                actual_type = type(df[col].iloc[0]) if len(df) > 0 else 'unknown'
                violations.append(
                    f"Column '{col}' has wrong type: {actual_type}, "
                    f"expected one of {expected_types}"
                )
    
    is_valid = len(violations) == 0
    return is_valid, violations


def check_value_ranges(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Check if values are within expected ranges."""
    violations = []
    
    # Magnitude range (0-10 is realistic)
    if 'magnitude' in df.columns:
        invalid_mag = df[(df['magnitude'] < 0) | (df['magnitude'] > 10)]
        if len(invalid_mag) > 0:
            violations.append(
                f"Found {len(invalid_mag)} rows with magnitude outside [0, 10] range"
            )
    
    # Longitude range (-180 to 180)
    if 'longitude' in df.columns:
        invalid_lon = df[(df['longitude'] < -180) | (df['longitude'] > 180)]
        if len(invalid_lon) > 0:
            violations.append(
                f"Found {len(invalid_lon)} rows with longitude outside [-180, 180] range"
            )
    
    # Latitude range (-90 to 90)
    if 'latitude' in df.columns:
        invalid_lat = df[(df['latitude'] < -90) | (df['latitude'] > 90)]
        if len(invalid_lat) > 0:
            violations.append(
                f"Found {len(invalid_lat)} rows with latitude outside [-90, 90] range"
            )
    
    is_valid = len(violations) == 0
    return is_valid, violations


def run_quality_checks(file_path: str, file_format: str = 'geojson') -> Dict:
    """
    Run all quality checks and return results.
    
    Returns:
        Dictionary with check results and overall status
    """
    print(f"[data_quality_check] Loading data from {file_path}...")
    df = load_data(file_path, file_format)
    
    print(f"[data_quality_check] Running quality checks on {len(df)} rows...")
    
    results = {
        'file_path': file_path,
        'row_count': len(df),
        'checks': {},
        'passed': True,
        'violations': []
    }
    
    # Check 1: Row count
    passed, message = check_row_count(df)
    results['checks']['row_count'] = {'passed': passed, 'message': message}
    if not passed:
        results['passed'] = False
        results['violations'].append(message)
    
    # Check 2: Null values
    passed, violations = check_null_values(df)
    results['checks']['null_values'] = {'passed': passed, 'violations': violations}
    if not passed:
        results['passed'] = False
        results['violations'].extend(violations)
    
    # Check 3: Schema
    passed, violations = check_schema(df)
    results['checks']['schema'] = {'passed': passed, 'violations': violations}
    if not passed:
        results['passed'] = False
        results['violations'].extend(violations)
    
    # Check 4: Value ranges
    passed, violations = check_value_ranges(df)
    results['checks']['value_ranges'] = {'passed': passed, 'violations': violations}
    if not passed:
        results['passed'] = False
        results['violations'].extend(violations)
    
    return results


def print_results(results: Dict):
    """Print quality check results."""
    print("\n" + "="*60)
    print("DATA QUALITY CHECK RESULTS")
    print("="*60)
    print(f"File: {results['file_path']}")
    print(f"Rows: {results['row_count']:,}")
    print(f"\nOverall Status: {'✓ PASSED' if results['passed'] else '✗ FAILED'}")
    
    print("\nCheck Details:")
    for check_name, check_result in results['checks'].items():
        status = "✓" if check_result['passed'] else "✗"
        print(f"  {status} {check_name.replace('_', ' ').title()}")
        if not check_result['passed']:
            if 'violations' in check_result:
                for violation in check_result['violations']:
                    print(f"    - {violation}")
            elif 'message' in check_result:
                print(f"    - {check_result['message']}")
    
    if results['violations']:
        print("\nAll Violations:")
        for i, violation in enumerate(results['violations'], 1):
            print(f"  {i}. {violation}")
    
    print("="*60)


def main(input_file: str, file_format: str = 'geojson', fail_on_error: bool = True):
    """
    Main quality check function.
    
    Args:
        input_file: Path to input file
        file_format: File format ('geojson' or 'parquet')
        fail_on_error: If True, exit with error code on failure
    """
    try:
        results = run_quality_checks(input_file, file_format)
        print_results(results)
        
        if not results['passed']:
            print("\n[data_quality_check] ✗ QUALITY CHECK FAILED")
            if fail_on_error:
                sys.exit(1)
        else:
            print("\n[data_quality_check] ✓ All quality checks passed!")
            sys.exit(0)
    
    except Exception as e:
        print(f"\n[data_quality_check] ERROR: {e}")
        if fail_on_error:
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Data Quality Check - Mandatory Quality Gate"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input file path (GeoJSON or Parquet)"
    )
    parser.add_argument(
        "--format",
        default="geojson",
        choices=['geojson', 'parquet'],
        help="File format (default: geojson)"
    )
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="Don't exit with error code on failure (for testing)"
    )
    
    args = parser.parse_args()
    
    main(args.input, args.format, fail_on_error=not args.no_fail)

