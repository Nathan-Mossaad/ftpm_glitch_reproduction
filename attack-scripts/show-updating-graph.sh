#!/usr/bin/env bash

while true; do
  # start the process in background
  uv run duration_test_plot.py &
  pid=$!

  # wait 1 second
  sleep 1

  # terminate the process gracefully, then force kill if still running
  kill "$pid" 2>/dev/null || true
  sleep 0.2
  if kill -0 "$pid" 2>/dev/null; then
    kill -9 "$pid" 2>/dev/null || true
  fi

done
