import os
import boto3
import json
import gzip
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from typing import Dict, Any, Optional

@dataclass
class S3Config:
    """S3 configuration for data lake storage"""
    bucket_name: str
    region: str = 'us-east-1'
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    prefix: str = 'fpl-data'


def generate_config():
    load_dotenv()
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        raise ValueError("S3_BUCKET_NAME environment variable is required")
    
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    return S3Config(
        bucket_name=bucket_name,
        region=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )


class S3DataLake:
    def __init__(self):
        self.config = generate_config()
        self.s3_client = self._create_boto3_client()
    
    def _create_boto3_client(self):
        """Create boto3 S3 client with optional credentials"""
        if self.config.aws_access_key_id and self.config.aws_secret_access_key:
            return boto3.client(
                's3',
                region_name=self.config.region,
                aws_access_key_id=self.config.aws_access_key_id,
                aws_secret_access_key=self.config.aws_secret_access_key
            )
        else:
            return boto3.client('s3', region_name=self.config.region)
    
    def _generate_s3_key(self, data_type: str, filename: str) -> str:
        """Generate partitioned S3 key with date partitioning"""
        return f"{self.config.prefix}/{data_type}/{filename}"
        
    
    def save_json(self, data: Dict[str, Any], data_type: str, filename: str) -> str:
        """Save JSON data to S3 with gzip compression"""
        # Add .gz extension for compressed files
        now = datetime.now(ZoneInfo("Australia/Sydney"))
        data["extraction_timestamp"] = now.strftime("%Y-%m-%d %H:%M:%S")
        data["extraction_date"] = now.strftime("%Y-%m-%d")
        if not filename.endswith('.gz'):
            compressed_filename = filename.replace('.json', '.json.gz')
        else:
            compressed_filename = filename
            
        # Generate S3 key with partitioning
        s3_key = self._generate_s3_key(data_type, compressed_filename)
        s3_path = f"s3://{self.config.bucket_name}/{s3_key}"
        
        # Compress JSON data with gzip
        json_data = json.dumps(data).encode('utf-8')
        compressed_data = gzip.compress(json_data)
        
        # Upload compressed data to S3
        self.s3_client.put_object(
            Bucket=self.config.bucket_name,
            Key=s3_key,
            Body=compressed_data,
            ContentType='application/json',
            ContentEncoding='gzip'
        )
        
        return s3_path