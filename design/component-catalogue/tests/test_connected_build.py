"""Cross-model topology, supply, lifecycle and energy invariants for RFC 0034."""
from dataclasses import asdict, replace
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest
from ifcopenshell.util.element import get_psets

from osr_mech.buildable_stations import station_variant, _template_archetypes, DEFAULT_TEMPLATE
from osr_mech.common import StationArchetype
from osr_mech.station.layout import station_layout, step_free_reachability
from osr_mech.station.product_geometry import station_product_geometry
from osr_mech.civil.construction import CivilProductionInputs, civil_production_plan, ErectionMethod, erection_resources
from osr_mech.civil.shift_schedule import ShiftCycle, simulate_erection
from osr_mech.civil.supply import SupplierCapacity, Evidence, ErectionFront, DeliveryRoute, validate_supplier_allocations
from osr_mech.civil.costing import ComponentPurchase, reconcile_installed_rate, station_access_cost, island_net_saving
from osr_mech.civil.decked_pi import manufacturing_specification, suspended_load_kg
from osr_mech.battery_profiles import chronological_energy, vehicle_profile, resolve_profile
from osr_mech.network_energy_duty import network_duty
from engineering.interchange.station_ifc import export_variant

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'deployment/erpnext/apps/osr_erpnext'))
from osr_erpnext.construction_fleet import validate_transfers, validate_crew_task, fleet_economics


def island():
    config={**_template_archetypes(DEFAULT_TEMPLATE)['standard'],'elevation':'elevated','platform_length_m':121}
    return station_variant(StationArchetype.STANDARD,config)


def front(fid='a',access='a',path='a',supports=3):
    return ErectionFront(fid,'line',0 if fid=='a' else 50,50 if fid=='a' else 100,1,'launcher-'+fid,access,path,supports)


def simulate(fronts,cycle=ShiftCycle(),accepted=None,delivered=None,supports=None,days=4):
    return simulate_erection(fronts,cycle,accepted_beams_day=accepted or {},delivered_beams_day=delivered or {},
        supports_released_day=supports or {},buffer_capacity={f.id:10 for f in fronts},maximum_days=days)


def test_one_island_and_two_faces_agree_in_bom_cad_and_ifc(tmp_path):
    variant=island();layout=station_layout(variant.parameters)
    assert layout.quantities==dict(platform_count=1,boarding_face_count=2,track_count=2,lift_count=2,escalator_count=2,staircase_count=2,shaft_count=2)
    assert layout.faces[0].platform_id==layout.faces[1].platform_id
    lift_ids=[e.id for e in layout.equipment if e.kind=='lift']
    assert all(step_free_reachability(layout,{lift})['platforms_reachable']['platform-1'] for lift in lift_ids)
    assert not step_free_reachability(layout,set(lift_ids))['platforms_reachable']['platform-1']
    assert all(f.door_side==f.psd_side for f in layout.faces)
    products={item.id:asdict(item) for item in variant.product_items}
    for pid,kind in [('STN-ACC-P020','lift'),('STN-ACC-P040','escalator'),('STN-ACC-P050','staircase'),('STN-ACC-P060','shaft')]:
        geometry=station_product_geometry(products[pid],variant.parameters)
        assert len(geometry.children)==products[pid]['quantity']==layout.quantities[kind+'_count']
    edge=station_product_geometry(products['STN-CIV-P010'],variant.parameters)
    infill=station_product_geometry(products['STN-CIV-P050'],variant.parameters)
    assert edge.volume+infill.volume==pytest.approx(121000*8000*420)
    edges=station_product_geometry(products['STN-PLT-P010'],variant.parameters)
    for i,face in enumerate(layout.faces):
        coping,tactile=edges.children[2*i:2*i+2]
        assert coping.bounding_box().max.Z==tactile.bounding_box().max.Z==face.boarding_z_mm
        front_y=coping.bounding_box().max.Y if face.track_centre_y_mm>face.platform_face_y_mm else coping.bounding_box().min.Y
        assert front_y==face.platform_face_y_mm
    path=tmp_path/'station.ifc';export_variant(asdict(variant),path)
    import ifcopenshell
    psets=get_psets(ifcopenshell.open(str(path)).by_type('IfcBuilding')[0])['OSR_StationLayout']
    assert (psets['PhysicalPlatforms'],psets['BoardingFaces'],psets['Tracks'])==(1,2,2)
    assert json.loads(psets['TopologyAndAccess'])['quantities']==layout.quantities


def test_major_is_island_and_stacked_levels_have_transfer_links():
    configs=_template_archetypes(DEFAULT_TEMPLATE)
    major=station_layout(station_variant(StationArchetype.MAJOR,configs['major']).parameters)
    assert len(major.platforms)==1 and len(major.faces)==2
    assert major.platforms[0].y_mm==0
    stacked=station_layout(station_variant(StationArchetype.INTERCHANGE_ELEVATED,configs['interchange-elevated']).parameters)
    assert len({p.level for p in stacked.platforms})==2
    assert len(stacked.transfer_connections)==1
    assert len({f.boarding_z_mm for f in stacked.faces})==2


def test_elevated_exceptions_and_clear_width_are_checked():
    with pytest.raises(ValueError,match='exception_reason'):
        station_layout(dict(platform_layout='side',elevation='elevated',platform_count=2,platform_length_m=121))
    with pytest.raises(ValueError,match='clear width'):
        station_layout(dict(platform_layout='island',elevation='elevated',platform_count=1,platform_length_m=121,platform_width_m=4))


def test_two_shifts_change_resources_without_changing_installed_quantities():
    p=CivilProductionInputs(route_m=1000,elevated_m=1000,at_grade_m=0,gantry_count=18,independent_fronts=9)
    a=civil_production_plan(p);b=civil_production_plan(replace(p,shifts_day=2,handover_hours=1,maintenance_hours_day=1,productive_fraction=0.8))
    assert (a.primary_beams,a.foundations)==(b.primary_beams,b.foundations)
    assert b.erection_days<a.erection_days
    cycle=ShiftCycle(shifts_day=2,handover_hours=1,maintenance_hours_day=1,productive_fraction=0.8)
    assert cycle.bays_launcher_day==pytest.approx(1.4)
    assert cycle.bays_launcher_day<2*ShiftCycle().bays_launcher_day


def test_no_future_accepted_supply_or_support_credit_and_whole_bays():
    result=simulate([front(supports=1)],accepted={1:1,2:1,3:2},delivered={1:{'a':1},2:{'a':1},3:{'a':2}},supports={3:{'a':2}})
    assert result['daily'][0]['cumulative_erected_beams']==0
    assert result['daily'][1]['cumulative_erected_beams']==0
    for row in result['daily']:
        assert row['cumulative_erected_beams']<=row['cumulative_accepted_beams']
        assert row['cumulative_erected_beams']%2==0
    assert result['complete']
    with pytest.raises(ValueError,match='accepted components'):
        simulate([front()],delivered={1:{'a':2}})


@pytest.mark.parametrize('shared', ['access','path'])
def test_shared_obstructions_cannot_credit_simultaneous_output(shared):
    a=front('a','shared' if shared=='access' else 'a','shared' if shared=='path' else 'a')
    b=front('b','shared' if shared=='access' else 'b','shared' if shared=='path' else 'b')
    result=simulate([a,b],accepted={1:8},delivered={1:{'a':4,'b':4}},days=1)
    assert result['daily'][0]['cumulative_erected_beams']==2
    assert not result['complete']


def test_whole_beam_and_segmental_equipment_scope_is_distinct():
    whole=erection_resources(ErectionMethod.WHOLE_BEAM_LAUNCHER,10)
    segmental=erection_resources(ErectionMethod.SEGMENTAL,10)
    assert whole['equipment_family']!=segmental['equipment_family']
    assert whole['complete_beams']==20 and segmental['segments']==200
    assert segmental['stressing_operations']==20
    spec=manufacturing_specification(25)
    assert suspended_load_kg(spec,4000)>spec['manufactured_study_mass_kg']>spec['bare_section_mass_kg']
    assert spec['centre_of_gravity_study_m'][2]>1.155/2
    with pytest.raises(ValueError,match='approved'):
        suspended_load_kg(spec,4000,approved=True)


def test_candidate_capacity_is_zero_and_aggregate_contract_cannot_be_exceeded():
    data=dict(id='test-supplier',location='test-only',delivery_catchment=['test-city'],relevant_products=['station-slabs'],
        prestressing_qualified=False,beds=None,moulds=None,handling_limit_t=None,maximum_length_m=None,maximum_width_m=None,
        demonstrated_cycle_days=None,total_plant_units_day=None,contracted_units_day={},storage_units=None,dispatch_units_day=None,
        existing_commitments='unknown',qualification='candidate',required_upgrades=[],delivered_prices_usd={},commercial_terms='none',
        evidence=dict(units='units/day',source='test fixture',date='2026-10-06',confidence='test-only',qualification='unqualified',kind='user-selected-scenario'))
    supplier=SupplierCapacity(**{**data,'evidence':Evidence(**data['evidence'])})
    with pytest.raises(ValueError,match='not qualified'):
        supplier.allocate('station-slabs',1)
    qualified=replace(supplier,qualification='qualified',contracted_units_day={'station-slabs':4})
    with pytest.raises(ValueError,match='contracted capacity'):
        validate_supplier_allocations([qualified],[dict(supplier=supplier.id,product='station-slabs',units_day=3)]*2)


def test_logistics_require_route_and_payload_qualification():
    route=DeliveryRoute('route','supplier','front',1,3,100,4,12,0.5,0.5,25,100,12)
    assert route.capacity(80,25)==0
    released=replace(route,access_released=True,turning_space_released=True,loading_equipment_released=True,unloading_equipment_released=True,vehicle_tare_t=20)
    assert released.capacity(80,25)==12
    assert released.capacity(101,25)==0
    assert released.capacity(80,30)==0


def test_no_double_counted_tooling_erection_or_reuse_credit():
    with pytest.raises(ValueError,match='amortisation'):
        ComponentPurchase('beam',100,10000,100000,True).total()
    assert reconcile_installed_rate(1000000,None,{'launcher':9000000})['claimed_saving_usd'] is None
    assert reconcile_installed_rate(1000000,100000,{'erection':80000})['reconciled_total_usd']==980000
    assert island_net_saving(2e6,1e6,None,100000,100000) is None
    money=fleet_economics(9e6,100000,0.5,3e6,200000)
    assert money['initial_cash_purchase_usd']==9.1e6
    assert money['project_cost_allocation_usd']==3.1e6


def test_asset_transfer_and_worker_competence_cannot_overlap():
    with pytest.raises(ValueError,match='overlap'):
        validate_transfers([dict(asset='launcher',start='2027-01-01',finish='2027-03-01',transfer_days=7),dict(asset='launcher',start='2027-03-05',finish='2027-05-01',compatibility_accepted=True)])
    task=dict(department='Civil',unit='line',crew='crew',task='lift',front='front',shift=2,equipment='launcher',workers=['worker'],required_roles=['operator'],finish='2027-01-01')
    worker=dict(id='worker',crew='crew',shift=1,equipment='launcher',role='operator',commissioning_supervised=True,equipment_assessment_passed=True,competency_expires='2027-05-01')
    with pytest.raises(ValueError,match='another shift'):
        validate_crew_task(task,[worker])
    with pytest.raises(ValueError,match='expired'):
        validate_crew_task(task,[{**worker,'shift':2,'competency_expires':'2026-12-31'}])


def profiles():
    return json.loads((ROOT/'lib/templates/battery-profiles.json').read_text())['profiles']


def energy(onboard,stationary,*,two_trains=True,setup=0,outages=None):
    trains={k:dict(cars=1,initial_soc=0.3,energy_kwh_km=3,mass_factor=1.0,auxiliary_kw=0) for k in ('a','b') if two_trains or k=='a'}
    visits=[dict(train=k,site='s',arrival_min=0,departure_min=2,required_charge_kwh=20) for k in trains]
    return chronological_energy(onboard,stationary,trains,{'s':dict(modules=1,initial_soc=0.2,grid_kw=100,charger_kw=100,pv_kw=0)},visits,[],3,ambient_c=25,setup_seconds=setup,outages=outages)


def test_concurrent_chargers_setup_and_outages_constrain_energy():
    p=profiles();o=p['lfp-onboard-study'];s=p['lfp-stationary-study']
    single=energy(o,s,two_trains=False);two=energy(o,s)
    assert two['totals']['charger_kwh']<=100*2/60+1e-9
    assert two['trains']['a']['energy']<single['trains']['a']['energy']
    assert energy(o,s,setup=60)['totals']['charger_kwh']<two['totals']['charger_kwh']
    assert energy(o,s,outages={0,1,2})['totals']['charger_kwh']==0
    assert two['missed_charges']
    missed=chronological_energy(o,s,{'a':dict(cars=1,initial_soc=0.3,energy_kwh_km=3,mass_factor=1,auxiliary_kw=0)},
        {'s':dict(initial_soc=0.5,modules=1,pv_kw=0,grid_kw=500,charger_kw=500)},
        [dict(train='a',site='s',arrival_min=0,departure_min=1,required_charge_kwh=0,missed=True)],[],1,ambient_c=25)
    assert missed['missed_charges'][0]['reason']=='missed-opportunity'


def test_battery_selection_propagates_to_mass_energy_and_costs():
    p=profiles();lfp=p['lfp-onboard-study'];sodium=p['sodium-ion-onboard-study']
    a=vehicle_profile(34000,1,lfp,lfp);b=vehicle_profile(34000,1,lfp,sodium)
    assert b['vehicle_mass_kg']>a['vehicle_mass_kg'] and b['energy_mass_factor']>a['energy_mass_factor']
    assert b['installed_cost_usd']!=a['installed_cost_usd']
    with pytest.raises(ValueError,match='chemistry/application mismatch'):
        resolve_profile(dict(battery_profile=lfp['id'],battery_chemistry='sodium-ion'),dict(profiles=p),'onboard')
    assert energy(sodium,p['sodium-ion-stationary-study'])['totals']!=energy(lfp,p['lfp-stationary-study'])['totals']


def test_regeneration_waits_for_arrival_and_replacements_reset_soh():
    p=profiles();o=p['lfp-onboard-study'];s=p['lfp-stationary-study']
    args=({'a':dict(cars=1,initial_soc=0.2,energy_kwh_km=3,mass_factor=1.0,auxiliary_kw=0)}, {}, [],
          [dict(train='a',minute=0,distance_km=1,regenerative_kwh=1,arrival_minute=2,travel_minutes=2)])
    early=chronological_energy(o,s,*args,1,ambient_c=25)
    later=chronological_energy(o,s,*args,3,ambient_c=25)
    assert early['totals']['regeneration_accepted_kwh']==0
    assert later['totals']['regeneration_accepted_kwh']>0
    short_life={**o,'calendar_life_years':1/(365.25*1440)}
    replacement=chronological_energy(short_life,s,args[0],{},[],[],3,ambient_c=25)
    assert replacement['trains']['a']['replacements']==3
    assert replacement['trains']['a']['soh']==1.0


def test_generated_connected_package_has_revision_assumptions_and_hashes():
    folder=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/engineering/connected-build'
    manifest=json.loads((folder/'manifest.json').read_text())
    assert len(manifest['source_revision'])==64
    assert manifest['source_revision_kind']=='sha256-input-content'
    assert set(('units','source','as_of','confidence','qualification'))<=set(manifest['assumptions']['schema'])
    for name,expected in manifest['output_sha256'].items():
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==expected
    civil=json.loads((folder/'civil.json').read_text())
    assert not civil['actual_evidence_schedule']['complete']
    for case in civil['conditional_scenarios'].values():
        assert sum(case['completed_bays'].values())==sum(row['running_bays'] for row in civil['lines'])
        assert case['maximum_launchers']==18 and case['assumed_transporters']==72
        assert case['complete']
    spans=json.loads((folder/'span-layout.json').read_text())
    assert len({s['id'] for s in spans['spans']})==len(spans['spans'])
    assert spans['quantities']['total_alignment_m']==pytest.approx(sum(l['running_elevated_m'] for l in civil['lines']),abs=.555)
    ordinary=[s for s in spans['spans'] if s['beam_variant']]
    assert 2*len(ordinary)==spans['quantities']['pi20_beams']+spans['quantities']['pi25_beams']
    assert all(s['quantity'] is None and not s['component_ids'] for s in spans['spans'] if not s['beam_variant'])
    transfers=json.loads((folder/'erp-drafts.json').read_text())['conditional_baghdad_reassignments']
    assert len(transfers)==6 and all(not t['allocation_approved'] for t in transfers)
    from datetime import date
    assert all((date.fromisoformat(t['destination_start'])-date.fromisoformat(t['source_finish'])).days>=t['transfer_days'] for t in transfers)


def test_incompatible_charger_voltage_never_reuses_existing_power_rating():
    p=profiles();onboard={**p['lfp-onboard-study'],'voltage_min_v':900,'nominal_voltage_v':950,'voltage_max_v':1000}
    result=chronological_energy(onboard,p['lfp-stationary-study'],{'a':dict(cars=1,initial_soc=0.3,energy_kwh_km=3,mass_factor=1,auxiliary_kw=0)},
        {'s':dict(initial_soc=0.5,modules=1,pv_kw=0,grid_kw=500,charger_kw=500,charger_bus_voltage_v=650)},
        [dict(train='a',site='s',arrival_min=0,departure_min=1,required_charge_kwh=10)],[],1,ambient_c=25)
    assert result['totals']['charger_kwh']==0
    assert not result['charging_voltage_compatible']['s']


def test_launcher_can_reassign_after_finish_and_relocation_without_overlap():
    first=replace(front('a'),relocation_days=2)
    second=replace(front('b'),launcher=first.launcher,planned_start_day=6)
    result=simulate([first,second],accepted={1:8},delivered={1:{'a':4,'b':4}},days=12)
    assert result['complete']
    assert result['finish_days']['b']>result['finish_days']['a']+first.relocation_days
    assert all(sum(f['bays_complete'] for f in row['fronts'])>=0 for row in result['daily'])
    assert result['daily'][-1]['cumulative_erected_beams']==8


def test_disconnected_intervals_need_a_new_support_pair():
    f=replace(front(),end_chainage_m=100,available_foundations=3,work_intervals_m=((0,25),(75,100)))
    result=simulate([f],accepted={1:4},delivered={1:{'a':4}},days=2)
    assert result['completed_bays']['a']==1
    assert not result['complete']
    released=simulate([f],accepted={1:4},delivered={1:{'a':4}},supports={2:{'a':1}},days=2)
    assert released['complete']


def test_identified_sections_require_relocation_before_next_span():
    from osr_mech.civil.span_layout import plan_spans
    spans=plan_spans('line',[(0,25),(75,100)])
    f=replace(front(),end_chainage_m=100,available_foundations=4,
        work_intervals_m=((0,25),(75,100)),planned_spans=tuple(spans),section_relocation_days=2)
    result=simulate([f],accepted={1:4},delivered={1:{'a':4}},days=6)
    assert result['finish_days']['a']==4
    assert result['disconnected_section_moves']['a']==1
    assert [r['fronts'][0]['limiting_resource'] for r in result['daily'][1:3]]==['disconnected-section-relocation']*2


def test_ring_reassignment_retains_spans_machines_and_shared_transport_capacity():
    from osr_mech.civil.span_layout import plan_spans
    spec=importlib.util.spec_from_file_location('connected_study',ROOT/'tools/automation/connected-build-study.py')
    generator=importlib.util.module_from_spec(spec);spec.loader.exec_module(generator)
    ring=plan_spans('ring',[(0,400)])
    def assigned(identity,line,spans,launcher):
        return ErectionFront(identity,line,spans[0]['start_chainage_m'],spans[-1]['end_chainage_m'],1,
            launcher,identity,identity,20,work_intervals_m=tuple((s['start_chainage_m'],s['end_chainage_m']) for s in spans),planned_spans=tuple(spans))
    initial=[assigned('r1','ring',ring[:8],'machine-1'),assigned('r2','ring',ring[8:],'machine-2')]
    initial += [assigned(f'd{i}',f'radial-{i}',plan_spans(f'radial-{i}',[(0,25)]),f'machine-{i+3}') for i in range(6)]
    moved=generator.reassigned_ring_fronts(initial,{f.id:5 for f in initial},'ring',{})
    assert sorted(s['id'] for f in initial for s in f.planned_spans)==sorted(s['id'] for f in moved for s in f.planned_spans)
    assert {f.launcher for f in moved}=={f.launcher for f in initial}
    added=[f for f in moved if f.predecessors]
    assert len(added)==6 and all(f.available_foundations==0 and f.planned_start_day>5 for f in added)
    cfg=generator.read(ROOT/'lib/templates/accelerated-build.toml')
    chain=generator.study_supply_chain(moved,ShiftCycle(),cfg['erection'],cfg['logistics'],cfg['schema']['as_of'])
    assert len({r.fleet_id for r in chain.routes})==8


def test_grid_replenishment_respects_policy_outages_and_import_limit():
    p=profiles();site=dict(initial_soc=0.2,modules=1,pv_kw=0,grid_kw=100,charger_kw=100)
    def run(policy,outages=None):
        return chronological_energy(p['lfp-onboard-study'],p['lfp-stationary-study'],{},
            {'s':{**site,'allow_grid_storage_recharge':policy,'storage_recharge_target_soc':.8}},[],[],60,
            ambient_c=25,outages=outages)
    enabled=run(True);disabled=run(False);outage=run(True,set(range(60)))
    assert enabled['storage_kwh']['s']>disabled['storage_kwh']['s']
    assert 0<enabled['totals']['grid_storage_replenishment_kwh']<=enabled['totals']['grid_kwh']<=100+1e-9
    assert disabled['totals']['grid_storage_replenishment_kwh']==outage['totals']['grid_storage_replenishment_kwh']==0


def test_reserve_train_minutes_are_distinct_from_affected_journeys():
    p=profiles()
    result=chronological_energy(p['lfp-onboard-study'],p['lfp-stationary-study'],
        {'a':dict(cars=1,initial_soc=.01,energy_kwh_km=3,mass_factor=1,auxiliary_kw=0,
                  service_journeys=[(0,3,'trip-a')])},{},[],[],3,ambient_c=25)
    assert result['reserve_violation_train_minutes']==3
    assert result['distinct_energy_affected_journeys']==1
    assert not result['service_disruption_feedback_modelled']


def test_bounded_diagnostics_preserve_energy_and_all_shortfall_counts():
    p=profiles();trains={'a':dict(cars=1,initial_soc=.01,energy_kwh_km=3,mass_factor=1,auxiliary_kw=10,
        service_intervals=[(.5,30.5)],service_journeys=[(.5,30.5,'first')])}
    def run(retain):
        return chronological_energy(p['lfp-onboard-study'],p['lfp-stationary-study'],trains,{},[],[],40,
            ambient_c=25,retain_shortfalls=retain)
    full=run(True);bounded=run(False)
    assert bounded['totals']==full['totals'] and bounded['trains']==full['trains']
    assert bounded['shortfalls']==full['shortfalls'][:20]
    assert bounded['shortfall_events']==len(full['shortfalls'])>20
    assert bounded['reserve_violation_train_minutes']==full['reserve_violation_train_minutes']
    assert bounded['distinct_energy_affected_journeys']==full['distinct_energy_affected_journeys']==1


def test_continuous_state_preserves_clock_solar_outages_and_degradation():
    p=profiles();trains={'a':dict(cars=1,initial_soc=.8,energy_kwh_km=3,mass_factor=1,auxiliary_kw=10)}
    sites={'s':dict(initial_soc=.2,modules=1,pv_kw=100,grid_kw=100,charger_kw=100,allow_grid_storage_recharge=True,storage_recharge_target_soc=.8)}
    outages=set(range(450,465))
    whole=chronological_energy(p['lfp-onboard-study'],p['lfp-stationary-study'],trains,sites,[],[],600,outages=outages,ambient_c=25)
    state=None;totals={k:0 for k in whole['totals']}
    for offset in range(0,600,10):
        state=chronological_energy(p['lfp-onboard-study'],p['lfp-stationary-study'],trains,sites,[],[],10,outages=outages,ambient_c=25,minute_offset=offset,initial_state=state)
        for k,v in state['totals'].items():totals[k]+=v
    assert state['trains']==whole['trains'] and state['storage_soh']==whole['storage_soh']
    assert state['storage_kwh']==whole['storage_kwh']
    assert totals==pytest.approx(whole['totals'],abs=1e-8)
