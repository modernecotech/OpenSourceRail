from math import sqrt
import pytest
from engineering.station_rail import station_motor as m

def test_actual_windings_fit_and_account_end_turns():
    d=m.definition()
    assert d['slot_fill_fraction']==pytest.approx(40*25/(40*55))
    assert d['wire_length_m_per_coil']>40*.16*2
    assert d['bare_primary_stock_kg_per_m']>200
    assert d['bare_900m_stock_kg_per_direction']==900*d['bare_primary_stock_kg_per_m']

def test_peak_rms_and_three_phase_reversal_are_explicit():
    c=m.case(current_peak_A=100.)
    assert c['current_RMS_A']==pytest.approx(100/sqrt(2))
    text=m.formulation(c,m.definition())
    assert 'js[Region[100]]' in text
    assert 'Dof{u}' in text and 'v[] /\\ Dof{d a}' in text
    assert 'Value 0.' in text
    assert 'exact[]' not in text
    assert text!=m.formulation(m.case(phase_direction=-1),m.definition())

def test_out_of_domain_values_fail_closed():
    with pytest.raises(ValueError):m.case(current_peak_A=-1)
    with pytest.raises(ValueError):m.case(temperature_C=50)
    assert len(m.campaign_cases())<=18


def test_zero_source_is_valid_and_candidate_current_fits_copper_bound():
    assert m.case(current_peak_A=0)['current_RMS_A']==0
    assert m.case(current_peak_A=140)['wire_current_density_RMS_A_mm2']<4
