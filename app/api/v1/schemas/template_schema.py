from pydantic import BaseModel
from typing import Optional,Dict,List

class TemplateBase(BaseModel):
    template_name: str
    latest_version: Optional[str]

