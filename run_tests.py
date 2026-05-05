import subprocess
import sys
import os

services = [
    ("Auth Service", "services/auth-service"),
    ("Material Service", "services/material-service"),
    ("AI Service", "services/ai-service"),
    ("Memory Service", "services/memory-service"),
    ("RecSys Service", "services/recsys-service"),
    ("Multi-Agent", "agents/multi-agent"),
]

results = []

for name, path in services:
    print(f"\n{'='*50}")
    print(f"Testing: {name}")
    print(f"{'='*50}")
    
    venv_python = os.path.join(path, "venv", "Scripts", "python.exe")
    
    if not os.path.exists(venv_python):
        print(f"SKIP: No venv found at {venv_python}")
        results.append((name, "SKIPPED"))
        continue
    
    result = subprocess.run(
        [venv_python, "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=path,
        capture_output=False
    )
    
    if result.returncode == 0:
        results.append((name, "PASSED"))
    else:
        results.append((name, "FAILED"))

print(f"\n{'='*50}")
print("TEST SUMMARY")
print(f"{'='*50}")
for name, status in results:
    emoji = "✅" if status == "PASSED" else "❌" if status == "FAILED" else "⏭️"
    print(f"{emoji} {name}: {status}")