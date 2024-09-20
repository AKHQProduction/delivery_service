from dataclasses import dataclass


@dataclass(frozen=True)
class FileMetadata:
    payload: bytes
    extension: str = "jpg"
