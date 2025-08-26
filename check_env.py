import sys

if sys.prefix != sys.base_prefix:
    print(f"Running in a virtual environment: {sys.prefix}")
else:
    print("Running in the base Python environment.")