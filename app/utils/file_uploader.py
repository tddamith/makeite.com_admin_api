import base64
import io
import asyncio
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import boto3
import os

# AWS Config
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

# S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)

# Thread executor for uploads
executor = ThreadPoolExecutor()


# --- Progress Tracker ---
class S3Progress:
    def __init__(self, filesize, job_collection, job_id):
        self._filesize = filesize
        self._seen_so_far = 0
        self.job_collection = job_collection
        self.job_id = job_id

    def __call__(self, bytes_amount):
        self._seen_so_far += bytes_amount
        progress = int((self._seen_so_far / self._filesize) * 100)

        # Schedule progress update in the main loop safely
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # Get running loop from FastAPI app (if called from a thread)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        asyncio.run_coroutine_threadsafe(
            self.job_collection.update_one(
                {"job_id": self.job_id},
                {"$set": {"progress": progress}},
            ),
            loop,
        )


# --- Async Upload Function ---
async def upload_to_s3_with_progress(file_data, filename, content_type, job_collection, job_id):
    file_size = len(file_data)
    progress_callback = S3Progress(file_size, job_collection, job_id)

    def _upload():
        try:
            s3_client.upload_fileobj(
                io.BytesIO(file_data),
                AWS_BUCKET_NAME,
                filename,
                ExtraArgs={"ContentType": content_type},
                Callback=progress_callback,
            )
            # Mark job complete
            asyncio.run(
                job_collection.update_one(
                    {"job_id": job_id},
                    {"$set": {"progress": 100, "status": "completed"}},
                )
            )
        except Exception as e:
            # Mark job failed
            asyncio.run(
                job_collection.update_one(
                    {"job_id": job_id},
                    {"$set": {"status": "failed", "error": str(e)}},
                )
            )

    # Run upload in background thread
    await asyncio.to_thread(_upload)
