from pathlib import Path
import numpy as np
import pandas as pd
from src.analysis import ELECTIONS, FAMILIES_2022, round_rows_to_100, label_profiles

def test_five_elections_and_shas_in_haredi():
    assert len(ELECTIONS) == 5
    assert "שס" in FAMILIES_2022["Haredi"]

def test_2022_vote_families_are_disjoint():
    flat = [code for codes in FAMILIES_2022.values() for code in codes]
    assert len(flat) == len(set(flat))

def test_largest_remainder_rows_total_100():
    pct = pd.DataFrame([[10.4, 20.4, 69.2], [33.34, 33.33, 33.33]])
    rounded = round_rows_to_100(pct)
    assert (rounded.sum(axis=1) == 100).all()
    assert np.issubdtype(rounded.to_numpy().dtype, np.integer)

def test_expected_source_paths_are_data_free():
    assert not list(Path("data/raw").glob("*.xlsx"))
    assert not list(Path("data/raw").glob("*.csv"))
