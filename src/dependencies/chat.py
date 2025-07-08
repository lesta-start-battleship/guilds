from infra.repositories.chat_mongo_repo import MongoChatRepository
from settings import settings

mongo_repo = MongoChatRepository(
    mongo_uri=settings.mongo_db,
    db_name="guilds_chat",
    collection_name="messages"
)