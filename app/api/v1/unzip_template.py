import zipfile
import io
import requests
from fastapi import APIRouter, HTTPException
from app.db.database import mongo



router = APIRouter()


@router.get("/template/unzip/{templateId}")
async def unzip_template(templateId: str):
    """
    Download ZIP from S3, read content, return HTML/CSS/JS as text.
    """

    try:
        template_collection = await mongo.get_collection("templates")

        template_data = await template_collection.find_one({"template_id": templateId})
        if not template_data:
            raise HTTPException(status_code=404, detail="Template not found")

        file_url = template_data.get("file_url")

        # 1️⃣ Download the zip from S3
        response = requests.get(file_url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=400, 
                detail="Failed to download template ZIP"
            )

        # 2️⃣ Load zip into memory
        zip_bytes = io.BytesIO(response.content)

        html = None
        css = None
        js = None
        theme = None
        manifest = None

        # 3️⃣ Extract files
        with zipfile.ZipFile(zip_bytes, 'r') as zip_ref:
            for file in zip_ref.namelist():
                # Read HTML
                if file.endswith(".html"):
                    html = zip_ref.read(file).decode("utf-8")

                # Read CSS
                if file.endswith(".css"):
                    css = zip_ref.read(file).decode("utf-8")

                # Read JS
                if file.endswith(".js"):
                    js = zip_ref.read(file).decode("utf-8")

                # Optional: theme.json
                if file.endswith("theme.json"):
                    theme = zip_ref.read(file).decode("utf-8")
                
                # Optional: manifest.json
                if file.endswith("manifest.json"):
                    manifest = zip_ref.read(file).decode("utf-8")


        return {
            "status": True if (html and css and js) else False,
            "message": "Success",
            "data": {
                    "html": html,
                    "css": css,
                    "js": js,
                    "theme": theme,
                    "manifest": manifest
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unzip error: {str(e)}")
