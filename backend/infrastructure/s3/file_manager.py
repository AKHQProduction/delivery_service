from io import BytesIO

from boto3 import client
from botocore.client import BaseClient
from botocore.config import Config

from application.common.file_manager import FileManager
from infrastructure.s3.config import S3Config


class S3FileManager(FileManager):
    def __init__(self, config: S3Config):
        self._config = config

    def _client(self) -> BaseClient:
        return client(
            "s3",
            endpoint_url=self._config.endpoint_url,
            aws_access_key_id=self._config.aws_access_key_id,
            aws_secret_access_key=self._config.aws_secret_access_key,
            config=Config(signature_version="s3v4"),
        )

    def save(self, payload: bytes, path: str) -> None:
        s3 = self._client()

        with BytesIO(payload) as file_obj:
            s3.upload_fileobj(file_obj, "goods", path)
