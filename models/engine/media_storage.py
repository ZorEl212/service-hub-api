import os
from typing import Optional

import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from fastapi import UploadFile


class MediaStorage:
    """
    Media storage class for handling image and video uploads, transformations,
    and deletions using Cloudinary.
    """

    def __init__(self):
        self.cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        self.api_key = os.getenv("CLOUDINARY_API_KEY")
        self.api_secret = os.getenv("CLOUDINARY_API_SECRET")

        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True
        )

    def upload_file_from_path(self, file_path: str, public_id: Optional[str] = None, resource_type: str = "image"):
        """Upload a local file (image or video)."""
        return cloudinary.uploader.upload(
            file_path,
            public_id=public_id,
            resource_type=resource_type
        )

    def upload(self, file: UploadFile, public_id: Optional[str] = None, resource_type: str = "image"):
        """Upload an in-memory file (e.g., from FastAPI UploadFile)."""
        return cloudinary.uploader.upload(
            file.file,
            public_id=public_id,
            resource_type=resource_type
        )

    def delete_media(self, public_id: str, resource_type: str = "image"):
        """Delete media by public_id."""
        return cloudinary.uploader.destroy(public_id, resource_type=resource_type)

    def generate_optimized_url(self, public_id: str, resource_type: str = "image"):
        """Generate optimized URL with auto format and quality."""
        return cloudinary_url(public_id, fetch_format="auto", quality="auto", resource_type=resource_type)[0]

    def generate_cropped_url(self, public_id: str, width: int = 500, height: int = 500, resource_type: str = "image"):
        """Generate auto-cropped URL."""
        return cloudinary_url(public_id, width=width, height=height, crop="auto", gravity="auto", resource_type=resource_type)[0]
