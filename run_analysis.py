"""Public verification entry point for Israel Fractures Conference.

The full analytical source and authorized raw inputs are prerequisites. This
script fails explicitly when they are absent; it never substitutes hardcoded
slide values for recalculations.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUTS = [
    "Knesset 21 - 2019 - 1.csv",
    "Knesset 22 - 2019 - 2.csv",
    "Knesset 23 - 2020.csv",
    "Knesset 24 - 2021.csv",
    "Knesset 25 - 2022.csv",
    "selected-data-by-localities-and-statistical-areas-2022-census.xlsx",
    "24_24_230t1.xlsx",
    "Copie de 24_24_230t3.xlsx",
    "bycode2023.xlsx",
]


def check_inputs():
    missing = [name for name in INPUTS if not (ROOT / "data/raw" / name).exists()]
    if missing:
        raise SystemExit(
            "Missing source data in data/raw/:\n  - " + "\n  - ".join(missing)
            + "\nThe source files must be obtained from the original CBS / "
            "election datasets before the complete run."
        )
    if not (ROOT / "src/pipeline_v16.py").exists():
        raise SystemExit(
            "Full research pipeline is not yet installed in this repository. "
            "Do not treat GitHub Actions smoke tests as slide validation."
        )


if __name__ == "__main__":
    check_inputs()
    from src.pipeline_v16 import run
    run(ROOT)
