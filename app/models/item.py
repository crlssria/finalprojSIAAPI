# backend/app/models/item.py

from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

class Item(BaseModel):
    id: Optional[ObjectId] = Field(alias="_id")
    name: str
    description: Optional[str] = None
    owner_id: ObjectId

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    @classmethod
    async def create_item(cls, db, item_data):
        item = cls(**item_data)
        await db.items.insert_one(item.dict(by_alias=True))
        return item

    @classmethod
    async def get_items_by_owner(cls, db, owner_id):
        items = await db.items.find({"owner_id": owner_id}).to_list(None)
        return [cls(**item) for item in items]

    @classmethod
    async def get_item_by_id(cls, db, item_id):
        item = await db.items.find_one({"_id": ObjectId(item_id)})
        if item:
            return cls(**item)
        return None

    @classmethod
    async def delete_item(cls, db, item_id):
        result = await db.items.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count == 1
