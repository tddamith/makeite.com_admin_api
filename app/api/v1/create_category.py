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
        category_collection = await mongo.get_collection("categories")
        
        # Check if category with the same name already exists
        existing_category = await category_collection.find_one({"category_name": category.category_name})
        if existing_category:
            raise HTTPException(status_code=400, detail="Category with this name already exists.")
        
        category_data = {
            "category_id": str(ObjectId()),
            "icon_name": category.icon_name,
            "category_name": category.category_name,
            "sub_category":category.sub_category,
            "status": "new",
            "created_at": datetime.utcnow()
           
        }
        
        result = await category_collection.insert_one(category_data)
        
        return {"message": "Category created successfully", "category_id": str(result.inserted_id)}
    
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
        
        return {"categories": categories}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
#update category
@router.put("/update/category/by/{category_id}")
async def update_category(category_id: str, category: CategoryBase):
    """Update an existing category."""
    try:
        category_collection = await mongo.get_collection("categories")
        
        update_data = {
            "icon_name": category.icon_name,
            "category_name": category.category_name,
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
@router.put("/update/sub-categories/by/{category_id}") 
async def update_sub_categories(category_id: str):
    """Retrieve sub-categories by category ID."""
    try:
        sub_category_collection = await mongo.get_collection("categories")
        
        sub_categories_cursor = sub_category_collection.find({"category_id": category_id})
        sub_categories = sub_categories_cursor["sub_category"] if sub_categories_cursor else []
        async for sub_category in sub_categories_cursor:
            sub_category["_id"] = str(sub_category["_id"])  
            sub_categories.append(sub_category)
        
        return {"sub_categories": sub_categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")