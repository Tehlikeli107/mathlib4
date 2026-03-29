import time
import subprocess

start = time.time()
subprocess.run(['python3', 'scripts/downstream-tags.py', 'v4.6.0-rc1'], stdout=subprocess.DEVNULL)
end = time.time()

print(f"Elapsed time: {end - start:.2f} seconds")
