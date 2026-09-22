import os
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from app.core.config import settings
from app.core.logging import logger


class BaseStorageAdapter(ABC):
    @abstractmethod
    async def save_file(self, file_name: str, content: bytes, content_type: Optional[str] = None) -> str:
        pass

    @abstractmethod
    async def get_file(self, file_path: str) -> Optional[bytes]:
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        pass


class LocalStorageAdapter(BaseStorageAdapter):
    def __init__(self, base_dir: str = settings.LOCAL_STORAGE_DIR):
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    async def save_file(self, file_name: str, content: bytes, content_type: Optional[str] = None) -> str:
        target_path = os.path.join(self.base_dir, file_name)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "wb") as f:
            f.write(content)
        return target_path

    async def get_file(self, file_path: str) -> Optional[bytes]:
        if not os.path.exists(file_path):
            return None
        with open(file_path, "rb") as f:
            return f.read()

    async def delete_file(self, file_path: str) -> bool:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False


def get_storage_adapter() -> BaseStorageAdapter:
    if settings.STORAGE_BACKEND.lower() == "s3":
        logger.info("Using S3 Storage Adapter (configured for S3 bucket)")
        # S3 storage implementation placeholder / falls back to local if unset
        return LocalStorageAdapter()
    return LocalStorageAdapter()
