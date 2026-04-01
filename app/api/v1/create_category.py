from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime
from bson import ObjectId
from app.db.database import mongo
from app.api.v1.schemas.category_schema import CategoryBase
from app.utils.validation import validate_signature
from datetime import datetime,timedelta
from typing import Optional


router = APIRouter()


#create category
@router.post("/create/new/category")
async def create_category(category: CategoryBase):
    """Create a new category."""
    try:
        category_dict = category.model_dump()

        category_collection = await mongo.get_collection("categories")
        
        # Check if category with the same name already exists
        existing_category = await category_collection.find_one({"category_name": category.category_name})
        if existing_category:
            return {"status": False ,"message": "Category with this name already exists."}
        
        category_data = {
            "category_id": str(ObjectId()),
            "category_name": category_dict["category_name"],
            "sub_category": category_dict["sub_category"],
            "status": "new",
            "created_at": datetime.utcnow()           
        }
        
        result = await category_collection.insert_one(category_data)
        
        return {"status": True ,"message": "Category created successfully", "category_id": str(result.inserted_id)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
#get all categories
@router.get("/get/all/categories")
async def get_categories():
    """Retrieve all categories."""
    try:
        category_collection = await mongo.get_collection("categories")
        
        categories_cursor = category_collection.find({})
        categories = []
        async for category in categories_cursor:
            category["_id"] = str(category["_id"])  # Convert ObjectId to string
            categories.append(category)
        
        return {"status": True, "categories": categories}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
#update category
@router.put("/update/category/by/{category_id}")
async def update_category(category_id: str, category: CategoryBase):
    """Update an existing category."""
    try:
        category_data = category.model_dump()
        category_collection = await mongo.get_collection("categories")
        
        update_data = {
            "category_name": category_data["category_name"],
            "sub_category": category_data["sub_category"],
            "updated_at": datetime.utcnow()
        }
        
        result = await category_collection.update_one(
            {"category_id": category_id},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Category not found.")
        return {"message": "Category updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
#delete category
@router.delete("/delete/category/by/{category_id}")
async def delete_category(category_id: str):
    """Delete a category."""
    try:
        category_collection = await mongo.get_collection("categories")
        
        result = await category_collection.delete_one({"category_id": category_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Category not found.")
        return {"message": "Category deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


#get sub categories by category_id
@router.get("/get/sub-categories/by/{category_id}") 
async def get_sub_categories(category_id: str):
    """Retrieve sub-categories by category ID."""
    try:
        category_collection = await mongo.get_collection("categories")
        
        category = await category_collection.find_one({"category_id": category_id})
        sub_categories = category.get("sub_category", []) if category else []
        
        return {"sub_categories": sub_categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")