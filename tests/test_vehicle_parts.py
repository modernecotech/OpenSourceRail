from copy import deepcopy
import gzip,json,math
from pathlib import Path
import pytest
from engineering.station_rail.common import identity
from engineering.vehicle_parts import catalogue as c,publication as p,FLAGS


@pytest.fixture(scope='module')
def bundle():return c.build()


def test_whole_train_counts_are_expanded_once_and_parent_is_not_added(bundle):
    assert bundle['counted']['roles']['bogie']==12
    assert bundle['counted']['roles']['wheelset']==24
    assert bundle['counted']['roles']['door-leaf']==24
    assert bundle['counted']['roles']['fixed-seat']==264
    assert bundle['counted']['roles']['wheelchair-place']==12
    assert bundle['candidate_id']!=bundle['parent_candidate_id']
    assert bundle['parent_account_comparison']['added_to_new_leaf_sum'] is False
    assert bundle['installed_mass_kg'] is None and bundle['installed_CG_m'] is None
    expected=sum(r['quantity_per_train']*r['mass_each_kg']['base'] for r in bundle['parts'])
    assert bundle['nominal_mass_kg']['known_leaf_subtotal']['base']==pytest.approx(expected)
    assert all(bundle[k] is False for k in FLAGS)
    assert {r['candidate_id'] for r in bundle['parts']}=={bundle['candidate_id']}
    assert {r['candidate_id'] for r in bundle['downstream'].values()}=={bundle['candidate_id']}


def project(bundle,sections):
    return c.physical_projection(sections,bundle['parent_candidate_id'],bundle['physical_definition']['reference_interfaces'],bundle['integration_policy'])


def test_prices_routes_check_outcomes_and_order_do_not_change_physical_identity(bundle):
    sections=deepcopy(bundle['sections']);original=project(bundle,sections)
    sections[0]['parts'][0]['direct_cost_each_usd']['high']*=2
    sections[0]['assemblies'][0]['interfaces'][0]['verification']='Independently rechecked; geometry unchanged'
    sections[0]['parts'][0]['manufacturing'].append('Additional traceability check')
    for s in sections:s['parts'].reverse();s['materials'].reverse();s['assemblies'].reverse()
    assert project(bundle,sections)==original
    changed=c.build(sections=sections)
    assert changed['candidate_id']==bundle['candidate_id']
    assert changed['evaluation_id']!=bundle['evaluation_id']
    assert changed['input_section_ids']!=bundle['input_section_ids']


def test_battery_topology_and_component_rating_change_physical_identity(bundle):
    sections=deepcopy(bundle['sections']);services=next(s for s in sections if s['section_id']=='services')
    topology=services['electrical_assumptions']['battery'];topology['series_modules']=15;topology['parallel_strings']=5
    assert identity(project(bundle,sections))!=bundle['candidate_id']
    with pytest.raises(ValueError,match='topology/count'):c.build(sections=sections)
    led=next(r for r in bundle['parts'] if r['id']=='services/led-board');material=next(m for m in bundle['materials'] if m['id']==led['material_id'])
    new=deepcopy(led);new['proposed_electrical_W_each']=20
    assert identity(c.component_projection(new,material))!=led['component_definition_id']


@pytest.mark.parametrize('change',['duplicate','stock-mass','missing-route','zero','approval'])
def test_bad_definitions_are_rejected_before_any_export(bundle,change):
    sections=deepcopy(bundle['sections']);part=sections[0]['parts'][0]
    if change=='duplicate':sections[0]['parts'].append(deepcopy(part))
    if change=='stock-mass':part['mass_each_kg']['base']+=10;part['mass_each_kg']['high']+=10
    if change=='missing-route':
        for a in sections[0]['assemblies']:
            for step in a['assembly_steps']:step['part_ids']=[n for n in step['part_ids'] if n!=part['id']]
    if change=='zero':part['mass_each_kg']={k:0 for k in c.CASES}
    if change=='approval':sections[0]['physical_accepted']=True
    with pytest.raises(ValueError):c.validate_sections(sections,bundle['parent_candidate_id'])


def test_missing_component_mass_stays_unknown_and_never_zero(bundle):
    sections=deepcopy(bundle['sections']);part=next(r for r in sections[0]['parts'] if r['mass_basis']['kind']=='engineering-allowance')
    part['mass_each_kg']={k:None for k in c.CASES};part['mass_basis']['kind']='unknown'
    new=c.build(sections=sections)
    assert part['id'] in new['nominal_mass_kg']['unknown_leaf_ids']
    assert new['nominal_mass_kg']['complete_installed_quantity'] is None
    assert new['installed_mass_complete'] is False


def test_stock_formulas_do_not_treat_envelopes_as_solid_material():
    assert c.stock_volume(dict(kind='envelope',size_m=[1,2,3])) is None
    assert c.stock_volume(dict(kind='rhs',length_m=2,width_m=.2,depth_m=.3,wall_m=.01))==pytest.approx(2*(.2*.3-.18*.28))
    assert c.stock_volume(dict(kind='u_channel',length_m=1.5,width_m=.035,depth_m=.015,wall_m=.0015))*2710==pytest.approx(.378045)
    with pytest.raises(ValueError):c.stock_volume(dict(kind='rhs',length_m=2,width_m=.2,depth_m=.3,wall_m=.11))


def test_lighting_energy_terminal_and_coolant_counts_reconcile(bundle):
    e=bundle['electrical_checks']
    assert e['normal_light_output_W_per_car']==216
    assert e['normal_driver_capacity_W_per_car']==300
    assert e['half_branch_current_A']==2.25
    assert e['half_branch_voltage_drop_V']==pytest.approx(.29195775)
    assert e['gross_service_energy_kWh_per_car']==pytest.approx(82.8)
    assert e['total_lighting_input_W_per_train_hypothesis']==pytest.approx(1553.3333333333)
    assert e['emergency_lighting_energy_Wh_per_train_hypothesis']==pytest.approx(56.6666666667)
    assert e['capacity_or_hotel_target_changed'] is False


@pytest.mark.parametrize('field,value',[('cars',5),('body_length_m',16),('proposed_intercar_gap_m',0),('proposed_intercar_gap_m',-1)])
def test_formation_must_match_bounded_six_car_recipe(bundle,field,value):
    form=deepcopy(bundle['integration_policy']['formation']);form[field]=value
    with pytest.raises(ValueError):c.validate_formation(form,dict(cars=6,body_length_m=17))
    assert c.validate_formation(bundle['integration_policy']['formation'],dict(cars=6,body_length_m=17))==105.25


def test_business_draft_and_handoffs_are_disabled_and_candidate_bound(bundle):
    draft=p.business_draft(bundle)
    assert draft['disabled']==1 and draft['transactions_performed'] is False and draft['executable_work_order'] is False
    assert {r['candidate_id'] for r in draft['items']}=={bundle['candidate_id']}
    plan=p.assembly_plan(bundle)
    assert plan['production_capacity_verified'] is False and plan['tooling_capital_usd'] is None


def test_publication_recomputes_source_and_rejects_resealed_substitutes(tmp_path):
    out=tmp_path/'public';r=p.publish(output=out)
    assert r['verified'] and r['native_execution'] is False
    f=out/'summary.json';value=json.loads(f.read_bytes());value['nominal_mass_kg']['known_leaf_subtotal']['base']=1
    f.write_text(json.dumps(value));m=json.loads((out/'manifest.json').read_bytes());m['files_sha256']['summary.json']=c.digest(f)
    m['manifest_id']=identity({k:v for k,v in m.items() if k!='manifest_id'});(out/'manifest.json').write_text(json.dumps(m))
    with pytest.raises(ValueError,match='artifact differs'):p.verify(output=out)


def test_cached_web_assets_recheck_bytes_without_recompiling_each_response(tmp_path,monkeypatch):
    from engineering.vehicle_parts import web_assets
    out=tmp_path/'public';p.publish(output=out)
    monkeypatch.setattr(p,'OUTPUT',str(out))
    real=p.verify;calls=[]
    def verify(*a,**kw):calls.append(True);return real(*a,**kw)
    monkeypatch.setattr(p,'verify',verify);web_assets._verified.clear()
    for name in ('index.html','catalogue.js','manifest.json'):
        web_assets.verify_asset(c.ROOT,str(out)+'/'+name,out/name)
    assert len(calls)==1
    # A cached approval is not permission to alter a script or its sources.
    script=out/'catalogue.js';script.write_bytes(script.read_bytes()+b'\nchanged\n')
    with pytest.raises(ValueError,match='asset changed'):
        web_assets.verify_asset(c.ROOT,str(out)+'/catalogue.js',script)
    assert len(calls)==1
