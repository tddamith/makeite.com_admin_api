from fastapi import APIRouter, HTTPException,BackgroundTasks
from datetime import datetime
import asyncio
from app.db.database import mongo
from app.api.v1.schemas.template_schema import TemplateUpdateBase
from app.utils.file_uploader import upload_to_s3_with_progress
import base64
from bson import ObjectId

router = APIRouter()


@router.put("/update/template/by/{template_id}")
async def update_template_zip(
    template_id: str,
    new_file: TemplateUpdateBase,  # should contain base64 + filename
    background_tasks: BackgroundTasks
):
    """
    Replace existing template ZIP in S3 (overwrite).
    """
    try:
        template_collection = await mongo.get_collection("templates")
        job_collection = await mongo.get_collection("jobs")

        template_data = await template_collection.find_one({"template_id": template_id})
        if not template_data:
            raise HTTPException(status_code=404, detail="Template not found")

        file_url = template_data.get("file_url")
        if not file_url:
            raise HTTPException(status_code=400, detail="Template has no file_url")

        # Extract S3 key from URL
        s3_key = file_url.split(f".amazonaws.com/")[-1]

        # Prepare new file data
        if not new_file.base64_data or not new_file.filename:
            raise HTTPException(status_code=400, detail="Missing file data")

        base64_str = new_file.base64_data.split(",")[-1]
        file_bytes = base64.b64decode(base64_str)

        if not new_file.filename.lower().endswith(".zip"):
            raise HTTPException(status_code=400, detail="Only zip files allowed")

        # Create new job for progress tracking
        job_id = str(ObjectId())
        job_data = {
            "job_id": job_id,
            "template_id": template_id,
            "type": "update_zip",
            "status": "queued",
            "progress": 0,
            "created_at": datetime.utcnow()
        }

        await job_collection.insert_one(job_data)

        await template_collection.update_one(
            {"template_id": template_id},
            {"$set": {"template_name": new_file.template_name, "category_id":new_file.category_id,"sub_category_id":new_file.sub_category_id,"cover_image":new_file.cover_image,"type":new_file.type}},)

        # Upload (overwrite existing file)
        background_tasks.add_task(
            asyncio.create_task(
                upload_to_s3_with_progress(
                    file_bytes,
                    s3_key,                      # SAME FILE NAME → Overwrite
                    "application/zip",
                    job_collection,
                    job_id,
                    overwrite=True,
                )
            )
        )

        return {
            "status": True,
            "message": "Template ZIP update started",
            "data": {
                "template_id": template_id,
                "job_id": job_id,
                "file_url": file_url,  # same since overwritten
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error updating: {str(e)}")