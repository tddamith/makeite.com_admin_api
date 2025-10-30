import base64
import io
import asyncio
import threading
from uuid import uuid4
from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
import boto3
import os




# Initialize router
router = APIRouter()

# Example AWS config
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

# Initialize S3 client
s3_client =boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)

# --- Thread executor for uploads ---
executor = ThreadPoolExecutor()


# --- Progress Tracker ---
class S3Progress:
    def __init__(self, filesize, job_collection, job_id):
        self._filesize = filesize
        self._seen_so_far = 0
        self.job_collection = job_collection
        self.job_id = job_id
        self.loop = asyncio.get_event_loop()

    def __call__(self, bytes_amount):
        self._seen_so_far += bytes_amount
        progress = int((self._seen_so_far / self._filesize) * 100)

        async def update_progress():
            await self.job_collection.update_one(
                {"job_id": self.job_id},
                {"$set": {"progress": progress}}
            )

        asyncio.run_coroutine_threadsafe(update_progress(), self.loop)

# --- Async Upload Function ---
async def upload_to_s3_with_progress(file_data, filename, content_type, job_collection, job_id):
    file_size = len(file_data)
    progress_callback = S3Progress(file_size, job_collection, job_id)

    def _upload():
        s3_client.upload_fileobj(
            io.BytesIO(file_data),
            AWS_BUCKET_NAME,
            filename,
            ExtraArgs={"ContentType": content_type},
            Callback=progress_callback
        )

    await asyncio.to_thread(_upload)