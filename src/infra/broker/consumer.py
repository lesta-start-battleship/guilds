import json
from aiokafka import AIOKafkaConsumer

from services.guild_ import GuildService
from services.guild_request_ import RequestService
from services.member_ import MemberService


class KafkaListener:
    def __init__(
        self,
        kafka_consumer: AIOKafkaConsumer,
        member_service: MemberService,
        guild_service: GuildService,
        request_service: RequestService
        ):
        self.kafka_consumer = kafka_consumer
        self.member_service = member_service
        self.guild_service = guild_service
        self.request_service = request_service

    async def listen(self):
        await self.kafka_consumer.start()
        try:
            async for msg in self.kafka_consumer:
                topic = msg.topic
                payload = json.loads(msg.value.decode('utf-8'))

                if topic == 'prod.auth.fact.username-change.1':
                    await self.member_service.on_username_changed(
                        user_id=payload['user_id'],
                        username=payload['username']
                    )
                    
                    await self.request_service.on_username_changed(
                        user_id=payload['user_id'],
                        username=payload['username']
                    )

                elif topic == 'prod.auth.fact.user-delete.1':
                    if not await self.guild_service.on_user_deleted(payload['user_id']):
                        if not await self.member_service.on_user_deleted(payload['user_id']):
                            await self.request_service.on_user_deleted(payload['user_id'])
                
        finally:
            await self.kafka_consumer.stop()