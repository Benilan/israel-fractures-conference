from pathlib import Path
import run_analysis

ROOT = Path(__file__).resolve().parents[1]

def test_expected_source_file_list():
    assert len(run_analysis.INPUTS) == 9
    assert len(set(run_analysis.INPUTS)) == 9

def test_entrypoint_exists():
    assert (ROOT / "run_analysis.py").is_file()

def test_no_raw_source_files_committed():
    assert not list((ROOT / "data/raw").glob("*.xlsx"))
    assert not list((ROOT / "data/raw").glob("*.csv"))
