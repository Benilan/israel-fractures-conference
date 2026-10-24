"""Tests of stable scientific invariants; independent of raw external files."""
from pathlib import Path
import numpy as np
import pandas as pd
from src.heatmap_v15 import FAMILIES, round_rows_to_100, PROFILE_ORDER
from src.pipeline_v16 import ELECTIONS, PENDING
from src.historical_audit import EXPECTED

def test_five_knesset_elections():
    assert list(ELECTIONS) == ['K21','K22','K23','K24','K25']

def test_party_lists_not_double_counted_in_2022_mapping():
    codes = [code for family in FAMILIES.values() for code in family]
    assert len(codes) == len(set(codes))
    assert 'שס' in FAMILIES['Haredi']

def test_social_profiles_count():
    assert len(PROFILE_ORDER) == 5

def test_rounding_all_rows_sum_to_100():
    p = pd.DataFrame([[20.2,30.3,49.5],[33.34,33.33,33.33]],columns=['A','B','C'])
    r = round_rows_to_100(p)
    assert np.array_equal(r.sum(axis=1).to_numpy(),[100,100])

def test_official_netanyahu_bloc_reference():
    assert EXPECTED == {'K21':60,'K22':55,'K23':58,'K24':52,'K25':64}

def test_pending_claims_not_misrepresented():
    assert 'slide_11_evolution_families' in PENDING
    assert 'slide_19_published_eta' in PENDING
