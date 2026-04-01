from pydantic import BaseModel
from typing import Optional,Dict,List


class Sub_category(BaseModel):
    Sub_category_id:Optional[str]
    Sub_category_name:Optional[str]

class CategoryBase(BaseModel):
    icon_name: str
    category_name: str
    sub_category:List[Sub_category]
    
