from pathlib import Path
import pytest
from engineering.reference_cell import vehicles
from engineering.component_registry import validate_registry
from engineering.sourced_case import equipment,power_revision as p
ROOT=Path(__file__).resolve().parents[3]
@pytest.fixture(scope='module')
def base():return equipment.substitute(vehicles.evaluate('V1',root=ROOT),root=ROOT)
@pytest.fixture(scope='module')
def eight(base):return p.revise(base,root=ROOT)


def test_real2s8p_same_candidate_registry_and_mass(base,eight):
    v=eight['vehicle'];validate_registry(v['registry'])
    assert v['candidate_id']==eight['candidate_id']!=base['candidate_id']
    assert v['registry']['parent_candidate_id']==base['candidate_id']
    assert eight['counts']['auxiliary-battery-with-BMS']==96
    assert eight['counts']['auxiliary-DC-converter']==54
    assert eight['architecture']['auxiliary_nominal_voltage_V']==51.2
    assert v['per_car_mass_properties']['mass_lower_bound_kg']>base['vehicle']['per_car_mass_properties']['mass_lower_bound_kg']
    assert equipment.constraints(eight)['electrical']['parallel_strings']==8
    assert equipment.constraints(eight)['electrical']['nominal_per_car_energy_Wh']==81920


def test_real_counts_and_no_old_BMS_or_pad_double_count(eight):
    r=eight['vehicle']['registry'];parts={x['physical_definition_id']:x for x in r['parts']}
    assert not any(x['part_id']=='OSR-SOURCED-BMS-ENCLOSURE-BUSBARS' for x in r['parts'])
    for token,expected in [('LYNX1000-NG',6),('CRADLE-RAIL',192),('CRADLE-STOP',192),('CRADLE-FASTENER',1152),('EPC5K5648I',18)]:
        assert sum(token in parts[o['part_definition_id']]['part_id'] for o in r['occurrences'])==expected
    assert not any('BRAKE-PAD-PAIR' in x['part_id'] for x in r['parts'])


def test_actual_module_locations_clear_original_bay_and_scoped_holds(eight):
    r=eight['vehicle']['registry'];parts={x['physical_definition_id']:x for x in r['parts']}
    rows=[o for o in r['occurrences'] if o['occurrence_id'].startswith('car-1/') and parts[o['part_definition_id']]['part_id']=='OSR-SOURCED-VICTRON-NG256-200']
    assert len(rows)==16
    assert min(o['transform'][0][3] for o in rows)==4.5
    assert max(o['transform'][0][3] for o in rows)==12.6
    assert set(o['transform'][1][3] for o in rows)=={-.8,.8}
    c=eight['complete_source_power_case']
    assert c['candidate_id']==eight['candidate_id']
    assert c['source_derivation_body_candidate_id']!=c['candidate_id']
    assert c['complete_installed_mass_kg'] is None
    assert not c['all_final_position_clearances_proved']


def test_source_limit_and_spacing_failure_preserved(base):
    with pytest.raises(ValueError):p.revise(base,parallel_strings=26,root=ROOT)
    with pytest.raises(ValueError):p.revise(base,parallel_strings=0,root=ROOT)
