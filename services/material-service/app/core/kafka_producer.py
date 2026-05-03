from kafka import KafkaProducer
from app.core.config import settings
import json

producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_event(topic: str, event: dict):
    producer.send(topic, event)
    producer.flush()