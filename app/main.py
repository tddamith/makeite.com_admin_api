from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.create_category import router as category_router
from app.api.v1.create_sub_category import router as sub_category_router
from app.api.v1.create_template import router as template_router
from app.db.database import connect_all, close_all
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Write logs to a file
        logging.StreamHandler()         # Print logs to the console
    ]
)
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_db():
    # Connect to MongoDB and MySQL during application startup
    await connect_all()
    #asyncio.create_task(auto_sync_impressions(3600))
    #asyncio.create_task(run_task_at_time(auto_sync_impressions, target_hour=3, target_minute=0))
@app.on_event("shutdown")
async def shutdown_db():
    # Close database connections during application shutdown
    await close_all()



app.include_router(category_router, prefix="/api/v1", tags=["Categories"])
app.include_router(sub_category_router, prefix="/api/v1", tags=["Sub-Categories"])
app.include_router(template_router, prefix="/api/v1", tags=["Templates"])