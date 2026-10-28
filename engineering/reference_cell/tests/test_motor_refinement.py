"""Numerical resource revisions never change a physical or evidence obligation."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from engineering.station_rail.common import identity,encoded
from engineering.railway_completion import motor as old
from engineering.railway_twin import model
from engineering.reference_cell import motor_refinement as m

@pytest.fixture(scope='module')
def bundle():return old.rewound_variant(model.materialize()['bundle'])

def test_resource_revision_retains_physics_and_frozen_input_identity(bundle):
    variables=dict(voltage_peak_V=375.,frequency_Hz=50.,steps=64,speed_m_s=20.,transport_method='supg-coth')
    prior=old.request(bundle,**variables)
    current=m.request(bundle,maximum_seconds=600.,**variables)
    assert current['bundle_id']==prior['bundle_id']
    assert current['motor_component_id']==prior['motor_component_id']
    assert current['physical_geometry']==prior['physical_geometry']
    assert current['evaluated_component_definition_id']==prior['evaluated_component_definition_id']
    assert current['wiring']==prior['wiring']
    assert current['current_limit_A']==prior['current_limit_A']==230.
    assert current['request_id']!=prior['request_id']
    assert m.path_resistance(current).tolist()==old.path_resistance(prior).tolist()
    assert m.estimate(current)==old.estimate(prior)
    assert m.sources()[m.UPSTREAM]==m.UPSTREAM_SHA256

@pytest.mark.parametrize('seconds',[175.,600.,900.])
def test_explicit_bounded_numerical_seconds(bundle,seconds):
    assert m.validate(m.request(bundle,maximum_seconds=seconds))['maximum_seconds']==seconds

@pytest.mark.parametrize('variables',[
    dict(maximum_seconds=901.),dict(memory_bytes=4*1024**3),dict(maximum_nodes=180001),
    dict(steps=513),dict(current_limit_A=255.),dict(voltage_peak_V=376.),dict(temperature_C=100.)])
def test_resource_extension_cannot_relax_physical_or_absolute_budget(bundle,variables):
    with pytest.raises(ValueError):m.request(bundle,**variables)


def fixture(folder,bundle,dt,steps,scale=1.,execution='completed'):
    folder.mkdir();r=m.request(bundle,dt_s=dt,steps=steps,maximum_seconds=600.)
    result=dict(execution=execution,state='completed',trace=[dict(time_s=(i+1)*dt,
        thrust_N=scale*(i+1)*dt,path_currents_A=[scale*(i+1)*dt]*30) for i in range(steps)],
        actual_mesh={'fixture_only':'no native execution'},evaluation_id=identity([dt,steps,scale,execution]))
    (folder/'input.json').write_bytes(encoded({'request':r}))
    (folder/'result.json').write_bytes(encoded(result))
    return folder


def test_matched_horizon_diagnostics_do_not_claim_convergence(bundle,tmp_path,monkeypatch):
    monkeypatch.setattr(m,'verify',lambda *a,**k:dict(verified=True))
    coarse=fixture(tmp_path/'coarse',bundle,.002,4)
    fine=fixture(tmp_path/'fine',bundle,.001,8)
    value=m.compare([fine,coarse])
    assert value['completed_same_horizon'] and value['matched_points']==4
    assert value['relative_thrust_RMS_change']==0
    assert value['approved_convergence_limit'] is None
    assert value['numerical_time_convergence']=='unconfirmed'
    assert value['available_operating_map'] is None
    assert all(value[k] is False for k in m.FLAGS)


def test_interrupted_trace_never_counts_as_matched_horizon(bundle,tmp_path,monkeypatch):
    monkeypatch.setattr(m,'verify',lambda *a,**k:dict(verified=True))
    coarse=fixture(tmp_path/'coarse',bundle,.002,4)
    fine=fixture(tmp_path/'fine',bundle,.001,8,execution='interrupted')
    value=m.compare([coarse,fine])
    assert value['completed_same_horizon'] is False
    assert value['relative_thrust_RMS_change'] is None


def test_different_requested_horizon_rejected(bundle,tmp_path,monkeypatch):
    monkeypatch.setattr(m,'verify',lambda *a,**k:dict(verified=True))
    coarse=fixture(tmp_path/'coarse',bundle,.002,4)
    fine=fixture(tmp_path/'fine',bundle,.001,7)
    with pytest.raises(ValueError,match='horizons'):m.compare([coarse,fine])
