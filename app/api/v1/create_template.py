from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime
from bson import ObjectId
from app.db.database import mongo
from app.api.v1.schemas.template_schema import TemplateBase
import base64
import io
from uuid import uuid4
import boto3
import os

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


#create template
@router.post("/create/new/template")
async def create_template(template: TemplateBase):
    """Create a new template (ZIP-based)."""
    try:
        template_collection = await mongo.get_collection("templates")
        job_collection = await mongo.get_collection("jobs")

        # Check for duplicate template name
        existing_template = await template_collection.find_one({"template_name": template.template_name})
        if existing_template:
            raise HTTPException(status_code=400, detail="Template with this name already exists.")

        template_id = str(ObjectId())
        job_id = str(ObjectId())

        template_data = {
            "template_id": template_id,
            "template_name": template.template_name,
            "latest_version": template.latest_version,
            "status": "draft",
            "created_at": datetime.utcnow(),
        }

        job_data = {
            "job_id": job_id,
            "template_id": template_id,
            "type": "upload_extract",
            "status": "queued",
            "progress": 0,
            "created_at": datetime.utcnow(),
        }

        # Insert records
        await template_collection.insert_one(template_data)
        await job_collection.insert_one(job_data)

        # --- File Upload Section ---
        if not template.base64_data or not template.filename or not template.type:
            raise HTTPException(status_code=400, detail="Missing file data.")

        # Support both inline and plain base64
        if "," in template.base64_data:
            base64_str = template.base64_data.split(",")[1]
        else:
            base64_str = template.base64_data

        try:
            file_data = base64.b64decode(base64_str)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid Base64 data provided.")

        file_extension = template.filename.split(".")[-1].lower()
        if file_extension != "zip":
            raise HTTPException(status_code=400, detail="Only .zip files are supported.")

        unique_file_name = f"{uuid4()}.{file_extension}"

        # Upload to S3 (non-blocking helper)
        await s3_client.upload_to_s3(file_data, unique_file_name, template.type)

        file_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_file_name}"
        await template_collection.update_one({"template_id": template_id}, {"$set": {"file_url": file_url}})

        return {
            "status": True,
            "message": "Template created successfully",
            "data": {
                "template_id": template_id,
                "job_id": job_id,
                "file_url": file_url
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
