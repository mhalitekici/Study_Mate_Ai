import httpx
import asyncio
import time
import json
from datetime import datetime
from langfuse import Langfuse

OLLAMA_URL = "http://localhost:11434"
LANGFUSE_PUBLIC_KEY = "pk-lf-4ea992ff-0d02-48ae-b1cc-c418d5819f7c"
LANGFUSE_SECRET_KEY = "sk-lf-e8ad74b9-449f-4f49-9612-525365c132db"
LANGFUSE_HOST = "http://localhost:3001"

langfuse = Langfuse(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY,
    host=LANGFUSE_HOST
)

TEST_QUESTIONS = [
    "Explain the concept of recursion in programming with an example.",
    "What is the difference between microservices and monolithic architecture?",
    "How does RAG (Retrieval-Augmented Generation) work?"
]

MODELS = ["qwen2.5:latest", "qwen3:8b", "deepseek-coder:6.7b"]

async def test_model(model: str, question: str) -> dict:
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": question,
                    "stream": False
                }
            )
            
            raw = response.text
            if not raw:
                return {"model": model, "question": question, "status": "error", "error": "Empty response"}
            
            result = json.loads(raw)
            latency = time.time() - start
            answer = result.get("response", "")
            prompt_tokens = result.get("prompt_eval_count", 0)
            completion_tokens = result.get("eval_count", 0)

            generation = langfuse.generation(
                name=f"model-comparison-{model}",
                model=model,
                input=question,
                output=answer,
                usage={
                    "input": prompt_tokens,
                    "output": completion_tokens,
                    "total": prompt_tokens + completion_tokens
                },
                metadata={
                    "latency_seconds": round(latency, 2),
                    "tokens_per_second": round(completion_tokens / latency, 2) if latency > 0 else 0,
                }
            )

            return {
                "model": model,
                "question": question,
                "latency_seconds": round(latency, 2),
                "answer_length": len(answer),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "tokens_per_second": round(completion_tokens / latency, 2) if latency > 0 else 0,
                "status": "success"
            }

    except Exception as e:
        return {
            "model": model,
            "question": question,
            "latency_seconds": round(time.time() - start, 2),
            "status": "error",
            "error": str(e)
        }

async def run_comparison():
    print("=" * 70)
    print("StudyMate AI — Model Comparison (with Langfuse tracking)")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    all_results = []

    for question in TEST_QUESTIONS:
        print(f"\nQuestion: {question[:60]}...")
        print("-" * 70)

        for model in MODELS:
            print(f"  Testing {model}...", end=" ", flush=True)
            result = await test_model(model, question)
            all_results.append(result)

            if result["status"] == "success":
                print(f"✓ {result['latency_seconds']}s | {result['total_tokens']} tokens | {result['tokens_per_second']} t/s")
            else:
                print(f"✗ Error: {result.get('error', 'Unknown')}")

    print("\n" + "=" * 70)
    print("FINAL SUMMARY PER MODEL")
    print("=" * 70)

    for model in MODELS:
        model_results = [r for r in all_results if r["model"] == model and r["status"] == "success"]
        if model_results:
            avg_latency = sum(r["latency_seconds"] for r in model_results) / len(model_results)
            avg_tokens = sum(r["total_tokens"] for r in model_results) / len(model_results)
            avg_tps = sum(r["tokens_per_second"] for r in model_results) / len(model_results)
            print(f"\n{model}:")
            print(f"  Avg Latency    : {round(avg_latency, 2)}s")
            print(f"  Avg Tokens     : {round(avg_tokens, 0)}")
            print(f"  Avg Tokens/sec : {round(avg_tps, 2)}")

    langfuse.flush()

    with open("model_comparison_results.json", "w") as f:
        json.dump({
            "date": datetime.now().isoformat(),
            "models_tested": MODELS,
            "results": all_results
        }, f, indent=2)

    print("\nResults saved to model_comparison_results.json")
    print("Check Langfuse at http://localhost:3001 for detailed traces!")

if __name__ == "__main__":
    asyncio.run(run_comparison())