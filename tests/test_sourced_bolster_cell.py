from pathlib import Path
from copy import deepcopy
import importlib.util
import pytest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('bolster_cell_helper',ROOT/'tools/automation/sourced-bolster-cell.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
h.modules(ROOT)
from engineering.component_registry import make_part,make_occurrence,make_registry,summary


def seal(v):
    v.pop('evaluation_id',None);v['evaluation_id']=h.identity(v);return v


def fixture(change=None):
    def part(name,fn,m=1):
        return make_part(name,'A',[fn],dict(kind='box',dimensions_m=[1.,.1,.1],net_volume_m3=.01),None,
            dict(calculated_kg=m,lower_bound_kg=m,upper_bound_kg=m,evidence_state='calculated'),dict(method='test-only'))
    body=part('body','primary-body');newbody=part('bolster','bogie-interfaces',2);battery=part('battery','auxiliary-power');brake=part('brake','running-gear')
    def registry(new):
        occ=[]
        for car in range(1,7):
            for label,p in [('bolster-test' if new else 'old-support',newbody if new else body),('battery',battery),('brake',brake)]:
                T=[[1.,0.,0.,float(car)*17.5],[0.,1.,0.,0.],[0.,0.,1.,1.],[0.,0.,0.,1.]]
                if change=='pose' and new and label=='battery':T[2][3]+=.001
                if change=='brake' and new and label=='brake':p=part('changedbrake','running-gear',1.1)
                occ.append(make_occurrence(f'car-{car}/'+label,p,'car-'+str(car),T,'vehicle/test'))
        parts={x['physical_definition_id']:x for x in (newbody if new else body,battery,brake)}
        if change=='brake' and new:
            p=part('changedbrake','running-gear',1.1);parts.pop(brake['physical_definition_id']);parts[p['physical_definition_id']]=p
        return make_registry('body-new' if new else 'body-old',list(parts.values()),occ,['primary-body','auxiliary-power','running-gear'],parent_candidate_id=old['candidate_id'] if new else None,assemblies=[dict(id='car-'+str(i),parent_id=None) for i in range(1,7)])
    reg=registry(False)
    old=seal(dict(candidate_id=reg['candidate_id'],registry=reg,vehicle_id='V4',requirements=dict(cars=6),functional_requirements=['primary-body','auxiliary-power','running-gear'],interfaces=dict(bogie=[2.,15.]),architecture=dict(passive=True),summary=summary(reg),**h.FLAGS))
    reg2=registry(True)
    new=deepcopy(old);new.update(candidate_id=reg2['candidate_id'],registry=reg2,summary=summary(reg2),bolster_revision=dict(parent_candidate_id=old['candidate_id'],parent_vehicle_evaluation_id=old['evaluation_id'],removed_local_names=['old-support']))
    seal(new)
    source=seal(dict(candidate_id='historical-intermediate',source='unchanged-source-receipt',**h.FLAGS))
    power=seal(dict(candidate_id=old['candidate_id'],body_candidate_id=old['candidate_id'],actual_registry_id=reg['registry_id'],source_derivation=source,source_derivation_evaluation_id=source['evaluation_id'],source_derivation_body_candidate_id=source['candidate_id'],hardware_counts_per_car=dict(battery_modules=16,brakes=8),**h.FLAGS))
    e=seal(dict(candidate_id=old['candidate_id'],vehicle=old,summary=old['summary'],counts=dict(battery=96),architecture=dict(battery_parallel_strings=8),catalogue=dict(historical_product_id='product-bound-to-'+old['candidate_id']),replacements=[dict(candidate_id=old['candidate_id'],product_id='real-product')],complete_source_power_case=power,fitment_screens=dict(status='previous'),known_installation_scope=dict(status='unqualified'),**h.FLAGS))
    return e,old,new


def test_derived_wrapper_binds_current_hardware_retains_historical_receipts():
    e,old,new=fixture();saved=h.encoded(e)
    r,d=h.derive(e,old,new,helper_sha256='a'*64)
    assert h.encoded(e)==saved
    assert r['candidate_id']==new['candidate_id']!=e['candidate_id']
    assert h.encoded(r['vehicle'])==h.encoded(new)
    assert r['replacements']==e['replacements']
    assert r['catalogue']==e['catalogue']
    p=r['complete_source_power_case'];original=e['complete_source_power_case']
    assert p['candidate_id']==new['candidate_id']
    assert p['actual_registry_id']==new['registry']['registry_id']
    assert p['source_derivation']==original['source_derivation']
    assert p['source_derivation_evaluation_id']==original['source_derivation_evaluation_id']
    assert p['hardware_counts_per_car']==original['hardware_counts_per_car']
    assert d['boundary']['protected_nonbody_occurrences']==12
    assert d['boundary']['all_retained_physical_occurrences_and_poses_byte_identical']
    assert r['fitment_screens']['status']=='invalidated-by-primary-body-revision'
    assert r['dependency_invalidation']['inherited_assembly_access_and_body_joint_outcomes_current'] is False
    h.sealed(r);h.sealed(p);h.sealed(d,'derivation_id')


@pytest.mark.parametrize('change',['pose','brake'])
def test_rejects_any_service_hardware_or_pose_change(change):
    e,old,new=fixture(change)
    with pytest.raises(ValueError,match='Retained occurrence/part/pose'):h.derive(e,old,new,helper_sha256='a'*64)


def test_requires_exact_canonical_ancestor_not_candidate_id_only():
    e,old,new=fixture();e['vehicle']=deepcopy(old);e['vehicle']['unrecorded']='edited';seal(e['vehicle']);seal(e)
    with pytest.raises(ValueError,match='exact native ancestor'):h.derive(e,old,new,helper_sha256='a'*64)


def test_inherited_release_flag_is_rejected_recursively():
    e,old,new=fixture();e['replacements'][0]['manufacturing_release']=True;seal(e)
    with pytest.raises(ValueError,match='cannot grant release'):h.derive(e,old,new,helper_sha256='a'*64)


def test_wrong_power_registry_rejected_even_when_resealed():
    e,old,new=fixture();e['complete_source_power_case']['actual_registry_id']='another-registry';seal(e['complete_source_power_case']);seal(e)
    with pytest.raises(ValueError,match='Power hardware binding'):h.derive(e,old,new,helper_sha256='a'*64)


def test_fixed_bogie_interface_change_rejected():
    e,old,new=fixture();new['interfaces']['bogie']=[1.,16.];seal(new)
    with pytest.raises(ValueError,match='fixed vehicle interface'):h.derive(e,old,new,helper_sha256='a'*64)


def test_wrong_removed_stock_declaration_rejected():
    e,old,new=fixture();new['bolster_revision']['removed_local_names']=[];seal(new)
    with pytest.raises(ValueError,match='Removed structural stock'):h.derive(e,old,new,helper_sha256='a'*64)


def test_nested_native_manifests_are_part_of_closed_inventory(tmp_path):
    (tmp_path/'manifest.json').write_text('root');(tmp_path/'native').mkdir();(tmp_path/'native/manifest.json').write_text('native')
    files=h.inventory(tmp_path)
    assert set(files)=={'native/manifest.json'}
    assert files['native/manifest.json']['sha256']==h.sha(tmp_path/'native/manifest.json')


def test_no_overwrite_of_existing_immutable_output(tmp_path,monkeypatch):
    monkeypatch.setattr(h,'modules',lambda root:object())
    with pytest.raises(ValueError,match='Fresh immutable'):h.run('unused','unused','unused',tmp_path,root=ROOT)


def test_closed_payload_whitelist_names_native_and_ifc_explicitly():
    assert 'ancestor-native/manifest.json' in h.expected_payload(False)
    assert 'bolster-native/input.json' in h.expected_payload(False)
    assert not any(x.startswith('ifc/') for x in h.expected_payload(False))
    assert h.expected_payload(True)-h.expected_payload(False)=={'ifc/V4.ifc','ifc/V4.ifc.receipt.json','ifc-verification.json'}


def test_output_inside_native_input_is_rejected_before_mutation(tmp_path,monkeypatch):
    monkeypatch.setattr(h,'modules',lambda root:object())
    source=tmp_path/'native';source.mkdir();output=source/'new-output'
    with pytest.raises(ValueError,match='must not mutate retained'):h.run(tmp_path/'e.json',source,tmp_path/'other',output,root=ROOT)
    assert not output.exists()
