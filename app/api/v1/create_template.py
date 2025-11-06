from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
from bson import ObjectId
from app.db.database import mongo
from app.api.v1.schemas.template_schema import TemplateBase,UpdateTemplateBase
from app.utils.file_uploader import s3_client
from app.utils.file_uploader import S3Progress, executor
from app.utils.file_uploader import upload_to_s3_with_progress
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



#create template
@router.post("/create/new/template")
async def create_template(template: TemplateBase,background_tasks: BackgroundTasks):
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
            "category_id":template.category_id,
            "sub_category_id":template.sub_category_id,
            "latest_version": 0,
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
        # if not template.base64_data or not template.filename or not template.type:
        #     raise HTTPException(status_code=400, detail="Missing file data.")

        # if "," in template.base64_data:
        #     base64_str = template.base64_data.split(",")[1]
        # else:
        #     base64_str = template.base64_data

        # try:
        #     file_data = base64.b64decode(base64_str)
        # except Exception:
        #     raise HTTPException(status_code=400, detail="Invalid Base64 data provided.")

        # file_extension = template.filename.split(".")[-1].lower()
        # print("File extension:", file_extension)
        # if file_extension != "zip":
        #     raise HTTPException(status_code=400, detail="Only .zip files are supported.")

        # unique_file_name = f"{uuid4()}.{file_extension}"

        # # Upload with progress tracking
        # await upload_to_s3_with_progress(file_data, unique_file_name, template.type, job_collection, job_id)

        # # Upload done — mark job as completed
        # file_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_file_name}"
        # await template_collection.update_one({"template_id": template_id}, {"$set": {"file_url": file_url}})
        # await job_collection.update_one(
        #     {"job_id": job_id},
        #     {"$set": {"progress": 100, "status": "completed"}}
        # )

        # return {
        #     "status": True,
        #     "message": "Template created and uploaded successfully",
        #     "data": {
        #         "template_id": template_id,
        #         "job_id": job_id,
        #         "file_url": file_url
        #     }
        # }

        # Prepare file
        if not template.base64_data or not template.filename or not template.type:
            raise HTTPException(status_code=400, detail="Missing file data.")

        base64_str = template.base64_data.split(",")[-1]
        file_data = base64.b64decode(base64_str)

        file_extension = template.filename.split(".")[-1].lower()
        if file_extension != "zip":
            raise HTTPException(status_code=400, detail="Only .zip files supported.")

        unique_file_name = f"{uuid4()}.{file_extension}"

         # ✅ Run upload in background (non-blocking)
        background_tasks.add_task(
            upload_to_s3_with_progress,
            file_data,
            unique_file_name,
            template.type,
            job_collection,
            job_id
        )

        # --- Generate File URL ---
        file_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_file_name}"

        # --- Save File URL Early (for preview) ---
        await template_collection.update_one({"template_id": template_id}, {"$set": {"file_url": file_url}})

       

        # ✅ Respond immediately — frontend can start polling now
        return {
            "status": True,
            "message": "Template upload started",
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
    

    
    

@router.put("/update/template/by/{template_id}")
async def create_template(template: UpdateTemplateBase,template_id:str):
    """Create a new template (ZIP-based)."""
    try:
        template_collection = await mongo.get_collection("templates")
        

        # Check for duplicate template name
        existing_template = await template_collection.find_one({"template_id": template_id})
        if not existing_template:
            raise HTTPException(status_code=400, detail="Not Found Template.")
            
         
        cover_image_data = template.cover_image.dict()

        # Insert records
        await template_collection.update_one(
            {"template_id": template_id},
            {
                "$set": {
                    "cover_image": cover_image_data,
                    "type": template.type,
                    "status": "draft",
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        return {
            "status": True,
            "message": "Template update successfully",
            "data": {
                "template_id": template_id,                
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")










# Remove Job when completed progress
@router.delete("/delete/job/{job_id}")
async def delete_job(job_id: str):
    """Delete a job by its ID."""
    try:
        job_collection = await mongo.get_collection("jobs")
        result = await job_collection.delete_one({"job_id": job_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Job not found.")
        return {
            "status": True,
            "message": "Job deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}") 
