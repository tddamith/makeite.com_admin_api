from pydantic import BaseModel
from typing import Optional,Dict,List

class TemplateBase(BaseModel):
    template_name: str
    # latest_version: Optional[str]
    category_id: str
    sub_category_id:str
    base64_data: str
    filename: str
    type: Optional[str] 

class UpdateTemplateBase(BaseModel):
    cover_image:str
    type:str
