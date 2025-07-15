import json
from aiokafka import AIOKafkaProducer

from domain.repositories.producer import ProducerBase

from settings import KafkaTopics

class KafkaPublisher(ProducerBase):
    def __init__(self, kafka_producer: AIOKafkaProducer):
        self.producer = kafka_producer
        
    def publish_guild_created(self, guild_id: int, guild_tag: str, owner_id: int):
        message = {'guild_id': guild_id, 'tag': guild_tag, 'user_owner_id': owner_id, 'user_amount': 1}
        self.producer.send(
            topic=KafkaTopics.scoreboard_guild_create,
            value=json.dumps(message).encode('utf-8')
        )

    def publish_guild_member_count_changed(self, guild_id: int, user_id: int, members_count: int, action: int):
        message = {'guild_id': guild_id, 'user_id': user_id, 'user_amount': members_count, 'action': action}
        self.producer.send(
            topic=KafkaTopics.scoreboard_guild_count_change,
            value=json.dumps(message).encode('utf-8')
        )
    
    def publish_guild_deleted(self, guild_id: int):
        message = {'guild_id': guild_id}
        self.producer.send(
            topic=KafkaTopics.scoreboard_guild_delete,
            value=json.dumps(message).encode('utf-8')
        )