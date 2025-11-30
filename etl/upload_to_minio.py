"""
Upload processed data files to MinIO object storage.

This script uploads files directly to MinIO (S3-compatible storage)
as required by the project specification.
"""

import argparse
import os
import sys
from datetime import datetime
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config


# Default MinIO configuration
# Note: Port 9000 is the API endpoint (for S3 operations), 9001 is the web console
DEFAULT_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'http://localhost:9000')
DEFAULT_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
DEFAULT_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
DEFAULT_BUCKET = os.getenv('MINIO_BUCKET', 'earthquake-data')
DEFAULT_REGION = os.getenv('MINIO_REGION', 'us-east-1')


def create_s3_client(endpoint_url, access_key, secret_key, region='us-east-1'):
    """Create an S3-compatible client for MinIO."""
    config = Config(
        signature_version='s3v4',
        s3={'addressing_style': 'path'}
    )
    
    client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
        config=config
    )
    return client


def ensure_bucket_exists(s3_client, bucket_name):
    """Ensure the bucket exists, create if it doesn't."""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"[MinIO] Bucket '{bucket_name}' already exists")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            # Bucket doesn't exist, create it
            try:
                s3_client.create_bucket(Bucket=bucket_name)
                print(f"[MinIO] Created bucket '{bucket_name}'")
                return True
            except ClientError as create_error:
                print(f"[MinIO] ERROR: Failed to create bucket: {create_error}")
                return False
        else:
            print(f"[MinIO] ERROR: Cannot access bucket: {e}")
            return False


def upload_file_to_minio(
    file_path,
    bucket_name=DEFAULT_BUCKET,
    endpoint_url=DEFAULT_ENDPOINT,
    access_key=DEFAULT_ACCESS_KEY,
    secret_key=DEFAULT_SECRET_KEY,
    object_name=None,
    region=DEFAULT_REGION
):
    """
    Upload a file to MinIO.
    
    Args:
        file_path: Local file path to upload
        bucket_name: MinIO bucket name
        endpoint_url: MinIO endpoint URL
        access_key: MinIO access key
        secret_key: MinIO secret key
        object_name: S3 object name (default: filename with timestamp)
        region: Region name (default: us-east-1)
    
    Returns:
        str: S3 object key if successful, None otherwise
    """
    if not os.path.exists(file_path):
        print(f"[MinIO] ERROR: File not found: {file_path}")
        return None
    
    # Generate object name if not provided
    if object_name is None:
        filename = os.path.basename(file_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        object_name = f"processed/{timestamp}_{filename}"
    
    try:
        # Create S3 client
        s3_client = create_s3_client(endpoint_url, access_key, secret_key, region)
        
        # Ensure bucket exists
        if not ensure_bucket_exists(s3_client, bucket_name):
            return None
        
        # Upload file
        file_size = os.path.getsize(file_path)
        print(f"[MinIO] Uploading {file_path} ({file_size:,} bytes) to s3://{bucket_name}/{object_name}")
        
        s3_client.upload_file(
            file_path,
            bucket_name,
            object_name,
            ExtraArgs={'Metadata': {'uploaded_at': datetime.now().isoformat()}}
        )
        
        print(f"[MinIO] ✓ Successfully uploaded to s3://{bucket_name}/{object_name}")
        return object_name
        
    except NoCredentialsError:
        print("[MinIO] ERROR: Credentials not found. Set MINIO_ACCESS_KEY and MINIO_SECRET_KEY")
        return None
    except ClientError as e:
        print(f"[MinIO] ERROR: Failed to upload file: {e}")
        return None
    except Exception as e:
        print(f"[MinIO] ERROR: Unexpected error: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Upload processed data files to MinIO object storage'
    )
    parser.add_argument(
        '--file',
        required=True,
        help='Path to file to upload'
    )
    parser.add_argument(
        '--bucket',
        default=DEFAULT_BUCKET,
        help=f'MinIO bucket name (default: {DEFAULT_BUCKET})'
    )
    parser.add_argument(
        '--endpoint',
        default=DEFAULT_ENDPOINT,
        help=f'MinIO endpoint URL (default: {DEFAULT_ENDPOINT})'
    )
    parser.add_argument(
        '--access-key',
        default=DEFAULT_ACCESS_KEY,
        help='MinIO access key (default: from env or minioadmin)'
    )
    parser.add_argument(
        '--secret-key',
        default=DEFAULT_SECRET_KEY,
        help='MinIO secret key (default: from env or minioadmin)'
    )
    parser.add_argument(
        '--object-name',
        default=None,
        help='S3 object name (default: auto-generated with timestamp)'
    )
    
    args = parser.parse_args()
    
    result = upload_file_to_minio(
        file_path=args.file,
        bucket_name=args.bucket,
        endpoint_url=args.endpoint,
        access_key=args.access_key,
        secret_key=args.secret_key,
        object_name=args.object_name
    )
    
    if result:
        print(f"[MinIO] Upload successful: {result}")
        sys.exit(0)
    else:
        print("[MinIO] Upload failed")
        sys.exit(1)


if __name__ == '__main__':
    main()

