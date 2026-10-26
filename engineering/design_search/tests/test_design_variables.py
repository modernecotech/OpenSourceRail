from copy import deepcopy
import pytest
from engineering.design_search import design_variables as v


def test_registry_covers_coupled_material_structure_fitout_and_system_changes():
    r=v.catalogue();assert r['extensible'] and not r['complete_universal_design_space_claimed']
    assert set(x['domain'] for x in r['variables'].values())==set(v.DOMAINS)
    required={'material.primary_grade','material.core_family','body.core_cell_direction','body.ply_angles_deg',
        'body.roof_floor_loadpath','joint.compliance_law','runninggear.bogie_spacing_m','motor.topology',
        'motor.current_A','brake.independent_channels','fitout.seat_bench_geometry','fitout.door_leaf_and_drive',
        'fitout.floor_panel','fitout.roof_panel','services.HVAC_routes','service.headway_s',
        'civil.pier_foundation','manufacturing.transport_erection','maintenance.recovery_resources'}
    assert required<=set(r['variables'])
    for d in r['variables'].values():
        assert d['unit'] and d['invalidates'] and d['requires_compatibility']
        assert not d['model_support']['independently_validated'] and not d['model_support']['native_dispatch_allowed']
        assert not d['numerical_properties_supplied'] and not d['example_values_are_exhaustive']
    assert v._checked_registry(r)==r


def test_registered_extension_preserves_default_and_requires_real_contract_metadata():
    before=v.catalogue()
    d=v.descriptor('body.rib_local_taper','body','record','mixed-record',effects=['geometry','stress','manufacturing'],
        compatibility=['buckling and actual joining'],note='New tapered rib requires geometry and validated native adapter')
    after=v.register(d,before)
    assert d['id'] not in before['variables'] and d['id'] not in v.catalogue()['variables']
    assert d['id'] in after['variables'] and before['registry_id']!=after['registry_id']
    contract=v.validate_changes({d['id']:{'root_depth_m':.2,'tip_depth_m':.08}},after)
    assert contract['physical_identity_must_change'] and not contract['automatic_native_dispatch']
    with pytest.raises(ValueError,match='silent replacement'):v.register(d,after)
    bad=deepcopy(d);bad.pop('descriptor_id');bad['model_support']['independently_validated']=True
    with pytest.raises(ValueError,match='validated native'):v.register(bad)
    bad=deepcopy(d);bad['invalidates']=[];bad.pop('descriptor_id')
    with pytest.raises(ValueError,match='Consequences'):v.register(bad)


def test_physical_operation_and_model_changes_keep_separate_identities():
    p=v.validate_changes({'body.sill.depth_m':.6})
    o=v.validate_changes({'motor.current_A':100.})
    m=v.validate_changes({'model.provisional_stiffness_target_m':.03})
    assert p['physical_identity_must_change'] and not o['physical_identity_must_change'] and not m['physical_identity_must_change']
    assert o['requirement_or_operation_revision_required']
    assert all(r['evaluation_identity_must_change'] and not r['physical_accepted'] for r in (p,o,m))
    assert 'civil' in p['affected_outputs'] and 'motor-thrust-and-braking' in p['affected_outputs']
    assert m['physical_performance_estimate'] is None


def test_unknown_material_and_topology_values_do_not_inherit_native_support():
    result=v.validate_changes({'material.core_family':'new locally available cellular core','body.topology':'new structural family'})
    assert result['automatic_native_dispatch'] is False and result['physical_performance_estimate'] is None
    assert all(not r['independently_validated'] for r in result['adapter_requirements'])
    note=v.catalogue()['variables']['body.sill.depth_m']['model_support']['domain_note']
    assert 'coupled' in note and 'extension' in note


def test_change_values_and_registry_tampering_fail_closed():
    for changes in ({'unknown.variable':1.},{'body.sill.depth_m':float('nan')},
                    {'runninggear.driven_axles':True},{'body.ply_angles_deg':[]},{'fitout.floor_panel':{}}):
        with pytest.raises(ValueError):v.validate_changes(changes)
    bad=v.catalogue();bad['variables']['motor.current_A']['unit']='invented'
    with pytest.raises(ValueError):v.validate_changes({'motor.current_A':10.},bad)
    bad=v.catalogue();bad['physical_accepted']=True;bad['registry_id']=v.identity({n:x for n,x in bad.items() if n!='registry_id'})
    with pytest.raises(ValueError,match='unaccepted'):v.register(v.descriptor('body.new','body','number','m',effects=['geometry'],compatibility=['actual fit'],note='Unimplemented'),bad)


def test_descriptor_does_not_accept_evaluator_identity_or_fake_source_data():
    d=deepcopy(v.catalogue()['variables']['body.sill.depth_m']);d.pop('descriptor_id');d['evaluation_id']='a'*64
    with pytest.raises(ValueError,match='fields belong elsewhere'):v.validate_descriptor(d)
    d=deepcopy(v.catalogue()['variables']['body.sill.depth_m']);d.pop('descriptor_id');d['numerical_properties_supplied']=True
    with pytest.raises(ValueError,match='material properties'):v.validate_descriptor(d)
