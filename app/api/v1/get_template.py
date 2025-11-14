from fastapi import APIRouter, HTTPException
from app.db.database import mongo

router = APIRouter()

@router.get("/get/template/{page_count}/{page_no}")
async def get_templates(page_count: int, page_no: int):
    """
    Retrieve templates with pagination.
    - page_count: number of items per page
    - page_no: page number (starting from 1)
    """
    try:
        template_collection = await mongo.get_collection("templates")

        # Ensure valid page numbers
        if page_no < 1 or page_count < 1:
            raise HTTPException(status_code=400, detail="Invalid pagination parameters")

        pipeline = [
            {"$sort": {"created_at": -1}},
            {"$skip": page_count * (page_no - 1)},
            {"$limit": page_count}
        ]

        # Execute aggregation
        templates_cursor = template_collection.aggregate(pipeline)

        templates_list = []
        async for template in templates_cursor:
            template["_id"] = str(template["_id"])
            templates_list.append(template)

        total_count = await template_collection.count_documents({})

        return {
            "templates": templates_list,
            "total_count": total_count,
            "page_no": page_no,
            "page_count": page_count,
            "total_pages": (total_count + page_count - 1) // page_count  
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
