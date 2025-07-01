from services.chat_service import MongoChatRepository
import os

mongo_repo = MongoChatRepository(
    mongo_uri=os.getenv("MONGODB_URI", "mongodb://lesta-games-mongodb:27017"),
    db_name="guilds_chat",
    collection_name="messages"
)