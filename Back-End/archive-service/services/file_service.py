from fastapi import UploadFile
from minio import Minio
from minio.error import S3Error
from config import settings
import magic
import uuid
from typing import Optional
import io
from datetime import timedelta


class FileService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Ensure bucket exists"""
        try:
            if not self.client.bucket_exists(settings.MINIO_BUCKET):
                self.client.make_bucket(settings.MINIO_BUCKET)
        except S3Error as e:
            print(f"Error ensuring bucket: {e}")
    
    def validate_file(self, file: UploadFile) -> bool:
        """Validate file type and size"""
        # Check file extension
        if file.filename:
            extension = file.filename.split(".")[-1].lower()
            if extension not in settings.ALLOWED_FILE_TYPES:
                return False
        
        # Check file size (simplified - should read in chunks in production)
        if file.size and file.size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            return False
        
        return True
    
    async def upload_file(self, file: UploadFile, field: str) -> str:
        """Upload file to MinIO and return URL"""
        try:
            # Generate unique filename
            file_extension = file.filename.split(".")[-1] if file.filename else "bin"
            unique_filename = f"{field}/{uuid.uuid4()}.{file_extension}"
            
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            
            # Upload to MinIO
            self.client.put_object(
                settings.MINIO_BUCKET,
                unique_filename,
                io.BytesIO(file_content),
                file_size,
                content_type=file.content_type or "application/octet-stream"
            )
            
            # Reset file pointer for potential re-reading
            await file.seek(0)
            
            # Return file URL
            return f"minio://{settings.MINIO_BUCKET}/{unique_filename}"
        
        except S3Error as e:
            raise Exception(f"Failed to upload file: {e}")
    
    async def delete_file(self, file_url: str):
        """Delete file from MinIO"""
        try:
            # Extract object name from URL
            object_name = file_url.replace(f"minio://{settings.MINIO_BUCKET}/", "")
            self.client.remove_object(settings.MINIO_BUCKET, object_name)
        except S3Error as e:
            print(f"Error deleting file: {e}")
    
    def get_presigned_url(self, file_url: str, expires: int = 3600) -> str:
        """Generate a presigned URL for file access"""
        try:
            # Extract object name from URL
            object_name = file_url.replace(f"minio://{settings.MINIO_BUCKET}/", "")
            url = self.client.presigned_get_object(
                settings.MINIO_BUCKET,
                object_name,
                expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            raise Exception(f"Failed to generate presigned URL: {e}")
    
    def get_file_object(self, file_url: str):
        """Get file object from MinIO"""
        try:
            # Extract object name from URL
            object_name = file_url.replace(f"minio://{settings.MINIO_BUCKET}/", "")
            response = self.client.get_object(settings.MINIO_BUCKET, object_name)
            return response
        except S3Error as e:
            raise Exception(f"Failed to get file: {e}")
    
    async def extract_text(self, file: UploadFile) -> str:
        """Extract text content from file"""
        # This is a simplified version
        # In production, use proper libraries for each file type
        # - pypdf2 for PDFs
        # - python-docx for DOCX
        # - pytesseract for images (OCR)
        # - speech_recognition for audio
        
        try:
            if file.filename and file.filename.endswith(('.txt', '.md')):
                content = await file.read()
                await file.seek(0)
                return content.decode('utf-8')
            else:
                # Placeholder for other file types
                return f"Content extracted from {file.filename}"
        except Exception as e:
            return f"Failed to extract text: {e}"
