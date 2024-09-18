from application.common.file_manager import FileManager


class FakeFileManager(FileManager):
    def __init__(self):
        self.saved = False
        self.deleted = False

    def save(self, payload: bytes, path: str) -> None:
        self.saved = True

    def delete(self, path: str) -> None:
        self.deleted = True
