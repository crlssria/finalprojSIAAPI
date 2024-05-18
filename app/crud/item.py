from typing import List
from app.db.mongodb import mongodb
from app.schemas.item import Item

async def get_items() -> List[Item]:
    items = await mongodb.db.items.find().to_list(1000)
    return items

async def create_item(item: Item) -> Item:
    result = await mongodb.db.items.insert_one(item.dict(by_alias=True))
    item.id = str(result.inserted_id)
    return item
