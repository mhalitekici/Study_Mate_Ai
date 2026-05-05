from app.core.database import interactions_collection
from datetime import datetime, timedelta

async def heuristic_recommend(user_id: int, top_k: int = 5) -> list[dict]:
    try:
        week_ago = datetime.utcnow() - timedelta(days=7)

        pipeline = [
            {"$match": {"timestamp": {"$gte": week_ago}}},
            {"$group": {
                "_id": "$topic",
                "count": {"$sum": 1},
                "example": {"$first": "$question"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": top_k}
        ]

        results = await interactions_collection.aggregate(pipeline).to_list(length=top_k)

        recommendations = []
        for r in results:
            recommendations.append({
                "type": "heuristic",
                "topic": r["_id"],
                "example_question": r["example"][:100],
                "popularity_score": r["count"],
                "reason": "Most popular topic this week"
            })

        return recommendations

    except Exception as e:
        print(f"[Heuristic] Error: {e}")
        return []

async def cold_start_recommend() -> list[dict]:
    return [
        {
            "type": "cold_start",
            "topic": "Microservices Architecture",
            "example_question": "What is microservices architecture?",
            "reason": "Essential topic for software engineering"
        },
        {
            "type": "cold_start",
            "topic": "Message Brokers",
            "example_question": "What is Kafka and why use it?",
            "reason": "Essential topic for distributed systems"
        },
        {
            "type": "cold_start",
            "topic": "AI/ML",
            "example_question": "How does RAG work?",
            "reason": "Essential topic for modern AI systems"
        },
        {
            "type": "cold_start",
            "topic": "Databases",
            "example_question": "What is the difference between SQL and NoSQL?",
            "reason": "Essential topic for backend development"
        },
        {
            "type": "cold_start",
            "topic": "Containerization",
            "example_question": "What is Docker and why use containers?",
            "reason": "Essential topic for DevOps"
        }
    ]