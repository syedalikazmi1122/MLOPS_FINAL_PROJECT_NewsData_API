"""
Apache Airflow DAG for Automated Earthquake Data Pipeline.

This DAG orchestrates the complete ETL pipeline:
1. Extract: Fetch earthquake data from USGS API
2. Quality Check: Validate data quality (mandatory gate)
3. Transform: Format data for model training
4. Load: Store processed data and version with DVC

Schedule: Daily at 2 AM UTC
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Default arguments
default_args = {
    'owner': 'mlops-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'earthquake_etl_pipeline',
    default_args=default_args,
    description='Automated Earthquake Data ETL Pipeline',
    schedule_interval='0 2 * * *',  # Daily at 2 AM UTC
    start_date=days_ago(1),
    catchup=False,
    tags=['mlops', 'earthquake', 'etl'],
)

# Configuration
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw')
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')
START_YEAR = 2010
END_YEAR = datetime.now().year - 1  # Previous year to avoid incomplete data
INTERVAL_YEARS = 1
MIN_MAGNITUDE = 3.0


def extract_data(**context):
    """Extract earthquake data from USGS API."""
    import subprocess
    
    print(f"[DAG] Starting data extraction...")
    print(f"[DAG] Date range: {START_YEAR} to {END_YEAR}")
    
    cmd = [
        'python',
        os.path.join(PROJECT_ROOT, 'etl', 'download_historical.py'),
        '--out-dir', RAW_DATA_DIR,
        '--start-year', str(START_YEAR),
        '--end-year', str(END_YEAR),
        '--interval-years', str(INTERVAL_YEARS),
        '--minmagnitude', str(MIN_MAGNITUDE),
        '--combine'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
    
    if result.returncode != 0:
        print(f"[DAG] Extraction failed: {result.stderr}")
        raise Exception(f"Data extraction failed: {result.stderr}")
    
    print(f"[DAG] Extraction completed successfully")
    print(result.stdout)
    
    # Return path to combined file
    combined_file = os.path.join(RAW_DATA_DIR, 'earthquakes_combined.geojson')
    if not os.path.exists(combined_file):
        raise Exception(f"Combined file not found: {combined_file}")
    
    return combined_file


def quality_check(**context):
    """Run mandatory data quality checks."""
    import subprocess
    
    # Get combined file from previous task
    ti = context['ti']
    combined_file = ti.xcom_pull(task_ids='extract_data')
    
    if not combined_file or not os.path.exists(combined_file):
        raise Exception(f"Input file not found: {combined_file}")
    
    print(f"[DAG] Running quality checks on {combined_file}...")
    
    cmd = [
        'python',
        os.path.join(PROJECT_ROOT, 'etl', 'data_quality_check.py'),
        '--input', combined_file,
        '--format', 'geojson'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
    
    if result.returncode != 0:
        print(f"[DAG] Quality check FAILED: {result.stderr}")
        print(result.stdout)
        raise Exception("Data quality check failed - DAG stopped")
    
    print(f"[DAG] Quality check passed!")
    print(result.stdout)
    
    return combined_file


def transform_data(**context):
    """Transform data for model training."""
    import subprocess
    
    # Get validated file from quality check
    ti = context['ti']
    input_file = ti.xcom_pull(task_ids='quality_check')
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    output_file = os.path.join(PROCESSED_DATA_DIR, f'earthquakes_processed_{timestamp}.parquet')
    
    print(f"[DAG] Transforming data: {input_file} -> {output_file}")
    
    cmd = [
        'python',
        os.path.join(PROJECT_ROOT, 'etl', 'transform_data.py'),
        '--input', input_file,
        '--output', output_file
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
    
    if result.returncode != 0:
        print(f"[DAG] Transformation failed: {result.stderr}")
        raise Exception(f"Data transformation failed: {result.stderr}")
    
    print(f"[DAG] Transformation completed successfully")
    print(result.stdout)
    
    return output_file


def version_data(**context):
    """Version data using DVC."""
    import subprocess
    
    # Get processed file from transform task
    ti = context['ti']
    processed_file = ti.xcom_pull(task_ids='transform_data')
    
    print(f"[DAG] Versioning data with DVC: {processed_file}")
    
    # DVC commands
    # Note: DVC remote should be configured separately (Dagshub, S3, etc.)
    dvc_commands = [
        # Add file to DVC tracking
        ['dvc', 'add', processed_file],
        # Commit DVC metadata (if git is configured)
        # ['git', 'add', f'{processed_file}.dvc', '.gitignore'],
        # ['git', 'commit', '-m', f'Add processed data: {os.path.basename(processed_file)}'],
    ]
    
    for cmd in dvc_commands:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
        if result.returncode != 0:
            print(f"[DAG] Warning: DVC command failed: {cmd}")
            print(result.stderr)
            # Don't fail DAG if DVC is not fully configured yet
            # raise Exception(f"DVC versioning failed: {result.stderr}")
    
    print(f"[DAG] Data versioning completed")
    return processed_file


# Task definitions
extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
)

quality_check_task = PythonOperator(
    task_id='quality_check',
    python_callable=quality_check,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

version_task = PythonOperator(
    task_id='version_data',
    python_callable=version_data,
    dag=dag,
)

# Task dependencies
extract_task >> quality_check_task >> transform_task >> version_task

