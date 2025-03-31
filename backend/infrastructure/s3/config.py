from dataclasses import dataclass


@dataclass
class S3Config:
    endpoint_url: str
    aws_access_key_id: str
    aws_secret_access_key: str
