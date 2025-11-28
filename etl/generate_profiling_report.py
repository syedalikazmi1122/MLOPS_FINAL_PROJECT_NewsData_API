#!/usr/bin/env python3
"""
Generate Pandas Profiling Report for Data Quality Documentation.

This script generates a detailed data profiling report and logs it to MLflow
as an artifact (for Dagshub integration).

Usage:
    python etl/generate_profiling_report.py --input data/processed/earthquakes_processed.parquet
    python etl/generate_profiling_report.py --input data/raw/earthquakes_combined.geojson --format geojson
"""

import argparse
import os
import sys
import pandas as pd
import mlflow
from ydata_profiling import ProfileReport


def load_data(file_path: str, file_format: str = 'parquet') -> pd.DataFrame:
    """Load data from file."""
    if file_format == 'parquet':
        return pd.read_parquet(file_path)
    elif file_format == 'geojson':
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        features = data.get('features', [])
        
        records = []
        for feat in features:
            props = feat.get('properties', {})
            geom = feat.get('geometry', {})
            coords = geom.get('coordinates', [])
            
            record = {
                'magnitude': props.get('mag'),
                'time': props.get('time'),
                'longitude': coords[0] if len(coords) > 0 else None,
                'latitude': coords[1] if len(coords) > 1 else None,
                'depth': coords[2] if len(coords) > 2 else None,
            }
            records.append(record)
        
        df = pd.DataFrame(records)
        # Convert time to datetime
        if 'time' in df.columns:
            df['datetime'] = pd.to_datetime(df['time'], unit='ms')
        return df
    else:
        raise ValueError(f"Unsupported format: {file_format}")


def generate_report(df: pd.DataFrame, output_path: str = None, minimal: bool = False):
    """
    Generate profiling report.
    
    Args:
        df: DataFrame to profile
        output_path: Optional path to save HTML report
        minimal: If True, generate minimal report (faster)
    """
    print(f"[profiling] Generating report for {len(df)} rows, {len(df.columns)} columns...")
    
    # Generate profile report
    profile = ProfileReport(
        df,
        title="Earthquake Data Profiling Report",
        minimal=minimal,
        progress_bar=True
    )
    
    if output_path:
        print(f"[profiling] Saving report to {output_path}...")
        profile.to_file(output_path)
    
    return profile


def log_to_mlflow(profile, experiment_name: str = "data_profiling"):
    """Log profiling report to MLflow as artifact."""
    mlflow_tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
    if mlflow_tracking_uri:
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        print(f"[profiling] Using MLflow tracking URI: {mlflow_tracking_uri}")
    
    mlflow.set_experiment(experiment_name)
    
    with mlflow.start_run():
        # Save report temporarily
        report_path = "data_profile_report.html"
        profile.to_file(report_path)
        
        # Log as artifact
        mlflow.log_artifact(report_path, "profiling_report")
        
        # Clean up
        os.remove(report_path)
        
        print(f"[profiling] ✓ Report logged to MLflow")
        print(f"[profiling] MLflow Run ID: {mlflow.active_run().info.run_id}")


def main(input_file: str, file_format: str = 'parquet', output_file: str = None, 
         log_to_mlflow_flag: bool = False, minimal: bool = False):
    """Main function."""
    # Load data
    df = load_data(input_file, file_format)
    
    # Generate report
    profile = generate_report(df, output_path=output_file, minimal=minimal)
    
    # Log to MLflow if requested
    if log_to_mlflow_flag:
        log_to_mlflow(profile)
    
    print("[profiling] ✓ Profiling complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate data profiling report"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input data file"
    )
    parser.add_argument(
        "--format",
        default="parquet",
        choices=['parquet', 'geojson'],
        help="File format"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output HTML report path (optional)"
    )
    parser.add_argument(
        "--log-to-mlflow",
        action="store_true",
        help="Log report to MLflow as artifact"
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Generate minimal report (faster)"
    )
    
    args = parser.parse_args()
    
    main(
        args.input,
        file_format=args.format,
        output_file=args.output,
        log_to_mlflow_flag=args.log_to_mlflow,
        minimal=args.minimal
    )

