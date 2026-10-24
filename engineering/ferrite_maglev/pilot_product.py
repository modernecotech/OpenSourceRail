"""One provisional product identity, allowance substitution and equipped-bay paths.

Defined means calculated geometry/quantity, never qualified material or a quote.
Allocations are retained only for unrepresented scope; overruns remain visible.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import csv
import gzip
import io
import json
import math
import subprocess
import tempfile
import tomllib
from . import assembled_body, configuration, drive_design, geometry, manufacturing, model, moving_train, station
from engineering.factory_examples import models

ROOT=model.ROOT
INPUT=Path(__file__).with_name('pilot-product.toml')
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/pilot-product'
TEST=ROOT/'engineering/analysis/tests/test_ferrite_maglev_pilot_product.py'
SCHEMA='osr-pilot-product/1'
FLAGS={**model.FLAGS,'physical_output_authorised':False,'automatic_adoption':False}
MAX_RAW=64*1024*1024

def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def digest(v):return sha256(v).hexdigest()
def source_paths():
    paths={Path(__file__),INPUT,TEST,Path(manufacturing.__file__),manufacturing.INPUT,
        Path(moving_train.__file__),moving_train.INPUT,Path(drive_design.__file__),drive_design.INPUT,
        Path(__file__).with_name('requirements.py'),Path(__file__).parent/'data/requirements.json',
        *(ROOT/n for n in drive_design.sources()),*configuration.source_paths(),*assembled_body.source_paths()}
    # These calculations consume analytical definitions, not generated parent
    # packets. Native parent acceptance is not inherited through a receipt.
    return sorted(p for p in paths if not p.is_relative_to(ROOT/'docs/design-engine'))
def sources():return {p.relative_to(ROOT).as_posix():digest(p.read_bytes()) for p in source_paths()}
def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!='osr-pilot-product-input/1' or a['profiles']!=['baghdad-30kwh-aw3','baghdad-50kwh-aw3'] or a['default_profile']!=a['profiles'][0]:raise ValueError('bounded pilot profiles required')
    for k,v in a.items():
        if type(v) in (int,float) and (not math.isfinite(v) or v<=0):raise ValueError('positive pilot assumption required: '+k)
    if a['replacement_path_samples']!=41:raise ValueError('fixed independently checked path sampling required')
    return a

def configuration_profile(profile_id='baghdad-30kwh-aw3'):
    a=load()
    if profile_id not in a['profiles']:raise ValueError('unknown explicit pilot configuration')
    _,c,_=model.load();battery=30. if profile_id==a['profiles'][0] else 50.;mass=model.mass(c,c['mass']['ferrite_base'],battery)
    m=moving_train.load();d=drive_design.load();cfg=configuration.selected()
    value=dict(schema='osr-pilot-product-configuration/1',id=profile_id,revision=a['revision'],cars=6,
        battery_kwh_per_car=battery,target_tare_kg=mass['tare_kg'],passenger_payload_kg=mass['aw3_kg']-mass['tare_kg'],target_aw3_kg=mass['aw3_kg'],
        body=dict(revision=assembled_body.load()['revision'],longitudinal_stiffness_n_m=assembled_body.axial_screen()['drilled_body_and_coupler_series_stiffness_n_m'],historical_ideal_force_stiffness_n_m=m['coupler_stiffness_n_m'],inertia_roll_kg_m2=m['inertia_roll_kg_m2'],inertia_pitch_kg_m2=m['inertia_pitch_kg_m2'],stiffness_role='geometry-derived drilled GFRP tubes in series with coupler; rigid-car lumped sensitivity, not flexible-body qualification'),
        magnetic=dict(revision=d['revision'],modules_per_car=d['support']['modules_per_car'],ferrite_allocation_kg=c['mass']['ferrite_base'],support_winding=d['support']),
        guideway=dict(configuration_revision=cfg.revision,section=cfg.record()['configuration']['civil']),
        service=dict(profile='current-fixed-line-station-and-located-booster',headway_target_s=180.,hot_services_kw_per_car=60.,ambient_reference_c=40.,passenger_load='AW3 160 persons at75kg'),
        controls=dict(support='Rust array allocator plus drives current kernel',protection='offline independently protected fixed-line study; no field adapter'),
        historical_benchmarks=['moving-six-car-1000m-88s-30kwh-26200kg','drive-construction-support-50kwh-26400kg'],source_sha256=sources(),**FLAGS)
    accounted=mass_ledger(value)
    value.update(controlled_tare_kg=accounted['reconciled_tare_kg'],controlled_aw3_kg=accounted['reconciled_aw3_kg'],
        controlled_load_profile='component-accounted-aw3; original26.2/26.4t cases retained as historical targets',
        provisional_dynamic_support_multiplier=1.3,provisional_dynamic_support_force_n=accounted['reconciled_aw3_kg']*9.81*1.3)
    value['configuration_sha256']=digest(encoded(value))
    return value

def reconcile_allowance(identity,allocation,defined):
    """Scope-exclusive substitution: defined + unrepresented residual, no duplicate."""
    if type(allocation) not in (int,float) or not math.isfinite(allocation) or allocation<0:raise ValueError('finite nonnegative allowance required')
    ids=[r['id'] for r in defined]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate definition in allowance')
    values=[r['value'] for r in defined]
    if any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in values):raise ValueError('finite defined quantities required')
    total=math.fsum(values);residual=max(0.,allocation-total)
    if any(r.get('state','Defined') not in {'Defined','Allocated'} for r in defined):raise ValueError('represented ledger value needs explicit state')
    actual_defined=math.fsum(r['value'] for r in defined if r.get('state','Defined')=='Defined')
    return dict(id=identity,original_allocation=allocation,defined=deepcopy(defined),defined_total=actual_defined,represented_total=total,explicit_allocated_total=total-actual_defined,residual_allocation=residual,
        reconciled_total=total+residual,overrun=max(0.,total-allocation),substitution_rule='Defined scope replaces the same scope allocation; remaining allowance retains unrepresented equipment. No double counting or negative reserve.')

def mass_ledger(profile=None):
    cfg=configuration_profile() if profile is None else profile;a=load();_,c,_=model.load();v=assembled_body.definition();s=drive_design.support()
    groups={}
    for p in v['parts']:
        if p['role'] not in {'guideway-context','magnetic-envelopes'}:
            groups.setdefault(p['role'],0.);groups[p['role']]+=p['volume_m3']*p['density_assumption_kg_m3']
    ferrite=math.fsum(p['volume_m3']*p['density_assumption_kg_m3'] for p in v['parts'] if p['material']=='ferrite')
    body_roles=['panel-floor','panel-roof','panel-side','panel-end','corner-bonds','corner-laps','primary-frame']
    body=math.fsum(groups[k] for k in body_roles)
    support=math.fsum(groups.values())-body-ferrite
    masses=c['mass'];pools=[reconcile_allowance('body-and-passenger-systems',masses['structural_body_floor_doors_glazing_interior'],[dict(id='defined-body-material',value=body)]),
        reconcile_allowance('ferrite',masses['ferrite_base'],[dict(id='defined-cartridge-ferrite',value=ferrite)]),
        reconcile_allowance('magnetic-equipment',masses['support_guidance_cores_windings_carriers_drives_sensors_cooling'],[
            dict(id='defined-carriers-hardpoints-cartridge-steel',value=support),dict(id='defined-winding-copper',value=s['copper_kg_per_car'])])]
    # Ancillaries are explicit NEW allocations in the magnetic scope; they are
    # not added once per car on top of a hidden full-car equipment allocation.
    ancillary=24*sum(a[k] for k in ('bay_connector_allowance_kg','bay_harness_allowance_kg','bay_cooling_allowance_kg','bay_cover_allowance_kg'))
    pools[2]=reconcile_allowance('magnetic-equipment',pools[2]['original_allocation'],pools[2]['defined']+[dict(id='bay-ancillaries-explicit-allocation',value=ancillary,state='Allocated')])
    other=[('capture-and-brake',masses['capture_landing_emergency_braking']),('battery',cfg['battery_kwh_per_car']*10.),('hvac',masses['cabin_hvac_ducting']),('train-controls-wiring',masses['auxiliary_electrical_train_controls_wiring']),('couplers-gangway-solar',masses['couplers_gangway_interfaces_solar']),('growth-reserve',masses['growth_reserve'])]
    total=math.fsum(p['reconciled_total'] for p in pools)+math.fsum(x[1] for x in other)
    rows=[dict(id=p['id'],mass_state='Defined+Allocated' if p['residual_allocation'] or p['explicit_allocated_total'] else 'Defined',mass_kg=p['reconciled_total'],definition=p) for p in pools]
    rows += [dict(id=k,mass_state='Allocated',mass_kg=v,geometry_state='Missing',cost_state='Allocated') for k,v in other]
    return dict(configuration_sha256=cfg.get('configuration_sha256'),unit='kg_per_car',rows=rows,defined_assembled_material_mass_kg=math.fsum(groups.values()),
        winding_copper_added_once_kg=s['copper_kg_per_car'],defined_mass_kg=math.fsum(p['defined_total'] for p in pools),allocated_mass_kg=total-math.fsum(p['defined_total'] for p in pools),bay_ancillary_allocation_kg=ancillary,original_target_tare_kg=cfg['target_tare_kg'],
        reconciled_tare_kg=total,reconciled_aw3_kg=total+cfg['passenger_payload_kg'],target_overrun_kg=total-cfg['target_tare_kg'],
        target_closed=total<=cfg['target_tare_kg'],full_equipped_mass_accepted=False,
        missing=['Detailed doors/glazing/interior mass within body residual','Qualified complete cores/drives/cooling/harness and evacuation equipment','Measured equipment CG/inertia and installed serial masses'],**FLAGS)

def products(profile=None):
    cfg=configuration_profile() if profile is None else profile;d=assembled_body.definition();prefix='cartridge/1/06/'
    ps=[p for p in d['parts'] if p['id'].startswith(prefix) and p['material']!='winding-envelope'];s=drive_design.support();a=load()
    ferrite=math.fsum(p['volume_m3']*p['density_assumption_kg_m3'] for p in ps if p['material']=='ferrite');carrier=math.fsum(p['volume_m3']*p['density_assumption_kg_m3'] for p in ps if p['material']!='ferrite')
    q=geometry.guideway_quantities(25.);w=drive_design.winding(zone=350.)
    def bom(i,q,u,mass=None,cost=None,state='Defined'):
        return dict(id=i,quantity=q,unit=u,mass_kg=mass,cost_usd=cost,definition_state=state,mass_state='Defined' if mass is not None and state=='Defined' else 'Allocated' if mass is not None else 'Missing',cost_state='Allocated' if cost is not None else 'Missing',space_state='Defined' if state=='Defined' else 'Missing')
    rows=[dict(id='OSR-PILOT-MAGNETIC-CARTRIDGE',quantity_per_car=24,geometry_source_ids=[p['id'] for p in ps],geometry_sha256=digest(encoded(ps)),bom=[
        bom('magnetic/cartridge/ferrite',1,'set',ferrite,ferrite*manufacturing.load()['rates']['ferrite_per_kg']),
        bom('magnetic/cartridge/carrier',1,'set',carrier),bom('magnetic/cartridge/lift-coil',1,'coil',s['coil']['copper_kg'],s['coil']['copper_kg']*a['support_copper_usd_per_kg']),
        bom('magnetic/cartridge/guide-coils',2,'coil',2*s['coil']['copper_kg'],2*s['coil']['copper_kg']*a['support_copper_usd_per_kg']),
        bom('magnetic/cartridge/sensors',2,'independent chain',None,a['sensor_pair_allowance_usd'],'Allocated'),
        bom('magnetic/cartridge/drive',2,'current circuit',None,2*a['drive_circuit_allowance_usd'],'Allocated')]),
        dict(id='OSR-PILOT-GUIDEBEAM-25M',quantity_per_car=0,geometry_source_ids=['beam-25m'],geometry_sha256=digest(encoded(q)),bom=[bom('guidebeam/concrete',q['beam_concrete_mass_kg']/geometry.MATERIALS['concrete'],'m3',q['beam_concrete_mass_kg']),bom('guidebeam/passive-rail',1,'set',q['magnetic_rail_mass_kg']),bom('guidebeam/reinforcement-allocation',25.,'direction-m',None,None,'Allocated')]),
        dict(id='OSR-PILOT-LAUNCH-CASSETTE-2P5M',quantity_per_car=0,geometry_source_ids=['winding-face-cassette-2p5m'],geometry_sha256=digest(encoded(w['schedule'])),bom=[bom('launch/cassette/copper',w['coils_per_face_cassette'],'coil',w['coils_per_face_cassette']*w['copper_per_coil']['copper_kg']),bom('launch/cassette/support-allocation',1,'cassette',None,None,'Allocated'),bom('launch/cassette/interfaces-allocation',1,'set',None,None,'Allocated')])]
    for r in rows:r.update(configuration_sha256=cfg['configuration_sha256'],revision=load()['revision'],product_revision_sha256=digest(encoded(r)),production_released=False)
    return rows

def bay_definition():
    d=assembled_body.definition();prefix='cartridge/1/06/';selected=[p for p in d['parts'] if p['id'].startswith(prefix) and p['material']!='winding-envelope']
    # A separately identified packaging candidate: three coil packs on the
    # underside, not an assertion that the retained two winding windows close.
    extra=[]
    def box(i,size,at,role):extra.append(dict(id=i,kind='box',size_m=size,at_m=at,role=role))
    for j,x in enumerate((.15,.43,.71)):box(f'bay/coil-{j}',[.174,.134,.060],[x,1.0,-.424],'replaceable')
    for j,x in enumerate((.10,.84)):box(f'bay/sensor-{j}',[.035,.025,.020],[x,1.155,-.350],'replaceable')
    box('bay/power-connector',[.05,.04,.04],[.08,1.20,-.32],'disconnect-before-removal')
    box('bay/signal-connector',[.04,.03,.035],[.18,1.20,-.32],'disconnect-before-removal')
    box('bay/cooling-interface',[.07,.035,.025],[.30,1.20,-.32],'disconnect-before-removal')
    box('bay/removable-cover',[.98,.005,.18],[.01,1.27,-.46],'remove-first')
    routes=[dict(id='power',points_m=[[.105,1.24,-.30],[.105,1.24,-.20],[.50,1.24,-.20]],cable_outer_diameter_m=.016,minimum_bend_radius_m=.080),
        dict(id='signal',points_m=[[.20,1.23,-.30],[.20,1.23,-.15],[.70,1.23,-.15]],cable_outer_diameter_m=.008,minimum_bend_radius_m=.040),
        dict(id='earth',points_m=[[.85,1.22,-.30],[.85,1.22,-.10]],cable_outer_diameter_m=.006,minimum_bend_radius_m=.030)]
    return dict(schema='osr-equipped-bay-packaging/1',source_definition_sha256=digest(encoded(d)),retained_parts=selected,equipment=extra,cable_routes=routes,
        positive_retention=[p['id'] for p in selected if '/keeper-' in p['id'] or '/bolt-' in p['id']],
        fixed_parts=[p for p in d['parts'] if not p['id'].startswith(prefix) and p['role']!='magnetic-envelopes'],
        steps=['isolate, prove dead, support module','remove cover','disconnect power/signal/cooling and bond','release positive retention with supported module','lower module on guided lift; protect magnetic attraction','inspect, replace and torque; electrical and gap calibration; independent handback'],
        qualified_magnetic_circuit=False,complete_harness_drawing=False,**FLAGS)

def redesigned_bay():
    """Counted alternative: detachable elbow + segmented collector, lateral lift.

    The new collector splices need strength/stiffness/fatigue qualification. This
    is a geometry experiment, never permission to cut an installed member.
    """
    v=bay_definition();byid={p['id']:p for p in v['fixed_parts']};moving=[];remaining=[];released=[]
    for p in v['fixed_parts']:
        i=p['id']
        if i.startswith(('hardpoint/1/06/carrier-','carrier/upright-1-6/','carrier/cantilever-1-6/')):moving.append(p)
        elif i.startswith('hardpoint/1/06/bolt-'):released.append(p)
        elif i.startswith('carrier/collector-1/'):
            left=deepcopy(p);left['id']=i+'/fixed-left';left['size_m'][0]=5.995
            right=deepcopy(p);right['id']=i+'/fixed-right';right['at_m'][0]=1.005;right['size_m'][0]=4.995
            mid=deepcopy(p);mid['id']=i+'/detachable-bay';mid['at_m'][0]=.005;mid['size_m'][0]=.99
            remaining.extend([left,right]);moving.append(mid)
        else:remaining.append(p)
    v['retained_parts'].extend(moving);v['fixed_parts']=remaining;v['translation_m']=[.0,.90,.0]
    plate_mass=4*.20*.008*.080*geometry.MATERIALS['steel']
    bolt_mass=16*geometry.MATERIALS['steel']*(math.pi*.008**2*.04/4+math.pi*.013**2*.005/4+math.pi*(.013**2-.008**2)*.006/4)
    v.update(id='segmented-collector-detachable-elbow-lateral-1',released_retention_ids=[p['id'] for p in released],
        released_mating_interfaces=[dict(moving='hardpoint/1/06/carrier-flange',fixed='hardpoint/1/06/spreader',
            release='Support assembly and remove16M12 retention bolts before normal separation')],
        new_interfaces=[dict(id='collector-splice-'+str(i),location_x_m=x,plates=2,plate_size_m=[.20,.008,.080],new_m8_bolts=8,qualified=False) for i,x in enumerate((0.,1.))],
        changed_hardware=dict(new_splice_plates=4,new_m8_bolts=16,reused_main_interface_m12_bolts=16,additional_stock_mass_kg_per_bay=plate_mass+bolt_mass,
            additional_stock_mass_kg_per_car=24*(plate_mass+bolt_mass),cut_gap_m=.010,removed_stock_mass_credit_kg=0.,
            tooling=dict(supported_lateral_lifting_fixture_capacity_assumption_kg=500.,fixture_allowance_usd=3000.,fixture_is_onboard_mass=False)),
        steps=['isolate, prove dead and independently support detachable elbow/cartridge','remove cover and disconnect all services and earth','remove four collector-splice plates and16M8 bolts','remove16M12 main interface bolts, preserving body laminate/spreader','translate supported complete elbow/cartridge90cm outboard','inspect every new splice and hardpoint; torque and calibrate; independent handback'],
        redraw_holds=['Collector splice bending/torsion/fatigue and alignment design','Socket/lateral fixture path including body environment and platforms','Retained-body global load redistribution after segmentation','Three winding circuit/core topology and actual connector/cable bend geometry'],selected=False)
    return v

def bounds(p):
    size=models.global_size(p) if p['kind']=='cylinder' else p['size_m']
    return [list(p['at_m']),[p['at_m'][i]+size[i] for i in range(3)]]

def path_check(value=None):
    v=bay_definition() if value is None else value;a=load();delta=v.get('translation_m',[0.,0.,-a['replacement_drop_m']]);moving=[*v['retained_parts'],*[p for p in v['equipment'] if p['role']=='replaceable']]
    required=a['minimum_path_clearance_m'];collisions=[];checks=0;fixed_bounds=[(p['id'],bounds(p)) for p in v['fixed_parts']]
    clearance_holds=[];release_checks=[];minimum=None
    releases={(r['moving'],r['fixed']):r for r in v.get('released_mating_interfaces',[])}
    if len(releases)!=len(v.get('released_mating_interfaces',[])):raise ValueError('duplicate mating-interface release')
    used=set()
    def separation(aa,bb):
        return math.sqrt(math.fsum(max(aa[0][i]-bb[1][i],bb[0][i]-aa[1][i],0.)**2 for i in range(3)))
    # Straight translation: endpoint separation is an exact swept AABB test;
    # samples are review output, never a claim to resolve arbitrary motion.
    swept=[]
    for p in moving:
        initial=bounds(p);aa=[[initial[0][i]+min(0.,delta[i]) for i in range(3)],[initial[1][i]+max(0.,delta[i]) for i in range(3)]]
        for fixed_id,bb in fixed_bounds:
            checks+=1
            pair=(p['id'],fixed_id);clearance=separation(aa,bb)
            if pair in releases:
                used.add(pair);record=releases[pair]
                # A disconnected mating face starts at zero gap. It may only
                # leave by its separating normal; penetration or tangential
                # extraction cannot be excused as a mating contact.
                depth=[min(initial[1][i],bb[1][i])-max(initial[0][i],bb[0][i]) for i in range(3)]
                axes=[i for i in range(3) if
                    (abs(initial[0][i]-bb[1][i])<=1e-9 and delta[i]>0) or
                    (abs(initial[1][i]-bb[0][i])<=1e-9 and delta[i]<0)]
                valid=bool(record.get('release')) and min(depth)<=1e-9 and bool(axes)
                fraction=min((required/abs(delta[i]) for i in axes),default=float('inf'))
                if fraction>1:valid=False
                if valid:
                    separated=[[initial[0][i]+delta[i]*fraction+min(0.,delta[i]*(1-fraction)) for i in range(3)],
                               [initial[1][i]+delta[i]*fraction+max(0.,delta[i]*(1-fraction)) for i in range(3)]]
                    clearance=separation(separated,bb);valid=clearance>=required-1e-9
                release_checks.append(dict(moving=p['id'],fixed=fixed_id,release=record.get('release'),
                    normal_separation_verified=valid,clearance_reached_at_path_fraction=fraction if math.isfinite(fraction) else None,
                    initial_contact_is_not_clearance=True,physical_release_executed=False))
                if not valid:clearance=0.
            minimum=clearance if minimum is None else min(minimum,clearance)
            if clearance<required-1e-9:clearance_holds.append(dict(moving=p['id'],fixed=fixed_id,clearance_m=clearance,required_m=required))
            if min(min(aa[1][i],bb[1][i])-max(aa[0][i],bb[0][i]) for i in range(3))>1e-9:
                swept.append([p['id'],fixed_id])
                for n in range(a['replacement_path_samples']):
                    pose=[[c+delta[i]*n/(a['replacement_path_samples']-1) for i,c in enumerate(q)] for q in initial]
                    depth=[min(pose[1][i],bb[1][i])-max(pose[0][i],bb[0][i]) for i in range(3)]
                    if min(depth)>1e-9 and len(collisions)<20:collisions.append(dict(step=n,moving=p['id'],fixed=fixed_id,aabb_overlap_m=depth))
    if set(releases)!=used:raise ValueError('mating-interface release does not identify a tested pair')
    return dict(translation_m=delta,sampled_poses=a['replacement_path_samples'],pair_checks=checks,
        conservative_swept_aabb_collisions=swept,sampled_collision_examples=collisions[:20],clear_under_declared_box_bounds=not swept and not clearance_holds,
        minimum_required_clearance_m=required,minimum_conservative_clearance_m=minimum,clearance_holds=clearance_holds,released_mating_interfaces=release_checks,
        motion_scope='Straight supported translation with declared minimum clearance; conservative swept AABB distances. Explicit disconnected mating faces first separate normally to the same clearance. Removed cover/connectors/retention require the declared steps. No flexible cable, lifting stability or magnetic/tool acceptance.',
        accepted=False)

def study():
    configs=[configuration_profile(i) for i in load()['profiles']];ledgers=[mass_ledger(c) for c in configs];p=products(configs[0]);bay=bay_definition();path=path_check(bay);redesign=redesigned_bay()
    support_cost=p[0]['bom'][2]['cost_usd']+p[0]['bom'][3]['cost_usd']+p[0]['bom'][4]['cost_usd']+p[0]['bom'][5]['cost_usd']
    cost=reconcile_allowance('magnetic-equipment-usd-per-car',manufacturing.load()['rates']['magnetic_equipment_per_car'],[dict(id='coils-sensors-drive-current-circuits',value=24*support_cost,state='Allocated')])
    return dict(schema=SCHEMA,revision=load()['revision'],configurations=configs,ledger=ledgers,products=p,cost_substitution=cost,
        equipped_bay=dict(definition_sha256=digest(encoded(bay)),part_count=len(bay['retained_parts'])+len(bay['equipment']),retention_count=len(bay['positive_retention']),path=path,
            redesign=dict(id=redesign['id'],definition_sha256=digest(encoded(redesign)),path=path_check(redesign),changed_hardware=redesign['changed_hardware'],holds=redesign['redraw_holds'],selected=False),
            winding_window_change='Three separately placed60mm packs are a new packaging hypothesis. Retained two100mm-wide windows are not silently treated as three134mm-wide coils.',
            missing=['Detailed lugs, qualified power connector, real coolant coupling, strain relief and cable minimum-bend tangent geometry','Measured magnetic and tool handling/lift fixture and retention load qualification']),
        affected_results_on_change=['mass and structural load profiles','support current and thermal duty','station trajectory and energy','production BOM and cost','qualification specimens and serial installation'],
        completion_scope='Controlled digital pilot product, scope-exclusive accounting and conservative packaging path evidence; complete equipped vehicle/physical release remains open',**FLAGS)

def overview(r):
    rows=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="440" viewBox="0 0 1100 440"><rect width="1100" height="440" fill="#101c2b"/><g fill="#edf4ff" font-family="sans-serif"><text x="30" y="45" font-size="25">Controlled pilot product and equipment accounting</text>']
    for j,l in enumerate(r['ledger']):rows.append(f'<text x="35" y="{95+j*55}" font-size="19">{r["configurations"][j]["id"]}: tare target {l["original_target_tare_kg"]:,.0f} kg; reconciled {l["reconciled_tare_kg"]:,.1f} kg</text>')
    rows+=['<text x="35" y="230" font-size="19">Defined body/cartridges + winding copper replace scope allowances once.</text>','<text x="35" y="270" font-size="19">Unrepresented equipment retains allocations; scope overruns remain visible.</text>',f'<text x="35" y="315" font-size="19">Bay swept-bound obstructions: {len(r["equipped_bay"]["path"]["conservative_swept_aabb_collisions"])}</text>','<text x="35" y="385" font-size="17">Unqualified packaging, cost and materials. No manufacturing or physical release.</text></g></svg>']
    return ''.join(rows)

def bay_views(value=None):
    """Code-native dimensioned orthographic bounds, independent of AI imagery."""
    from html import escape
    v=redesigned_bay() if value is None else value;moving=[*v['retained_parts'],*v['equipment']]
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="760" viewBox="0 0 1300 760"><rect width="1300" height="760" fill="#101c2b"/><g fill="#edf4ff" font-family="sans-serif"><text x="25" y="35" font-size="23">Detachable equipped bay — calculated orthographic bounds, metres</text>']
    for x0,label,axes,limits in [(35,'Front Y/Z; x≈0.5m',(1,2),(.3,2.7,-.8,.35)),(680,'Plan X/Y; complete bay envelope',(0,1),(-.15,1.15,.3,2.7))]:
        lo,hi,bottom,top=limits;scale_x=570/(hi-lo);scale_y=480/(top-bottom)
        out.append(f'<text x="{x0}" y="75" font-size="18">{label}</text><rect x="{x0}" y="90" width="570" height="480" fill="#162b3c"/>')
        def draw(p,colour,opacity,delta=None):
            bb=bounds(p)
            if axes==(1,2) and not bb[0][0]-.001<=.5<=bb[1][0]+.001:return
            if axes==(0,1) and bb[0][2]>.15:return
            if delta:bb=[[q[i]+delta[i] for i in range(3)] for q in bb]
            a,b=axes;left=x0+(bb[0][a]-lo)*scale_x;yy=90+(top-bb[1][b])*scale_y;width=(bb[1][a]-bb[0][a])*scale_x;height=(bb[1][b]-bb[0][b])*scale_y
            if left+width<x0 or left>x0+570 or yy+height<90 or yy>570:return
            right=min(left+width,x0+570);low=min(yy+height,570);left=max(x0,left);yy=max(90,yy);width=right-left;height=low-yy
            out.append(f'<rect x="{left:.3f}" y="{yy:.3f}" width="{max(.5,width):.3f}" height="{max(.5,height):.3f}" fill="{colour}" opacity="{opacity}" stroke="{colour}" stroke-width=".7"><title>{escape(p["id"])}</title></rect>')
        for p in v['fixed_parts']:draw(p,'#647787','.35')
        for p in moving:draw(p,'#35c8af','.75')
        for p in v['retained_parts']:draw(p,'#e1aa50','.25',v['translation_m'])
        out.append(f'<text x="{x0}" y="603" font-size="16">Teal installed; gold at+0.90m outboard; grey retained.</text>')
    out+=['<text x="30" y="650" font-size="17">Collector segment x0.005–0.995m;10mm joint cuts.4new200×80×8mm plates +16M8;16M12 released/reused.</text>',
        '<text x="30" y="687" font-size="17">Three174×134×60mm winding candidates; paired sensors; power/signal/cooling disconnects and earth route.</text>',
        '<text x="30" y="726" font-size="15">Conservative box-bound extraction evidence only. Magnetic circuit, splice loads, cables, tools and physical assembly remain unqualified.</text></g></svg>']
    return ''.join(out)

def animation_events(value=None):
    v=redesigned_bay() if value is None else value;n=load()['replacement_path_samples']
    return dict(schema='osr-pilot-bay-translation/1',definition_sha256=digest(encoded(v)),
        frames=[dict(frame=i,fraction=i/(n-1),translation_m=[x*i/(n-1) for x in v['translation_m']]) for i in range(n)],
        path_checks=path_check(v),physical_motion_measurements=False,scope='Calculated straight translation of declared box envelopes; illustration of retained conservative swept-bound test, not measured physical assembly',**FLAGS)

def render_bay_animation(value=None):
    from PIL import Image,ImageDraw,ImageFont
    v=redesigned_bay() if value is None else value;events=animation_events(v);frames=[]
    font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    try:font=ImageFont.truetype(font_path,18)
    except OSError:font=ImageFont.load_default()
    for event in events['frames']:
        im=Image.new('RGB',(1100,650),'#101c2b');draw=ImageDraw.Draw(im);draw.text((25,20),'Supported equipped-bay extraction — calculated front view',font=font,fill='white')
        def rectangle(p,colour,shift=None):
            bb=bounds(p)
            if not bb[0][0]-.001<=.5<=bb[1][0]+.001:return
            if shift:bb=[[q[i]+shift[i] for i in range(3)] for q in bb]
            coords=[60+(bb[0][1]-.3)*400,100+(.4-bb[1][2])*350,60+(bb[1][1]-.3)*400,100+(.4-bb[0][2])*350]
            if coords[2]<40 or coords[0]>1060 or coords[3]<80 or coords[1]>570:return
            draw.rectangle(coords,fill=colour,outline='#d5e8ed',width=1)
        for p in v['fixed_parts']:rectangle(p,'#405160')
        for p in v['retained_parts']:rectangle(p,'#238f82',event['translation_m'])
        for p in v['equipment']:
            if p['role']=='replaceable':rectangle(p,'#d99539',event['translation_m'])
        draw.text((25,555),f'Outboard travel {event["translation_m"][1]:.3f}m /0.900m; supported module; services/splices/M12 released first',font=font,fill='white')
        draw.text((25,595),'Provisional bounds/path calculation; splice strength, magnetic handling and physical acceptance remain open.',font=font,fill='#e3b66b')
        frames.append(im)
    poster=io.BytesIO();frames[0].save(poster,format='PNG')
    with tempfile.TemporaryDirectory(prefix='osr-pilot-bay-') as folder:
        folder=Path(folder)
        for j,im in enumerate(frames):im.save(folder/f'{j:03d}.png')
        run=subprocess.run(['ffmpeg','-v','error','-y','-framerate','12','-i',str(folder/'%03d.png'),'-an','-c:v','libx264','-pix_fmt','yuv420p','-crf','22',str(folder/'replacement.mp4')],capture_output=True,text=True,timeout=120)
        if run.returncode:raise ValueError('bay translation encoding failed: '+run.stderr[-1000:])
        video=(folder/'replacement.mp4').read_bytes()
    receipt=dict(schema='osr-pilot-bay-visuals/1',events_sha256=digest(encoded(events)),poster_sha256=digest(poster.getvalue()),video_sha256=digest(video),frames=len(frames),frames_per_second=12,source_geometry_sha256=events['definition_sha256'],**FLAGS)
    return {'bay-poster.png':poster.getvalue(),'bay-replacement.mp4':video,'bay-translation-events.json':encoded(events),'visual-receipt.json':encoded(receipt)}

def publish_packet(output,schema,result,source_map,extra=None):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    payload={'study.json.gz':gzip.compress(encoded(result),mtime=0),'overview.svg':overview(result).encode() if schema==SCHEMA else extra.pop('overview.svg')}
    if extra:payload.update(extra)
    for name,data in payload.items():(output/name).write_bytes(data)
    manifest=dict(schema=schema,source_sha256=source_map,files_sha256={n:digest(b) for n,b in sorted(payload.items())},**FLAGS)
    (output/'manifest.json').write_bytes(encoded(manifest));return manifest

def verify_packet(output,schema,source_map):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes())
    if m.get('schema')!=schema or m.get('source_sha256')!=source_map or any(m.get(k) is not False for k in FLAGS):raise ValueError('stale pilot packet source or release flags')
    for name,h in m['files_sha256'].items():
        if Path(name).name!=name or name.startswith('.') or (output/name).is_symlink():raise ValueError('unsafe pilot payload')
        b=(output/name).read_bytes()
        if len(b)>MAX_RAW or digest(b)!=h:raise ValueError('pilot payload checksum differs')
    with gzip.GzipFile(fileobj=io.BytesIO((output/'study.json.gz').read_bytes())) as f:b=f.read(MAX_RAW+1)
    if len(b)>MAX_RAW:raise ValueError('pilot raw budget exceeded')
    r=json.loads(b)
    if any(r.get(k) is not False for k in FLAGS):raise ValueError('pilot result release flags differ')
    return m,r

def readme(r):
    return '\n'.join(['# Controlled provisional pilot product','',f'Configurations: {len(r["configurations"])}; exact product definitions: {len(r["products"])}.','',
        'The scope ledger replaces each covered allocation with its definition and retains only the unrepresented residual. Defined mass above its allocation increases the total; the growth reserve is retained. Cost rates remain unquoted allowances.','',
        *[f'{c["id"]}: target tare {l["original_target_tare_kg"]:,.0f} kg; reconciled tare {l["reconciled_tare_kg"]:,.3f} kg, AW3 {l["reconciled_aw3_kg"]:,.3f} kg. These overruns prevent adoption of the old mass targets.' for c,l in zip(r['configurations'],r['ledger'])],'',
        'The equipped-bay geometry includes retained cartridge/positive retention, three winding-pack candidates, paired sensing, disconnect interfaces, power/signal/earth route definitions and a removable cover. Straight supported extraction uses conservative swept AABBs against the assembled body/guideway; reported obstructions are holds, never waived collisions. Cable bends, qualified fittings, tool access, magnetic handling and installed qualification remain open.','',
        f'The retained cartridge-only downward path has {len(r["equipped_bay"]["path"]["conservative_swept_aabb_collisions"])} conservative bound obstructions. The separately identified segmented-collector/detachable-elbow lateral candidate has {len(r["equipped_bay"]["redesign"]["path"]["conservative_swept_aabb_collisions"])}; it adds four splice plates and16M8 bolts per bay,106.014kg/car if adopted. Those unqualified splices are not included in the base product mass or silently selected.','',
        '[Dimensioned bay views](bay-views.svg) · [Calculated replacement animation](bay-replacement.mp4) · [Exact translation events](bay-translation-events.json). These are code-native bounds, not native-detail connector or released manufacturing drawings.','',
        'No complete equipped mass, supplier quotation, magnetic map, manufacturing or physical release is claimed.',''])

def publish(output=OUTPUT):
    src=sources();r=study();bay=bay_definition();text=readme(r)
    extra={'README.md':text.encode(),'bay-definition.json.gz':gzip.compress(encoded(bay),mtime=0),'bay-redesigned-definition.json.gz':gzip.compress(encoded(redesigned_bay()),mtime=0),'bay-views.svg':bay_views().encode(),**render_bay_animation()}
    if src!=sources():raise ValueError('pilot sources changed during publication')
    return publish_packet(output,SCHEMA,r,src,extra)

def verify(output=OUTPUT):
    m,r=verify_packet(output,SCHEMA,sources());expected=study()
    expected_files={'study.json.gz','overview.svg','README.md','bay-definition.json.gz','bay-redesigned-definition.json.gz','bay-views.svg','bay-poster.png','bay-replacement.mp4','bay-translation-events.json','visual-receipt.json'}
    if set(m['files_sha256'])!=expected_files or r!=expected or (Path(output)/'overview.svg').read_text()!=overview(expected) or (Path(output)/'README.md').read_text()!=readme(expected):raise ValueError('pilot derived ledger or presentation differs')
    with gzip.GzipFile(fileobj=io.BytesIO((Path(output)/'bay-definition.json.gz').read_bytes())) as f:b=f.read(MAX_RAW+1)
    if len(b)>MAX_RAW or json.loads(b)!=bay_definition():raise ValueError('pilot bay definition differs')
    with gzip.GzipFile(fileobj=io.BytesIO((Path(output)/'bay-redesigned-definition.json.gz').read_bytes())) as f:b=f.read(MAX_RAW+1)
    if len(b)>MAX_RAW or json.loads(b)!=redesigned_bay():raise ValueError('redesigned pilot bay definition differs')
    if (Path(output)/'bay-views.svg').read_text()!=bay_views() or json.loads((Path(output)/'bay-translation-events.json').read_bytes())!=animation_events():raise ValueError('pilot bay orthographic/translation evidence differs')
    visual=json.loads((Path(output)/'visual-receipt.json').read_bytes())
    if visual['events_sha256']!=digest(encoded(animation_events())) or visual['frames']!=41 or visual['frames_per_second']!=12 or any(visual[k]!=digest((Path(output)/name).read_bytes()) for k,name in [('poster_sha256','bay-poster.png'),('video_sha256','bay-replacement.mp4')]):raise ValueError('pilot bay visual receipt differs')
    return dict(schema='osr-pilot-product-verification/1',verified=True,configurations=len(r['configurations']),products=len(r['products']),mass_targets_closed=sum(l['target_closed'] for l in r['ledger']),**FLAGS)

def read_summary(output=OUTPUT):
    status=verify(output);r=study()
    return dict(**status,configuration_sha256=r['configurations'][0]['configuration_sha256'],profiles=r['configurations'],mass_ledger=r['ledger'],cost_substitution=r['cost_substitution'],bay=r['equipped_bay'],manifest_sha256=digest((Path(output)/'manifest.json').read_bytes()))
