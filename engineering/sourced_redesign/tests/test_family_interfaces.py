from pathlib import Path
import gzip,json
import numpy as np
import pytest
from engineering.sourced_redesign import family_interfaces as f
from engineering.sourced_case import layered_structure as layer
from engineering.sourced_case import whole_refinement as whole
ROOT=Path(__file__).resolve().parents[3]
from engineering.sourced_case.tests.portable_fixtures import baseline


def load(name):return baseline(name)


def test_actual_interference_and_low_cap_are_not_discarded():
    v2=f.diagnose(load('V2'));v5=f.diagnose(load('V5'))
    assert v2['roof_rib_lowering_m']==pytest.approx(.0073)
    assert max(r['actual_interference_m'] for r in v2['requests'])==pytest.approx(.0021)
    assert v5['roof_rib_lowering_m']==pytest.approx(.0018)
    assert v2['adaptation_needed'] and v5['adaptation_needed']


@pytest.mark.parametrize('name',['V1','V2','V3','V4','V5'])
def test_all_five_actual_family_definition_pipelines(name):
    original=load(name);adapted=f.revision(original,root=ROOT)
    if name in ('V1','V3','V4'):
        assert adapted is original
    else:
        assert adapted['candidate_id']!=original['candidate_id']
        assert adapted['registry']['parent_candidate_id']==original['candidate_id']
        assert adapted['registry']['parts']==original['registry']['parts']
        assert adapted['per_car_mass_properties']['mass_upper_bound_kg']==pytest.approx(original['per_car_mass_properties']['mass_upper_bound_kg'])
        assert adapted['per_car_mass_properties']['calculated_subset_CG_m'][2]<original['per_car_mass_properties']['calculated_subset_CG_m'][2]
        assert not f.diagnose(adapted)['adaptation_needed']
    bonded=layer.revision(adapted,root=ROOT)
    rows,panels=layer.inventory(bonded)
    assert all(patch['unfilled_gap_m']<1e-8 for p in panels for patch in p['bearing_patches'])
    caprows=[r for r in rows if 'rib-cap-' in r['occurrence']['occurrence_id'] and r['grade'] and r['grade'].startswith('AL-')]
    assert caprows and min(float(r['dimensions'][2]) for r in caprows)>=.004-1e-10
    full=whole.revision(bonded,root=ROOT)
    assert full['requirements']==original['requirements']
    assert full['candidate_id']!=original['candidate_id']
    assert all(full[k] is False for k in f.FLAGS)
    layer._vehicle(full)
