import requests
import time

question = "What is C++?"
user_id = 2

print("=== First Request ===")
start = time.time()
response = requests.post(
    "http://localhost:8110/agent/ask",
    json={"question": question, "user_id": user_id}
)
elapsed = round(time.time() - start, 2)
data = response.json()
print(f"Time: {elapsed}s")
print(f"Cached: {data.get('cached')}")
print(f"Answer: {str(data.get('answer', ''))[:100]}")

print("\n=== Second Request (should be cached) ===")
start = time.time()
response = requests.post(
    "http://localhost:8110/agent/ask",
    json={"question": question, "user_id": user_id}
)
elapsed = round(time.time() - start, 2)
data = response.json()
print(f"Time: {elapsed}s")
print(f"Cached: {data.get('cached')}")
print(f"Answer: {str(data.get('answer', ''))[:100]}")