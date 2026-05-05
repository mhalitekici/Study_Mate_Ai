from app.core.database import interactions_collection
from datetime import datetime

async def log_interaction(user_id: int, question: str, topic: str = None):
    await interactions_collection.insert_one({
        "user_id": user_id,
        "question": question,
        "topic": topic or extract_topic(question),
        "timestamp": datetime.utcnow()
    })

def extract_topic(question: str) -> str:
    keywords = {
        "kafka": "Message Brokers",
        "rabbitmq": "Message Brokers",
        "redis": "Caching",
        "cache": "Caching",
        "docker": "Containerization",
        "kubernetes": "Orchestration",
        "microservice": "Microservices",
        "database": "Databases",
        "sql": "Databases",
        "nosql": "Databases",
        "mongodb": "Databases",
        "rag": "AI/ML",
        "llm": "AI/ML",
        "machine learning": "AI/ML",
        "api": "API Design",
        "rest": "API Design",
        "python": "Programming",
        "recursion": "Programming",
    }
    question_lower = question.lower()
    for keyword, topic in keywords.items():
        if keyword in question_lower:
            return topic
    return "General"

async def collaborative_recommend(user_id: int, top_k: int = 5) -> list[dict]:
    try:
        user_interactions = await interactions_collection.find(
            {"user_id": user_id}
        ).to_list(length=100)

        if not user_interactions:
            return []

        user_topics = set(i.get("topic") for i in user_interactions)

        all_interactions = await interactions_collection.find(
            {"user_id": {"$ne": user_id}}
        ).to_list(length=1000)

        similar_users = {}
        for interaction in all_interactions:
            other_user = interaction["user_id"]
            topic = interaction.get("topic")
            if topic in user_topics:
                similar_users[other_user] = similar_users.get(other_user, 0) + 1

        if not similar_users:
            return []

        top_similar = sorted(similar_users.items(), key=lambda x: x[1], reverse=True)[:3]
        top_user_ids = [u[0] for u in top_similar]

        similar_interactions = await interactions_collection.find(
            {
                "user_id": {"$in": top_user_ids},
                "topic": {"$nin": list(user_topics)}
            }
        ).to_list(length=50)

        topic_counts = {}
        for interaction in similar_interactions:
            topic = interaction.get("topic", "General")
            q = interaction.get("question", "")
            if topic not in topic_counts:
                topic_counts[topic] = {"count": 0, "example": q}
            topic_counts[topic]["count"] += 1

        recommendations = []
        for topic, data in sorted(topic_counts.items(), key=lambda x: x[1]["count"], reverse=True)[:top_k]:
            recommendations.append({
                "type": "collaborative",
                "topic": topic,
                "example_question": data["example"][:100],
                "score": data["count"],
                "reason": f"Students with similar interests studied this topic"
            })

        return recommendations

    except Exception as e:
        print(f"[Collaborative] Error: {e}")
        return []