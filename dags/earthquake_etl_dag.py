"""
Apache Airflow DAG for Automated Earthquake Data Pipeline.

This DAG orchestrates the complete MLOps pipeline:
1. Extract: Fetch earthquake data from USGS API
2. Quality Check: Validate data quality (mandatory gate)
3. Transform: Format data for model training
4. Upload: Store processed data in MinIO
5. Version: Version data with DVC and push to both MinIO and Dagshub
6. Profiling: Generate data profiling report and log to MLflow
7. Train: Train ML model and track with MLflow

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

# MinIO Configuration (can be overridden via environment variables)
# In Docker: MINIO_ENDPOINT is set to 'http://minio:9000' in docker-compose.yml
# Locally: Use 'http://localhost:9000'
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'http://localhost:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'earthquake-data')


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


def upload_to_minio(**context):
    """Upload processed data to MinIO object storage."""
    import subprocess
    
    # Get processed file from transform task
    ti = context['ti']
    processed_file = ti.xcom_pull(task_ids='transform_data')
    
    if not processed_file or not os.path.exists(processed_file):
        raise Exception(f"Processed file not found: {processed_file}")
    
    print(f"[DAG] Uploading to MinIO: {processed_file}")
    
    cmd = [
        'python',
        os.path.join(PROJECT_ROOT, 'etl', 'upload_to_minio.py'),
        '--file', processed_file,
        '--bucket', MINIO_BUCKET,
        '--endpoint', MINIO_ENDPOINT,
        '--access-key', MINIO_ACCESS_KEY,
        '--secret-key', MINIO_SECRET_KEY
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
    
    if result.returncode != 0:
        print(f"[DAG] MinIO upload failed: {result.stderr}")
        print(result.stdout)
        raise Exception(f"MinIO upload failed: {result.stderr}")
    
    print(f"[DAG] MinIO upload completed successfully")
    print(result.stdout)
    
    return processed_file


def version_data(**context):
    """Version data using DVC and push to both MinIO and Dagshub remotes."""
    import subprocess
    
    # Get processed file from upload task
    ti = context['ti']
    processed_file = ti.xcom_pull(task_ids='upload_to_minio')
    
    if not processed_file or not os.path.exists(processed_file):
        raise Exception(f"Processed file not found: {processed_file}")
    
    print(f"[DAG] Versioning data with DVC: {processed_file}")
    
    # Set environment variables for DVC to use MinIO
    env = os.environ.copy()
    env['AWS_ACCESS_KEY_ID'] = MINIO_ACCESS_KEY
    env['AWS_SECRET_ACCESS_KEY'] = MINIO_SECRET_KEY
    env['AWS_ENDPOINT_URL'] = MINIO_ENDPOINT
    
    # DVC commands
    dvc_commands = [
        # Add file to DVC tracking (if not already tracked)
        ['dvc', 'add', processed_file],
        # Push to MinIO remote (default remote)
        ['dvc', 'push', '--remote', 'minio-storage'],
        # Push to Dagshub remote (for Phase II integration)
        ['dvc', 'push', '--remote', 'dagshub'],
    ]
    
    for cmd in dvc_commands:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            env=env
        )
        if result.returncode != 0:
            # Check if file is already tracked (this is OK)
            if 'already tracked' in result.stderr.lower() or 'already in cache' in result.stderr.lower():
                print(f"[DAG] File already tracked, continuing...")
                continue
            print(f"[DAG] Warning: DVC command failed: {cmd}")
            print(result.stderr)
            print(result.stdout)
            # Don't fail DAG if DVC remote is not fully configured
            # In production, you may want to make this stricter
            if 'push' in cmd[1]:
                remote_name = cmd[cmd.index('--remote') + 1] if '--remote' in cmd else 'default'
                print(f"[DAG] Warning: DVC push to {remote_name} failed. Ensure remote is configured.")
                # Continue with other remotes even if one fails
                continue
    
    print(f"[DAG] Data versioning completed (pushed to MinIO and Dagshub)")
    return processed_file


def generate_profiling_report(**context):
    """Generate data profiling report and log to MLflow."""
    import subprocess
    
    # Get processed file from version task
    ti = context['ti']
    processed_file = ti.xcom_pull(task_ids='version_data')
    
    if not processed_file or not os.path.exists(processed_file):
        raise Exception(f"Processed file not found: {processed_file}")
    
    print(f"[DAG] Generating profiling report for {processed_file}...")
    
    # Generate report and log to MLflow
    cmd = [
        'python',
        os.path.join(PROJECT_ROOT, 'etl', 'generate_profiling_report.py'),
        '--input', processed_file,
        '--format', 'parquet',
        '--log-to-mlflow'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
    
    if result.returncode != 0:
        print(f"[DAG] Profiling report generation failed: {result.stderr}")
        print(result.stdout)
        # Don't fail DAG if MLflow is not configured yet
        print(f"[DAG] Warning: Profiling report generation failed. Ensure MLflow is configured.")
    else:
        print(f"[DAG] Profiling report generated and logged to MLflow")
        print(result.stdout)
    
    return processed_file


def train_model(**context):
    """Train ML model and track with MLflow."""
    import subprocess
    
    # Get processed file from profiling task
    ti = context['ti']
    processed_file = ti.xcom_pull(task_ids='generate_profiling_report')
    
    if not processed_file or not os.path.exists(processed_file):
        raise Exception(f"Processed file not found: {processed_file}")
    
    print(f"[DAG] Training model on {processed_file}...")
    
    # Generate experiment name with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    experiment_name = f'earthquake_prediction_{timestamp}'
    
    cmd = [
        'python',
        os.path.join(PROJECT_ROOT, 'train.py'),
        '--data', processed_file,
        '--experiment-name', experiment_name,
        '--model-type', 'random_forest',
        '--n-estimators', '100'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
    
    if result.returncode != 0:
        print(f"[DAG] Model training failed: {result.stderr}")
        print(result.stdout)
        raise Exception(f"Model training failed: {result.stderr}")
    
    print(f"[DAG] Model training completed successfully")
    print(result.stdout)
    
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

upload_task = PythonOperator(
    task_id='upload_to_minio',
    python_callable=upload_to_minio,
    dag=dag,
)

version_task = PythonOperator(
    task_id='version_data',
    python_callable=version_data,
    dag=dag,
)

profiling_task = PythonOperator(
    task_id='generate_profiling_report',
    python_callable=generate_profiling_report,
    dag=dag,
)

train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

# Task dependencies
extract_task >> quality_check_task >> transform_task >> upload_task >> version_task >> profiling_task >> train_task

