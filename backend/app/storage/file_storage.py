import os
import uuid
import aiofiles
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException, status
from app.config import settings

class FileStorageService:
    def __init__(self, upload_dir: str = settings.UPLOAD_DIR):
        self.upload_dir = Path(upload_dir).resolve()
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 # Convert MB to Bytes

    async def save_file(self, file: UploadFile) -> Tuple[str, str, int, str]:
        """
        Validate and save an uploaded file securely.
        Returns: (stored_filename, original_filename, file_size, mime_type)
        """
        # Validate original filename existence
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_FILENAME", "message": "Uploaded file must have a filename."}
            )

        # Sanitize and validate extension
        file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_EXTENSION",
                    "message": f"File extension '.{file_ext}' is not permitted. Allowed: {settings.ALLOWED_EXTENSIONS}"
                }
            )

        # Validate MIME type
        content_type = file.content_type or ""
        if content_type not in settings.ALLOWED_MIME_TYPES:
            # Fallback check for standard image/pdf
            if not (content_type.startswith("image/") or content_type == "application/pdf"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "INVALID_MIME_TYPE",
                        "message": f"File type '{content_type}' is not supported."
                    }
                )

        # Generate secure unique server filename
        unique_name = f"{uuid.uuid4().hex}_{int(os.times().system * 1000)}.{file_ext}"
        destination = (self.upload_dir / unique_name).resolve()

        # Path traversal guard
        if not str(destination).startswith(str(self.upload_dir)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "PATH_TRAVERSAL_DETECTED", "message": "Invalid file path detected."}
            )

        # Stream write with size limit checking
        size = 0
        chunk_size = 1024 * 1024 # 1MB chunks
        
        async with aiofiles.open(destination, 'wb') as out_file:
            while chunk := await file.read(chunk_size):
                size += len(chunk)
                if size > self.max_size:
                    # Clean up partial file
                    await out_file.close()
                    if destination.exists():
                        destination.unlink()
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail={
                            "code": "FILE_TOO_LARGE",
                            "message": f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
                        }
                    )
                await out_file.write(chunk)

        return unique_name, file.filename, size, content_type

    def get_file_path(self, stored_filename: str) -> Path:
        """Resolve full filepath securely while preventing path traversal."""
        # Clean filename of path separators
        clean_filename = Path(stored_filename).name
        file_path = (self.upload_dir / clean_filename).resolve()

        if not str(file_path).startswith(str(self.upload_dir)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_PATH", "message": "Access denied."}
            )

        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "FILE_NOT_FOUND", "message": "Requested document was not found on server."}
            )

        return file_path

    def delete_file(self, stored_filename: str) -> bool:
        """Delete stored file from disk."""
        try:
            file_path = self.get_file_path(stored_filename)
            if file_path.exists():
                file_path.unlink()
                return True
        except Exception:
            pass
        return False

file_storage = FileStorageService()
