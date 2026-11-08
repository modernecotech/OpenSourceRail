"""Exact load transfer, disjoint corridor quantity rounding and identity domains."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from engineering.railway_project import civil
from engineering.station_rail.common import identity
from engineering.pilot_civil.design import specification


def seal(value):
    value.pop('evaluation_id',None);value['evaluation_id']=identity(value)
    return value


def body():
    physical=dict(geometry='small-test-control-only')
    rows=[]
    for p,delta in (('tare',0.),('normal',20700.),('crowd-control',72000.)):
        for c,base in (('low',100000.),('base',120000.),('high',150000.)):
            m=base+delta
            rows.append(dict(name=p+'-'+c,train_mass_kg=m,CG_m=[11.5,0.,1.5],
                lateral_acceleration_m_s2=.5,
                axles=[dict(id='axle-'+str(i),x_m=float(i),vertical_force_N=m*civil.G/24) for i in range(24)]))
    return seal(dict(schema='osr-vehicle-installation/1',physical_definition=physical,candidate_id=identity(physical),
        mass_scenarios=rows,source_sha256={},installed_mass_complete=False,policy=dict(track_interface=specification()['track_interface']),
        compact_drive_contract=dict(mass_ownership=dict(all_new_drive_components_in_body_BOM=True,additional_external_drive_mass_kg=0.)),**civil.FLAGS))


def test_all_mass_and_crowd_cases_transfer_once_without_legacy_drive_append():
    b=body();q=civil.axle_packet(b,line_equipment=None)
    assert len(q['load_cases'])==9
    assert q['mass_evaluation_id']==b['evaluation_id']
    assert q['vehicle_candidate_id']==b['candidate_id']==q['candidate_id']
    assert q['external_drive_mass_added_kg']==0 and q['zero_is_exact_already_counted_drive']
    assert q['load_cases'][4]['train_mass_kg']==140700.
    assert q['installed_mass_complete'] is False


def test_missing_crowd_case_and_inconsistent_cg_are_not_repaired():
    b=body();b['mass_scenarios'].pop()
    with pytest.raises(ValueError,match='crowd'):
        civil.axle_packet(seal(b),line_equipment=None)
    b=body();b['mass_scenarios'][0]['CG_m'][0]+=1.
    with pytest.raises(ValueError,match='conserve'):
        civil.axle_packet(seal(b),line_equipment=None)


@pytest.fixture(scope='module')
def span():
    # Existing analytical record is a test control, never physical evidence for
    # this new corridor. Tests do not run or inherit any native FEM.
    return json.loads(Path('docs/design-engine/reconciled-pilot-no-store/civil.json').read_bytes())


def alignment():
    p=dict(geometry='test-route-1234.56m')
    return seal(dict(schema='osr-station-straight-alignment/1',candidate_id=identity(p),physical_definition=p,
        route_m=1234.56,source_sha256={},**civil.FLAGS))


def count(span,**changes):
    return civil.count_corridor(span,alignment(),**dict(dict(headway_s=200.,operation_hours_day=18.,
        operation_days_year=365.,design_life_years=30.),**changes))


def test_noninteger_span_quantities_are_counted_not_pilot_dollars_multiplied(span):
    q=count(span)
    assert q['quantities']['beams']==124 and q['quantities']['shared_bents']==63
    assert q['quantities']['nominal_span_track_m']==2480.
    assert q['quantities']['terminal_credit_track_m']==pytest.approx(10.88)
    assert q['cost']['beams']==124
    assert q['old_pilot_cost_and_fatigue_schedule_imported'] is False
    assert q['old_native_FEM_inherited'] is False
    assert q['physical_accepted'] is False


def test_schedule_price_and_proof_are_evaluations_not_new_span_geometry(span):
    a=count(span);b=count(span,headway_s=300.)
    assert a['candidate_id']==b['candidate_id'] and a['evaluation_id']!=b['evaluation_id']
    assert b['service_duty']['full_axle_cycles_per_track']==pytest.approx(a['service_duty']['full_axle_cycles_per_track']*2/3)
    changed=deepcopy(span);changed['policy']['cost']['concrete_usd_m3']=[2*x for x in changed['policy']['cost']['concrete_usd_m3']]
    changed['physical_definition']['complete_installed_geometry']=True
    changed['civil_candidate_id']=identity(changed['physical_definition']);seal(changed)
    c=count(changed)
    assert c['candidate_id']==a['candidate_id'] and c['evaluation_id']!=a['evaluation_id']
    assert c['cost']['direct_subtotal_usd']['base']>a['cost']['direct_subtotal_usd']['base']
    assert c['physical_accepted'] is False


def test_changed_actual_section_dimension_changes_project_geometry(span):
    changed=deepcopy(span);changed['physical_definition']['beam_stock']['cells'][0]['sections'][0]['polygon_yz_m'][0][0]-=.01
    changed['civil_candidate_id']=identity(changed['physical_definition']);seal(changed)
    assert identity(civil.physical_projection(changed))!=identity(civil.physical_projection(span))
    with pytest.raises(ValueError,match='section and physical'):
        count(changed)
