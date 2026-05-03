import httpx
import asyncio
import json
from datetime import datetime

# Test questions and expected themes
EVAL_DATASET = [
    {
        "question": "What is machine learning?",
        "expected_keywords": ["algorithm", "data", "model", "learning", "training"],
        "user_id": 1
    },
    {
        "question": "Explain microservices architecture",
        "expected_keywords": ["service", "independent", "scalab", "deploy", "api"],
        "user_id": 1
    },
    {
        "question": "What is the difference between SQL and NoSQL?",
        "expected_keywords": ["relational", "schema", "flexible", "document", "query"],
        "user_id": 1
    }
]

AGENT_URL = "http://localhost:8090"

async def evaluate_answer(question: str, answer: str, expected_keywords: list) -> dict:
    keyword_hits = sum(
        1 for kw in expected_keywords
        if kw.lower() in answer.lower()
    )
    keyword_score = (keyword_hits / len(expected_keywords)) * 10

    length_score = min(10, len(answer) / 100)

    final_score = (keyword_score * 0.7) + (length_score * 0.3)

    return {
        "keyword_score": round(keyword_score, 2),
        "length_score": round(length_score, 2),
        "final_score": round(final_score, 2),
        "keyword_hits": keyword_hits,
        "total_keywords": len(expected_keywords),
        "answer_length": len(answer)
    }

async def run_evals():
    print("=" * 60)
    print("StudyMate AI — Evaluation Report")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = []
    total_score = 0

    async with httpx.AsyncClient(timeout=120) as client:
        for i, test_case in enumerate(EVAL_DATASET):
            print(f"\n[{i+1}/{len(EVAL_DATASET)}] Testing: {test_case['question'][:50]}...")

            try:
                response = await client.post(
                    f"{AGENT_URL}/agent/ask",
                    json={
                        "question": test_case["question"],
                        "user_id": test_case["user_id"]
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "")
                    agent_score = data.get("evaluation_score", 0)

                    eval_result = await evaluate_answer(
                        test_case["question"],
                        answer,
                        test_case["expected_keywords"]
                    )

                    eval_result["question"] = test_case["question"]
                    eval_result["agent_score"] = agent_score
                    eval_result["status"] = "success"

                    results.append(eval_result)
                    total_score += eval_result["final_score"]

                    print(f"  Agent Score: {agent_score}/10")
                    print(f"  Keyword Score: {eval_result['keyword_score']}/10")
                    print(f"  Final Score: {eval_result['final_score']}/10")
                else:
                    print(f"  ERROR: {response.status_code}")
                    results.append({
                        "question": test_case["question"],
                        "status": "failed",
                        "final_score": 0
                    })

            except Exception as e:
                print(f"  EXCEPTION: {e}")
                results.append({
                    "question": test_case["question"],
                    "status": "error",
                    "final_score": 0,
                    "error": str(e)
                })

    avg_score = total_score / len(EVAL_DATASET)

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {len(EVAL_DATASET)}")
    print(f"Average Score: {round(avg_score, 2)}/10")
    print(f"Passed (>=5): {sum(1 for r in results if r.get('final_score', 0) >= 5)}")
    print(f"Failed (<5): {sum(1 for r in results if r.get('final_score', 0) < 5)}")

    with open("eval_results.json", "w") as f:
        json.dump({
            "date": datetime.now().isoformat(),
            "average_score": round(avg_score, 2),
            "results": results
        }, f, indent=2)

    print("\nResults saved to eval_results.json")
    return results

if __name__ == "__main__":
    asyncio.run(run_evals())