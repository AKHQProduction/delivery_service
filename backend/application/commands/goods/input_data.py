from dataclasses import dataclass


@dataclass(frozen=True)
class FileMetadata:
    payload: bytes | None
    extension: str = "jpg"
