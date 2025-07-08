from aiokafka import AIOKafkaConsumer
from fastapi import FastAPI
import json
from infra.cache.redis_instance import redis

from settings import settings, KafkaTopics, KAFKA_GROUP_ID


async def consume_guild_declare_responses(app: FastAPI):
    consumer = AIOKafkaConsumer(
        KafkaTopics.auth_guild_war_declare_response_guild,  # <- Твой топик
        bootstrap_servers=settings.kafka_service,
        group_id=KAFKA_GROUP_ID,
        enable_auto_commit=True,
        auto_offset_reset="earliest"
    )

    await consumer.start()
    print(f"Kafka consumer started: {KafkaTopics.auth_guild_war_declare_response_guild}")
    try:
        async for msg in consumer:
            try:
                data = json.loads(msg.value.decode("utf-8"))

                correlation_id = data.get("correlation_id")
                success = data.get("success")

                if correlation_id is None:
                    print("[WARN] correlation_id not found in message")
                    continue

                # Ключ и значение
                key = f"rage-response:{correlation_id}"
                value = "true" if success else "false"

                await redis.redis.set(key, value)

                print(f"[Kafka->Redis] Stored result for {correlation_id}: {value}")

            except Exception as e:
                print(f"[Kafka] Failed to process message: {e}")

    finally:
        await consumer.stop()
        print(f"Kafka consumer stopped: {KafkaTopics.auth_guild_war_declare_response_guild}")