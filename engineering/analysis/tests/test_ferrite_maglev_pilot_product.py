"""Independent accounting/configuration/path controls for provisional pilot items."""
from copy import deepcopy
import gzip
import json
import math
import pytest
from engineering.ferrite_maglev import pilot_product as p

def test_profiles_and_identity_are_explicit():
    x=p.configuration_profile();y=p.configuration_profile('baghdad-50kwh-aw3')
    assert (x['battery_kwh_per_car'],x['target_tare_kg'],x['target_aw3_kg'])==(30.,14200.,26200.)
    assert (y['battery_kwh_per_car'],y['target_tare_kg'],y['target_aw3_kg'])==(50.,14400.,26400.)
    assert x['configuration_sha256']!=y['configuration_sha256']
    c=deepcopy(x);c.pop('configuration_sha256');assert p.digest(p.encoded(c))==x['configuration_sha256']
    with pytest.raises(ValueError):p.configuration_profile('all-primary-configurations')

def test_allowance_substitution_and_overrun_never_double_count():
    r=p.reconcile_allowance('a',100,[dict(id='part',value=70)])
    assert r['defined_total']==70 and r['residual_allocation']==30 and r['reconciled_total']==100
    r=p.reconcile_allowance('a',100,[dict(id='part',value=130)])
    assert r['residual_allocation']==0 and r['reconciled_total']==130 and r['overrun']==30
    with pytest.raises(ValueError):p.reconcile_allowance('a',100,[dict(id='x',value=1),dict(id='x',value=2)])
    with pytest.raises(ValueError):p.reconcile_allowance('a',100,[dict(id='x',value=float('nan'))])

def test_real_defined_material_and_copper_increase_inadequate_support_budget():
    a=p.mass_ledger();b=p.mass_ledger(p.configuration_profile('baghdad-50kwh-aw3'))
    assert a['defined_assembled_material_mass_kg']==pytest.approx(9492.609052646612,abs=1e-6)
    assert a['winding_copper_added_once_kg']==pytest.approx(262.176768,abs=1e-6)
    assert a['reconciled_tare_kg']>16000 and not a['target_closed']
    assert b['reconciled_tare_kg']-a['reconciled_tare_kg']==pytest.approx(200.)
    support=next(r for r in a['rows'] if r['id']=='magnetic-equipment')['definition']
    assert support['original_allocation']==1500 and support['overrun']>2000
    assert next(r for r in a['rows'] if r['id']=='growth-reserve')['mass_kg']==1800
    assert a['reconciled_aw3_kg']-a['reconciled_tare_kg']==12000.

def test_lifecycle_products_have_exact_unique_bom_identity():
    items=p.products();assert len(items)==3
    for item in items:
        assert len(item['product_revision_sha256'])==64 and item['production_released'] is False
        assert len({r['id'] for r in item['bom']})==len(item['bom'])
    cartridge=items[0]
    assert cartridge['bom'][0]['mass_kg']==pytest.approx(117.75)
    assert cartridge['bom'][2]['quantity']==1 and cartridge['bom'][3]['quantity']==2
    assert cartridge['bom'][4]['mass_state']=='Missing'

def test_current_requirement_load_profiles_do_not_inherit_legacy_masses():
    from engineering.ferrite_maglev import requirements
    rows={r['id']:r for r in requirements.register()['requirements']}
    assert 'all-primary-configurations' not in rows['MAG-051']['applicability']
    for row in rows['MAG-051']['screen_profiles']:
        assert row['screen_force_n']==pytest.approx(row['aw3_mass_kg']*9.81*row['multiplier'])
    for row in rows['MAG-051']['controlled_screen_profiles']:
        profile=p.configuration_profile(row['id'])
        assert row['aw3_mass_kg']==pytest.approx(profile['controlled_aw3_kg'])
        assert row['screen_force_n']==pytest.approx(profile['provisional_dynamic_support_force_n'])
    assert [r['aw3_mass_kg'] for r in rows['MAG-051']['historical_profiles']]==[30000,31000]
    assert 'located interstation booster' in rows['SYS-003']['requirement']

def test_swept_bound_checks_entire_translation_not_only_endpoints():
    v=dict(retained_parts=[dict(id='moving',kind='box',at_m=[0,0,0],size_m=[.1,.1,.1])],equipment=[],fixed_parts=[dict(id='obstruction',kind='box',at_m=[0,0,-.393],size_m=[.1,.1,.001])])
    check=p.path_check(v)
    assert not check['clear_under_declared_box_bounds']
    assert check['conservative_swept_aabb_collisions']==[['moving','obstruction']]
    assert check['accepted'] is False

def test_counted_detachable_elbow_repair_clears_retained_bounds():
    old=p.path_check();v=p.redesigned_bay();new=p.path_check(v)
    assert len(old['conservative_swept_aabb_collisions'])==48
    assert new['clear_under_declared_box_bounds'] and new['conservative_swept_aabb_collisions']==[]
    hardware=v['changed_hardware']
    assert (hardware['new_splice_plates'],hardware['new_m8_bolts'],hardware['reused_main_interface_m12_bolts'])==(4,16,16)
    assert hardware['additional_stock_mass_kg_per_car']==pytest.approx(106.01367954281218)
    assert not v['selected'] and not new['accepted']

def test_rotated_cylinder_bounds_use_declared_axis():
    b=p.bounds(dict(kind='cylinder',at_m=[0,0,0],size_m=[.02,.02,.2],cylinder_axis='y'))
    assert b==[[0,0,0],[.02,.2,.02]]

def test_publication_detects_coherently_rehashed_ledger(tmp_path):
    p.publish(tmp_path);assert p.verify(tmp_path)['verified']
    m=json.loads((tmp_path/'manifest.json').read_text());r=json.loads(gzip.decompress((tmp_path/'study.json.gz').read_bytes()))
    r['ledger'][0]['reconciled_tare_kg']=14200.
    b=gzip.compress(p.encoded(r),mtime=0);(tmp_path/'study.json.gz').write_bytes(b)
    m['files_sha256']['study.json.gz']=p.digest(b);(tmp_path/'manifest.json').write_bytes(p.encoded(m))
    with pytest.raises(ValueError,match='derived ledger'):p.verify(tmp_path)
