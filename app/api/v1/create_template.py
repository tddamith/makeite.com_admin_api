from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime
from bson import ObjectId
from app.db.database import mongo
from app.api.v1.schemas.template_schema import TemplateBase

router = APIRouter()

#create template
@router.post("/create/new/template")
async def create_template(template: TemplateBase):
    """Create a new template."""
    try:
        template_collection = await mongo.get_collection("templates")
        job_collection = await mongo.get_collection("jobs")
        
        # Check if template with the same name already exists
        existing_template = await template_collection.find_one({"template_name": template.template_name})
        if existing_template:
            raise HTTPException(status_code=400, detail="Template with this name already exists.")
        
        template_data = {
            "template_id": str(ObjectId()),
            "template_name": template.template_name,
            "latest_version": template.latest_version,
            "status": "draft",
            "created_at": datetime.utcnow()
           
        }

        #job created for upload
        job_data = {
            "job_id": str(ObjectId()),
            "template_id": template_data["template_id"],
            "type":"upload_extract",
            "status":"qeueued",
            "progress":0,
            "created_at": datetime.utcnow()
        }

        
        result = await template_collection.insert_one(template_data)
        res = await job_collection.insert_one(job_data)

        
        
        return {"status": True, "message": "Template created successfully", "data": {"template_id":template_data["template_id"],"job_id":job_data["job_id"]}}
    
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")