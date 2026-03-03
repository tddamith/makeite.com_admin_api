from fastapi import APIRouter, Depends, Request
from fastapi import APIRouter, Depends, Request
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
 # your auth dependency

 
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")



s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)

async def get_all_media(user_inputs: dict):
    key = user_inputs.get("key", "")

    params = {
        "Bucket": AWS_BUCKET_NAME,
    }

    if key:
        params["Prefix"] = key  # equivalent to folder filtering

    try:
        response = s3.list_objects_v2(**params)

        contents = response.get("Contents", [])

        return { 
            "status": True,
            "message": "",
            "data": contents
        }


    except Exception as e:
        return {
            "status": False,
            "message": str(e),
            "data": []
        }

@router.get("/get/all/media")
async def get_all_media_route():
    try:
        data = await get_all_media({})
        return data
    except Exception as e:
        return {
            "status": False,
            "message": str(e),
            "data": []
        }