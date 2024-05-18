from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

class Item(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str
    price: float

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ItemCreate(BaseModel):
    name: str
    price: float
