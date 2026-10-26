from copy import deepcopy
from pathlib import Path
import os
import pytest
from engineering.design_search import wheel_motor as m


def test_physical_stock_is_separate_from_operating_hypotheses():
    p=m.default_parameters();changed=deepcopy(p);changed['evaluation']['current_peak_A']=70.
    assert m.definition(p)['motor_component_id']==m.definition(changed)['motor_component_id']
    rows=m.stock(p);on=[r for r in rows if r['installation']=='onboard'];way=[r for r in rows if r['installation']=='wayside']
    assert len(on)==1
    assert on[0]['mass_kg']==pytest.approx(9*.015*.16*2710)
    assert sum(r['mass_kg'] for r in way)==pytest.approx(m.definition(p)['bare_primary_stock_kg_per_m']*12.5)


def test_failure_revision_changes_material_geometry_and_preserves_gap():
    ref,wide=m.initial_parameters();new=m.revise(wide,{'failure_reasons':['linear_steel_field_limit']},2)
    assert new['physical']['backiron_m']>wide['physical']['backiron_m']
    assert new['physical']['slot_width_m']<wide['physical']['slot_width_m']
    assert new['physical']['gap_each_side_m']==.015
    assert m.definition(new)['slot_fill_fraction']<=.6


def test_zero_current_and_quadratic_source_are_explicit_in_native_equations():
    p=m.default_parameters();d=m.definition(p);s=p['evaluation']['scenarios'][0]
    c=m._case(p,s,False);text=m.native.formulation(c,d)
    assert 'DtDof [sigma*Dof{a}' in text and '-sigma*(v[] /\\ Dof{d a})' in text
    assert 'PhaseAPower' in text and 'js[Region[100]]' in text
    z=deepcopy(p);z['evaluation']['current_peak_A']=0.;zt=m.native.formulation(m._case(z,s,False),m.definition(z))
    assert 'Complex[0,-0]' in zt or 'Complex[0,0]' in zt


def test_limits_cannot_be_relaxed_and_mesh_confirmation_is_distinct():
    p=m.default_parameters();p['evaluation']['linear_peak_field_limit_T']=2.3
    with pytest.raises(ValueError):m.definition(p)
    p=m.default_parameters();s=p['evaluation']['scenarios'][1]
    assert m._case(p,s,True)['plate_gap_mesh_m']<m._case(p,s,False)['plate_gap_mesh_m']
    bad=deepcopy(p);bad['physical']['gap_each_side_m']=.010
    with pytest.raises(ValueError):m.definition(bad)


def test_display_label_does_not_change_physical_motor():
    p=m.default_parameters();renamed=deepcopy(p);renamed['physical']['name']='display rename'
    assert m.definition(p)['motor_component_id']==m.definition(renamed)['motor_component_id']


@pytest.mark.skipif(os.environ.get('OSR_NATIVE_MOTOR_FIXTURE')!='1',reason='Explicit bounded native fixture opt-in')
def test_native_zero_current_and_quadratic_force_with_retained_raw(tmp_path):
    p=m.default_parameters();p['physical'].update(name='bounded-native-fixture',primary_length_m=1.5,periods=3,secondary_length_m=1.25,parallel_paths_per_phase=2)
    p['evaluation'].update(mesh_m=.0125,gap_mesh_m=.005,scenarios=[dict(speed_m_s=0.,temperature_C=80.,gap_m=.015)])
    root=Path(__file__).resolve().parents[3];rows=[]
    for current in (0.,50.,100.):
        case=deepcopy(p);case['evaluation']['current_peak_A']=current
        result=m.evaluate(case,1000.,tmp_path/str(int(current)),root=root)
        assert result['execution']=='completed';m.verify(tmp_path/str(int(current)),root)
        rows.append(result['cases'][0]['metrics'])
    assert rows[0]['force_N']==rows[0]['secondary_Joule_W']==0.
    assert rows[2]['force_N']/rows[1]['force_N']==pytest.approx(4.,rel=1e-6)
    assert rows[2]['maximum_steel_phasor_B_bound_T']/rows[1]['maximum_steel_phasor_B_bound_T']==pytest.approx(2.,rel=1e-6)
    assert all(r['relative_energy_residual']<1e-8 for r in rows)
    assert all(r['available_installed_force_N'] is None for r in rows)
