from motor.motor_asyncio import AsyncIOMotorClient
from db.mongo.chat import MongoChatMessage
from bson import ObjectId

class MongoChatRepository:
    def __init__(self, mongo_uri: str, db_name: str = "chat_db", collection_name: str = "messages"):
        self.client = AsyncIOMotorClient(mongo_uri)
        self.collection = self.client[db_name][collection_name]

    async def save_message(self, message_data: dict) -> MongoChatMessage:
        result = await self.collection.insert_one(message_data)
        message_data["_id"] = result.inserted_id
        return MongoChatMessage(**message_data)

    async def get_messages_by_guild(self, guild_id: int, limit: int = 50):
        cursor = self.collection.find({"guild_id": guild_id}).sort("timestamp", -1).limit(limit)
        return [MongoChatMessage(**doc) async for doc in cursor]



# from motor.motor_asyncio import AsyncIOMotorClient
# from settings import settings
#
# class MongoChatRepository:
#     def __init__(self):
#         self.client = AsyncIOMotorClient(settings.mongodb_uri)
#         self.collection = self.client[settings.mongodb_database]["chat_messages"]
#
#     async def get_last_messages(self, guild_id: int, limit: int = 20):
#         cursor = self.collection.find({"guild_id": guild_id}).sort("timestamp", -1).limit(limit)
#         return list(reversed(await cursor.to_list(length=limit)))
#
#     async def save_message(self, message_data: dict):
#         result = await self.collection.insert_one(message_data)
#         message_data["_id"] = result.inserted_id
#         return message_data