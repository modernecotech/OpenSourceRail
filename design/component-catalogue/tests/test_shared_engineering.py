"""Independent mass/tensor, geometry, configuration and evidence regressions."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from osr_mech.common import ConsistFamily, consist_length_m
from osr_mech.family_definition import family_definition
from osr_mech.rolling_stock.trainset import family_dimensions, trainset_length_m
from osr_mech.freecad_trainset import _trainset_items
from osr_mech.engineering_definition import (validate, fingerprint, catalogue_template, model_mass_properties,
    verification_register, evaluate_inspection)
from osr_mech.vehicle_mass_properties import mass_properties, combined_inertia
from engineering.civil_exploration.shared_demo import demonstration, variants, transform


@pytest.mark.parametrize('family',list(ConsistFamily))
def test_cad_and_operational_family_dimensions_and_bogie_positions_reconcile(family):
    d=family_definition(family.value);items=_trainset_items(family.value)
    assert trainset_length_m(family)==consist_length_m(family)==d['length_m']
    assert family_dimensions(family).body_length_mm==pytest.approx(d['car_length_m']*1000)
    bodies=[i for i in items if i.group=='Car Bodies']
    assert len(bodies)==d['car_count']
    assert all(i.source.car_length_mm==pytest.approx(d['car_length_m']*1000) for i in bodies)
    pivots=sorted(i.x_mm/1000+d['length_m']/2 for i in items if i.group=='Bogies')
    assert pivots==pytest.approx(sorted(b['pivot_x_m'] for b in d['bogies']))
    assert len([x for b in d['bogies'] for x in b['axle_x_m']])==d['car_count']*4
    if family is ConsistFamily.METRO_6CAR:assert d['length_m']==111. and len(pivots)==12


def test_tensor_rotation_and_parallel_axis_have_independent_expected_result():
    # Two 2 kg bodies at ±1 m: point separation adds 4 kg m² to Iyy/Izz.
    r=[dict(id=str(sign),mass_kg=2.,x_m=float(sign),y_m=0.,z_m=0.,inertia_tensor_kg_m2=[[1.,0.,0.],[0.,2.,0.],[0.,0.,3.]]) for sign in [-1,1]]
    inertia=combined_inertia(r,dict(x=0.,y=0.,z=0.),None)
    assert np.allclose(inertia['inertia_tensor_kg_m2'],np.diag([2.,8.,10.]))
    r[0]['rotation_matrix']=[[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]]
    assert np.allclose(combined_inertia(r,dict(x=0.,y=0.,z=0.),None)['inertia_tensor_kg_m2'],np.diag([3.,7.,10.]))
    assert inertia['inertia_interval_kg_m2'] is None


def test_asymmetric_wheels_conserve_weight_and_both_static_moments_and_bound_uncertainty():
    bodies=[dict(id='body',supports=['a','b'])]
    bogies=[dict(id='a',pivot_x_m=2.,axle_x_m=[1.,3.]),dict(id='b',pivot_x_m=8.,axle_x_m=[7.,9.])]
    row=dict(id='mass',included_items=['mass'],mass_kg=1000.,uncertainty_kg=20.,x_m=3.,y_m=.2,z_m=1.,body='body',
             evidence_record='fixture',position_uncertainty_m=.01,inertia_tensor_kg_m2=np.diag([300.,400.,500.]).tolist(),inertia_uncertainty_kg_m2=5.)
    r=mass_properties([row],['mass'],bodies,bogies);w=r['wheel_pattern'];weight=9.81
    assert sum(a['static_load_kn'] for a in w)==pytest.approx(weight)
    assert sum(a['x_m']*a['static_load_kn'] for a in w)==pytest.approx(weight*3)
    assert sum(a['y_m']*a['static_load_kn'] for a in w)==pytest.approx(weight*.2)
    assert sum(a['static_load_kn'] for a in w if a['rail']==1)>sum(a['static_load_kn'] for a in w if a['rail']==0)
    assert r['inertia_interval_kg_m2'] is not None
    for mass in [980.,1000.,1020.]:
        for x in [2.99,3.,3.01]:
            sample=mass_properties([dict(row,mass_kg=mass,x_m=x,uncertainty_kg=0.,position_uncertainty_m=0.,inertia_uncertainty_kg_m2=0.)],['mass'],bodies,bogies)
            for nominal,actual in zip(w,sample['wheel_pattern']):
                assert nominal['static_load_interval_kn'][0]-1e-10<=actual['static_load_kn']<=nominal['static_load_interval_kn'][1]+1e-10
            interval=np.asarray(r['inertia_interval_kg_m2']);tensor=np.asarray(sample['inertia_tensor_kg_m2'])
            assert np.all(tensor>=interval[:,:,0]-1e-10) and np.all(tensor<=interval[:,:,1]+1e-10)
    assert r['accepted_mass_closure'] is False


def test_missing_or_nonphysical_inertia_is_never_closed():
    r=dict(id='r',mass_kg=1.,x_m=0.,y_m=0.,z_m=0.)
    assert combined_inertia([r],dict(x=0.,y=0.,z=0.),None)['inertia_tensor_kg_m2'] is None
    for tensor in [np.diag([-1.,1.,1.]),np.diag([1.,1.,5.]),np.ones((2,2)),[[1.,1.,0.],[0.,1.,0.],[0.,0.,1.]]]:
        with pytest.raises(ValueError):combined_inertia([dict(r,inertia_tensor_kg_m2=tensor)],dict(x=0.,y=0.,z=0.),None)


def test_template_extends_existing_product_ids_and_keeps_envelope_mass_open():
    from osr_mech.buildable_trainset import buildable_trainset_design
    design=buildable_trainset_design();model=catalogue_template(design);validate(model)
    assert {r['part_id'] for r in model['instances']}=={p.id for p in design.product_items if p.quantity_per_trainset>0}
    assert all(r['properties']=={'design':None,'supplier':None,'measured':None} for r in model['instances'])
    assert model_mass_properties(model)['total_mass_kg'] is None


def test_controlled_changes_invalidate_only_relevant_calculations_and_inspections():
    base=demonstration();receipt=verification_register(base,implementation_hashes={'solver':'first'})
    cases=variants(base)
    battery=verification_register(cases['battery-plus-10-percent'],receipt,implementation_hashes={'solver':'first'})
    assert {'mass-properties','vehicle-dynamics','bridge-demand','cost','inspection:battery-mass-car-1','inspection:car-1-running-correlation'}<=set(battery['invalidated'])
    assert 'drawing:car-2/battery' not in battery['invalidated']
    material=verification_register(cases['deck-modulus-minus-10-percent'],receipt,implementation_hashes={'solver':'first'})
    assert 'bridge-demand' in material['invalidated'] and 'cost' in material['invalidated']
    assert 'vehicle-dynamics' in material['invalidated']
    assert 'mass-properties' not in material['invalidated'] and 'vehicle-model' not in material['invalidated']
    implementation=verification_register(base,receipt,implementation_hashes={'solver':'changed'})
    assert 'bridge-demand' in implementation['invalidated']
    assert receipt['nodes']['mass-properties']==verification_register(base,implementation_hashes={'solver':'first'})['nodes']['mass-properties']
    # The previous receipt is immutable; it still names the previous configuration.
    assert receipt['configuration_sha256']==fingerprint(base)


def test_instance_and_joint_validation_rejects_unknown_ids_overlap_and_bad_frames():
    for change in ['product','scope','parent','rotation','joint','number','supplier']:
        m=demonstration()
        if change=='product':m['instances'][0]['part_id']='invented-catalogue'
        if change=='scope':m['instances'][1]['scope']=m['instances'][0]['scope']
        if change=='parent':m['instances'][0]['parent']=m['instances'][0]['id']
        if change=='rotation':m['instances'][0]['transform']['rotation'][0][0]=2.
        if change=='joint':m['joints'][0]['endpoints'][0]['datum']='absent'
        if change=='number':m['instances'][0]['properties']['design']['mass_kg']=True
        if change=='supplier':m['instances'][0]['properties']['supplier']=m['instances'][0]['properties']['design']
        with pytest.raises(ValueError):validate(m)


def test_measured_inspections_bind_asset_revision_serial_calibration_and_units(tmp_path):
    m=demonstration();m['state']='as-built';m['asset_id']='test-asset'
    for i,r in enumerate(m['instances']):r['serial']=f'test-{i}'
    def evidence(name,kind):
        p=tmp_path/name;p.write_text('test fixture evidence')
        return dict(path=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),kind=kind)
    row=next(r for r in m['instances'] if r['id']=='car-1/battery')
    record=dict(inspection_id='battery-mass-car-1',configuration_sha256=fingerprint(m),instance=row['id'],serial=row['serial'],batch=None,
        unit='kg',value=2550.,calibration=evidence('calibration.json','calibration'),evidence=evidence('weigh.json','measurement'))
    result=evaluate_inspection(m,record,root=tmp_path)
    assert result['within_defined_limits'] is True and result['accepted'] is False
    assert evaluate_inspection(m,dict(record,value=2700.),root=tmp_path)['within_defined_limits'] is False
    for changed in [dict(record,serial='other'),dict(record,unit='g'),dict(record,configuration_sha256='old')]:
        with pytest.raises(ValueError):evaluate_inspection(m,changed,root=tmp_path)
    (tmp_path/'calibration.json').write_text('changed')
    with pytest.raises(ValueError,match='stale'):evaluate_inspection(m,record,root=tmp_path)


def test_published_schema_accepts_template_and_demo_and_rejects_unknown_fields():
    jsonschema=pytest.importorskip('jsonschema')
    schema=json.loads((ROOT/'design/component-catalogue/schemas/shared-engineering-model.json').read_text())
    model=demonstration();jsonschema.Draft202012Validator(schema).validate(model)
    model['uncontrolled_field']=True
    with pytest.raises(jsonschema.ValidationError):jsonschema.Draft202012Validator(schema).validate(model)


def test_partial_property_record_remains_explicitly_open_and_json_cannot_hide_duplicates(tmp_path):
    from osr_mech.engineering_definition import load_definition
    model=demonstration();p=model['instances'][0]['properties']['design'];p['inertia_tensor_kg_m2']=None
    result=model_mass_properties(model)
    assert result['total_mass_kg'] is not None and result['inertia_tensor_kg_m2'] is None
    p['cg_m']=None
    assert model_mass_properties(model)['total_mass_kg'] is None
    path=tmp_path/'duplicate.json';path.write_text('{"revision":"one","revision":"two"}')
    with pytest.raises(ValueError,match='duplicate'):load_definition(path)
    path.write_text('{"mass":NaN}')
    with pytest.raises(ValueError,match='nonfinite'):load_definition(path)


def test_profile_edits_invalidate_new_designs_but_do_not_rewrite_frozen_builds(tmp_path,monkeypatch):
    import osr_mech.family_definition as fd
    model=demonstration();original=fd.PROFILE_PATH.read_text()
    path=tmp_path/'rolling-stock.toml';path.write_text(original.replace('length_m               = 111','length_m               = 112'))
    monkeypatch.setattr(fd,'PROFILE_PATH',path);monkeypatch.setattr(fd,'ROOT',tmp_path)
    with pytest.raises(ValueError,match='stale'):validate(model)
    assert fd.family_definition('metro-6car')['length_m']==112.
    model['state']='as-built';model['asset_id']='frozen-test-build'
    for i,r in enumerate(model['instances']):r['serial']=f'physical-{i}'
    assert validate(model)['length_m']==111.
    assert model['family_definition']['length_m']==111.
