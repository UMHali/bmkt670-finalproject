import subprocess
import sys

# Scripts to run, in order.
steps = [
    "etl/check_retrosheet.py",
    "etl/check_statcast.py",
    "etl/extract_weather.py",
    "etl/transform.py",
    "etl/load.py",
    "etl/quality_checks.py"
]

for step in steps:
    print(f"\n=== Running {step} ===")

    result = subprocess.run(
    [sys.executable, step],
    check=False
    )

    if result.returncode != 0:
        print(
            f"\nStopped: {step} failed. "
            "Fix it and run again."
        )
        sys.exit(1)

print("\nPipeline finished.")