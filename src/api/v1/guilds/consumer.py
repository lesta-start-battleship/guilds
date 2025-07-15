from fastapi import Body
from faststream import Depends

from .broker import broker
from dependencies.services import get_lifecycle_service
from services.guild_lifecycle import LifecycleService

from settings import KAFKA_GROUP_ID, KafkaTopics

from pydantic import BaseModel


class UserDeleted(BaseModel):
    user_id: int

class UsernameChanged(UserDeleted):
    username: str

# @broker.subscriber(KafkaTopics.auth_user_delete, group_id=KAFKA_GROUP_ID)
# async def handle_user_delete(
#     event: dict,
#     service: LifecycleService = Depends(get_lifecycle_service)
# ):
#     player_id = int(event['user_id'])
#     await service.on_user_deleted(player_id)

@broker.subscriber(KafkaTopics.auth_user_delete, group_id=KAFKA_GROUP_ID)
async def handle_guild_delete(
    event: dict,
    service: LifecycleService = Depends(get_lifecycle_service)
):
    player_id = int(event['user_id'])
    await service.on_user_deleted(player_id)


@broker.subscriber(KafkaTopics.auth_username_change, group_id=KAFKA_GROUP_ID)
async def handle_username_change(
    event: UsernameChanged,
    service: LifecycleService = Depends(get_lifecycle_service)
):
    player_id = event.user_id
    new_nickname = event.username
    print('akakkaakak')
    await service.on_username_changed(player_id, new_nickname)