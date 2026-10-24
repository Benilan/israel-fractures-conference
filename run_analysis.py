"""Run the public, reproducible subset of Israel Fractures Conference."""
from pathlib import Path
from src.analysis import run

if __name__ == "__main__":
    run(Path(__file__).resolve().parent)
