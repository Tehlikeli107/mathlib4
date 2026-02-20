#!/usr/bin/env python3
import sys
import time
import subprocess
import os

LOG_FILE = "benchmark_log.txt"
JSON_OUTPUT = "benchmark_output.json"
NUM_LINES = 500000

def generate_log_file(filename, num_lines):
    print(f"Generating {num_lines} lines...")
    with open(filename, 'w') as f:
        for i in range(1, num_lines + 1):
            f.write(f"✔ [{i}/{num_lines}] Built Mathlib.Module.{i}\n")

def run_benchmark():
    if not os.path.exists(LOG_FILE):
        generate_log_file(LOG_FILE, NUM_LINES)

    print(f"Running benchmark on {LOG_FILE}...")
    start_time = time.time()

    # Run the wrapper, redirecting stdout to /dev/null to avoid terminal I/O or memory buffering overhead
    # We want to measure the processing time of the wrapper script.
    cmd = ["python3", "scripts/lake-build-wrapper.py", JSON_OUTPUT, "cat", LOG_FILE]

    with open(os.devnull, 'w') as devnull:
        process = subprocess.run(cmd, stdout=devnull, stderr=subprocess.PIPE, text=True)

    end_time = time.time()
    duration = end_time - start_time

    print(f"Time taken: {duration:.4f} seconds")

    if process.returncode != 0:
        print("Error running benchmark:")
        print(process.stderr)

    # Clean up
    if os.path.exists(JSON_OUTPUT):
        os.remove(JSON_OUTPUT)

if __name__ == "__main__":
    run_benchmark()
