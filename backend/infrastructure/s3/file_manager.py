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

    def get_by_file_id(self, file_path: str) -> bytes | None:
        s3 = self._client()

        data = s3.get_object(Bucket="goods", Key=file_path)

        if not data:
            return None
        return data["Body"].read()

    def delete_object(self, path: str) -> None:
        s3 = self._client()

        s3.delete_object(Bucket="goods", Key=path)

    def delete_folder(self, folder: str) -> None:
        s3 = self._client()

        objects_to_delete = s3.list_objects_v2(
            Bucket="goods",
            Prefix=folder,
        )

        if "Contents" in objects_to_delete:
            for obj in objects_to_delete["Contents"]:
                s3.delete_object(Bucket="goods", Key=obj["Key"])
