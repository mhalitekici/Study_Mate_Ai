#!/bin/bash

HOST=${1:-"http://localhost:8000"}
USERS=${2:-10}
SPAWN_RATE=${3:-2}
RUN_TIME=${4:-"60s"}

echo "Starting load test..."
echo "Host: $HOST"
echo "Users: $USERS"
echo "Spawn Rate: $SPAWN_RATE/s"
echo "Duration: $RUN_TIME"

locust \
  -f locustfile.py \
  --host=$HOST \
  --users=$USERS \
  --spawn-rate=$SPAWN_RATE \
  --run-time=$RUN_TIME \
  --headless \
  --html=load_test_report.html \
  --csv=load_test_results

echo "Load test completed!"
echo "Report saved to load_test_report.html"