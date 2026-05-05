from app.core.config import settings
import json

def publish_event(topic: str, event: dict):
    try:
        from kafka import KafkaProducer
        producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        producer.send(topic, event)
        producer.flush()
        producer.close()
        print(f"[Kafka Producer] Event published to {topic}: {event}")
    except Exception as e:
        print(f"[Kafka Producer] Failed to publish event: {e}")
