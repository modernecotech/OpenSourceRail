from copy import deepcopy
import pytest
from engineering.station_rail.common import identity
from engineering.design_search.craft_backends import backend_api as api,viaduct_cases,viaduct_delivery


def test_registered_preferences_preserve_existing_specialist_methods():
    value=api.registry()
    assert value['default_cad']=='freecad' and value['default_structural']=='calculix'
    assert {'solidcraft','fieldcraft','freecad','calculix','gmsh_getdp','ifcopenshell','chrono','sumo'}<=value['providers'].keys()
    assert value['interfaces_are_not_generic_admission']
    assert all(value[k] is False for k in api.FLAGS)


def test_physical_revision_preserves_parent_and_does_not_select_reference():
    parent=viaduct_cases.build('reference_box');original=deepcopy(parent)
    revised=api.CivilCAD().revise(parent,dict(family='folded_plate'),reason='Compare a different load path')
    assert parent==original
    assert revised['candidate']['candidate_id']!=parent['candidate_id']
    assert revised['ancestry']['parent_candidate_id']==parent['candidate_id']
    assert revised['ancestry']['physical_selection_changed'] is False
    with pytest.raises(api.CapabilityHold):api.CivilCAD().revise(parent,dict(unknown_topology=.4),reason='Unsupported compiler')
    with pytest.raises(ValueError,match='must change'):api.CivilCAD().revise(parent,dict(profile='reference'),reason='No change')


def test_definition_check_is_not_a_native_geometry_or_analysis_pass():
    value=api.CivilCAD().validate_geometry(viaduct_cases.build('reference_box'))
    assert value['definition_valid'] is True
    assert value['native_geometry_checked'] is False
    assert value['native_evaluation_admitted'] is False


def test_delivery_is_same_candidate_and_disabled_not_executable_ERP():
    context=viaduct_delivery.prepare();candidate=viaduct_cases.build('ribbed_u')
    interface=api.CivilDelivery()
    material=interface.calculate_materials(candidate,context)
    assert material['candidate_id']==candidate['candidate_id']
    assert len(interface.generate_processes(candidate,context))>0
    assert interface.estimate_costs(candidate,context)['quotes_verified'] is False
    draft=interface.export_business_records(candidate,context)
    assert draft['candidate_id']==candidate['candidate_id']
    assert draft['disabled']==1 and draft['transactions_performed'] is False
    bad=deepcopy(candidate);bad['candidate_id']='other';bad['case_definition_id']=identity({k:v for k,v in bad.items() if k!='case_definition_id'})
    with pytest.raises(ValueError,match='Canonical candidate'):interface.calculate_materials(bad,context)


def test_failed_requested_geometry_is_not_admitted_to_analysis(tmp_path,monkeypatch):
    import json
    from engineering.design_search.craft_backends import viaduct_admission
    case=viaduct_cases.build('reference_box')
    (tmp_path/'manifest.json').write_text(json.dumps(dict(cases={case['case_id']:dict(execution='completed',
        diagnostic=dict(comparison_passed=True),exact_step=dict(comparison_passed=False))})))
    monkeypatch.setattr(viaduct_admission,'verify',lambda *a,**kw:dict(source_result_id='source',verification_id='checked',nominal_geometry_comparison_passed=False))
    with pytest.raises(api.CapabilityHold,match='Requested case'):api.CivilCAD().export(case,tmp_path)


def test_mixed_mesh_and_unsealed_input_cannot_start_native_workers(tmp_path,monkeypatch):
    from engineering.design_search.craft_backends import viaduct_fem
    called=[]
    monkeypatch.setattr(viaduct_fem,'solve',lambda *a,**kw:called.append('solve'))
    monkeypatch.setattr(viaduct_fem,'mesh',lambda *a,**kw:called.append('mesh'))
    request=dict(candidate_id='one',component_geometry_id='component',input_id='input')
    mesh=dict(candidate_id='two',component_geometry_id='component',input_id='input')
    mesh['mesh_id']=identity(mesh)
    with pytest.raises(ValueError,match='Mixed numerical mesh'):api.CivilAnalysis().solve(request,mesh,tmp_path)
    mesh['candidate_id']='one'
    with pytest.raises(ValueError,match='mesh seal'):api.CivilAnalysis().solve(request,mesh,tmp_path)
    with pytest.raises(ValueError,match='input seal'):api.CivilAnalysis().mesh(request,'coarse',tmp_path)
    assert called==[]
