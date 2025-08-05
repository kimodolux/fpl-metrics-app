import boto3
from dataclasses import dataclass
from typing import Optional

@dataclass
class S3Config:
    """S3 configuration for data lake storage"""
    bucket_name: str
    region: str = 'us-east-1'
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    prefix: str = 'fpl-data'
