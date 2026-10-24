"""Execute the original V18 conference analysis pipeline."""
from pathlib import Path
from src.pipeline_v16 import run

if __name__ == "__main__":
    run(Path(__file__).resolve().parent)
