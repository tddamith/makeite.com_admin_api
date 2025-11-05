from fastapi import APIRouter, HTTPException
from app.db.database import mongo


# Initialize FastAPI router
router = APIRouter()

@router.get("get/progress/by/{job_id}")

async def get_job_progress(job_id:str):
    try:
        print("jobid",job_id)
        job_collection = await mongo.get_collection("jobs")

        jobs_cursor = job_collection.find_one({"job_id": job_id})        
        
        jobs_cursor["_id"] = str(jobs_cursor["_id"])         
        
        return {"progress": jobs_cursor["progress"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")