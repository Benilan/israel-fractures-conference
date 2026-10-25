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

def test_current_presentation_plot_functions_available():
    from src.deck_visuals import (
        plot_2022_parties, plot_turnout, plot_seven_families_reference,
        plot_coalition_reference, plot_anova_reference, plot_cbs_reference,
    )
    assert all(callable(f) for f in (
        plot_2022_parties, plot_turnout, plot_seven_families_reference,
        plot_coalition_reference, plot_anova_reference, plot_cbs_reference,
    ))

def test_reference_deck_series_are_complete_and_sum_to_100():
    import numpy as np
    from src.deck_visuals import REFERENCE_SHARE, FAMILIES, ELECTIONS
    assert REFERENCE_SHARE.shape == (5, 7)
    assert len(FAMILIES) == 7 and len(ELECTIONS) == 5
    assert np.allclose(REFERENCE_SHARE.sum(axis=1), 100, atol=.11)

def test_2022_main_party_mapping_matches_reference():
    from src.deck_visuals import PARTY_NAMES, MAIN_2022, K25_PPT_VALUES
    assert len(MAIN_2022) == len(K25_PPT_VALUES) == 13
    assert set(MAIN_2022).issubset(set(PARTY_NAMES.values()))

def test_coalition_reference_netanyahu_totals():
    from src.deck_visuals import COALITIONS
    expected=[60,55,58,52,64]
    actual=[sum(seats for _,seats in COALITIONS[k]['Netanyahu']) for k in ('K21','K22','K23','K24','K25')]
    assert actual == expected

def test_independent_historical_analysis_is_available():
    from src.historical_reproduction import calculate, export, EXPECTED_ETA
    assert callable(calculate) and callable(export)
    assert len(EXPECTED_ETA) == 6
    assert EXPECTED_ETA["AcadmCert_pcnt"] == 714

def test_historical_annotations_do_not_claim_full_coalition_coverage():
    from src.pipeline_v16 import PENDING
    assert "slide_13_coalition_scenarios" in PENDING

def test_bloc_chart_does_not_claim_to_allocate_all_seats():
    from src.deck_visuals import coalition_coverage
    frame=coalition_coverage().set_index('Election')
    assert list(frame.index)==['K21','K22','K23','K24','K25']
    assert frame.NetanyahuBlocSeats.to_dict()=={'K21':60,'K22':55,'K23':58,'K24':52,'K25':64}
    assert (frame.UnallocatedSeats>=0).all()
    assert not frame.Complete120SeatPartition.all()

def test_historical_chart_functions_consume_recomputed_data():
    import inspect
    from src.deck_visuals import plot_seven_families_reference, plot_anova_reference
    assert 'computed_share' in inspect.signature(plot_seven_families_reference).parameters
    assert 'computed_eta' in inspect.signature(plot_anova_reference).parameters
