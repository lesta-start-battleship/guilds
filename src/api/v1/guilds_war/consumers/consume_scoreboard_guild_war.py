from aiokafka import AIOKafkaConsumer
from fastapi import FastAPI
import json
from infra.cache.redis_instance import redis

from settings import settings, KafkaTopics, KAFKA_GROUP_ID
from .finalize_war import finalize_war

async def consume_scoreboard_guild_war(app: FastAPI):
    consumer = AIOKafkaConsumer(
        KafkaTopics.scoreboard_guild_war,
        bootstrap_servers=settings.kafka_service,
        group_id=KAFKA_GROUP_ID,
        enable_auto_commit=True,
        auto_offset_reset="earliest"
    )

    await consumer.start()
    print(f"Kafka consumer started: {KafkaTopics.scoreboard_guild_war}")
    try:
        async for msg in consumer:
            try:
                data = json.loads(msg.value.decode("utf-8"))

                correlation_id = data.get("correlation_id")
                id_guild_war = data.get("id_guild_war")

                redis_key = f"war-correlation:{id_guild_war}"
                redis_correlation_id = await redis.redis.get(redis_key)

                if redis_correlation_id:
                    redis_correlation_id = redis_correlation_id.decode("utf-8")

                    if redis_correlation_id == correlation_id:
                        print(f"[Redis] correlation_id match for war_id={id_guild_war}")

                        # Завершаем войну
                        await finalize_war(id_guild_war)

                        # Удаляем ключ
                        await redis.redis.delete(redis_key)
                        print(f"[Redis] Deleted key: {redis_key}")
                    else:
                        print(f"[WARN] correlation_id mismatch for war_id={id_guild_war}")
                else:
                    print(f"[WARN] Redis key not found: {redis_key}")

                # Удаляем rage-response:{correlation_id}
                rage_key = f"rage-response:{correlation_id}"
                if await redis.redis.exists(rage_key):
                    await redis.redis.delete(rage_key)
                    print(f"[Redis] Deleted key: {rage_key}")
                else:
                    print(f"[Redis] Key not found: {rage_key}")

            except Exception as e:
                print(f"[Kafka] Failed to process message: {e}")

    finally:
        await consumer.stop()
        print(f"Kafka consumer stopped: {KafkaTopics.scoreboard_guild_war}")