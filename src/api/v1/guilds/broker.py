from faststream.kafka import KafkaBroker

from settings import settings

broker = KafkaBroker(
    settings.kafka_service,
    # consumer_settings={
    #     'enable_auto_commit': True,
    #     'auto_offset_reset': 'latest'
    # }
)