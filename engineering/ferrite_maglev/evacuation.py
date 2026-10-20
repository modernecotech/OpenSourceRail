"""Conditional no-walkway guidebeam and onboard-evacuation research.

Geometric envelopes and ideal queue calculations cannot validate a chute or slide,
a pedestrian evacuation, wheelchair access, safe landing or railway acceptance.
No commands to real doors, restraints, support or inflation equipment are issued.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import itertools
import json
import math
import tomllib

from . import model,geometry

INPUT=Path(__file__).with_suffix('.toml')
SOURCES=[
 dict(url='https://www.transit.dot.gov/sites/fta.dot.gov/files/docs/repg_rts.pdf',date='1991',
      scope='Historical rail emergency guidance: move to station or rescue transfer where appropriate; no present-day rail approval established'),
 dict(url='https://www.nfpa.org/codes-and-standards/nfpa-130-standard-development/130?tab=2',date='2026 edition listed',
      scope='Rail-specific fire/life-safety standard exists. Full current clauses and applicable Iraqi/operator acceptance basis not assessed by this study'),
 dict(url='https://www.faa.gov/sites/faa.gov/files/2022-11/TSO-C69c.pdf',date='archived aviation document',
      scope='Aviation evacuation equipment reference only; no assumption of current product status or railway approval'),
 dict(url='https://www.easa.europa.eu/sites/default/files/dfu/cata_cwi_tcca-006_evacuation_slide_system_installed_in_non-pressurized_compartment.pdf',date='2020',
      scope='Aviation authorities discuss combined environment/wind deployment evidence. Aircraft requirements and test times do not establish railway acceptance'),
]
REQUIRED=(
 'door-height-roll-capture-and-landing-survey',
 'safe-landing-every-stop-position-or-approved-alternative',
 'road-traffic-roof-water-utility-and-adjacent-train-exclusion',
 'fire-smoke-tenability-and-available-exits',
 'independent-support-immobilisation-and-door-safety',
 'wind-heat-dust-puncture-ageing-and-inflation-reliability',
 'wheelchair-reduced-mobility-child-and-assisted-alternative',
 'crew-rescue-access-communications-and-evacuation-flow',
 'module-mass-volume-mount-loads-gas-isolation-and-battery-fault',
 'supplier-process-inspection-repack-replacement-and-cost',
 'chute-descent-control-blockage-recovery-and-entry-exit-queues',
 'chute-variable-height-ground-stabilisation-and-door-body-anchor-loads',
 'independent-full-scale-tests-and-authority-acceptance',
)


def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!={'version':1,'family':'ferrite-pm-maglev-study'}:raise ValueError('explicit evacuation study schema required')
    if any(v is not False for v in a['acceptance'].values()):raise ValueError('no physical evacuation evidence adapter supplied')
    ar=a['architecture']
    if any(ar.get(k) is not False for k in ('walkway_removal_approved','slide_is_universal_sole_means','chute_is_universal_sole_means','concrete_alone_supports_current_attraction_maglev')):
        raise ValueError('unqualified walkway deletion or concrete-only magnetic support claim')
    if ar['necessary_reaction_faces_supports_foundations_and_connections_retained'] is not True:
        raise ValueError('necessary magnetic/structural interfaces cannot be erased')
    if any(a[g].get(k) is not False for g,k in [('geometry','height_and_landing_surveyed'),('train','door_configuration_approved'),('flow','flow_is_measured'),('flow','mobility_assistance_demonstrated')]):
        raise ValueError('unqualified geometry/device/flow evidence')
    for group,key in [('chute','door_sill_height_screens_m'),('geometry','door_sill_height_screens_m'),('geometry','slide_slope_screens_degrees'),
                      ('train','installed_slide_pack_mass_screens_kg'),('flow','assumed_flow_screens_persons_per_second_per_exit')]:
        values=a[group][key]
        if not isinstance(values,list) or not 1<=len(values)<=12:raise ValueError('bounded nonempty sensitivity list required')
        for value in values:model.positive(value,key)
    for angle in a['geometry']['slide_slope_screens_degrees']:
        if not 10<=angle<=60:raise ValueError('bounded illustrative slope required; not a device operating limit')
    for key in ('landing_clearance_screen_m','slide_width_screen_m','lateral_clearance_each_side_screen_m'):model.positive(a['geometry'][key],key)
    for key in ('cars_screen','doors_per_side_per_car_screen','sides','aw3_passengers_screen'):
        if type(a['train'][key]) is not int or a['train'][key]<=0:raise ValueError('positive integer train scenario required')
    if a['train']['sides']!=2:raise ValueError('two-side installation hypothesis required')
    model.positive(a['flow']['deployment_delay_screen_seconds'],'deployment delay',zero=True)
    for key in ('outer_diameter_screen_m','door_standoff_screen_m','assumed_lateral_sway_screen_m','landing_clearance_screen_m','published_building_flow_claim_persons_per_minute'):
        model.positive(a['chute'][key],key)
    if any(a['chute'][key] is not False for key in ('railway_device_selected','wind_response_validated','accessible_evacuation_demonstrated')):
        raise ValueError('unqualified chute evidence')
    return a


def chute_geometry(height_m,*,diameter_m=1.2,standoff_m=1.,assumed_sway_m=.5,landing_clearance_m=3.):
    """Vertical swept clearance hypothesis; no wind-to-sway or descent dynamics."""
    for name,value in [('height',height_m),('diameter',diameter_m)]:model.positive(value,name)
    for name,value in [('stand-off',standoff_m),('assumed sway',assumed_sway_m),('landing clearance',landing_clearance_m)]:model.positive(value,name,zero=True)
    width=diameter_m+2*assumed_sway_m
    return dict(height_m=height_m,outer_diameter_m=diameter_m,door_standoff_m=standoff_m,assumed_lateral_sway_m=assumed_sway_m,
        total_clear_run_with_landing_m=standoff_m+width/2+landing_clearance_m,
        clear_width_with_margins_m=width,landing_area_rectangle_m2=(standoff_m+width/2+landing_clearance_m)*width,
        basis='Hypothetical vertical cylinder swept by assumed lateral displacement plus landing clearance; not a supplier dimension or wind model',
        descent_time_s=None,descent_speed_m_s=None,minimum_operating_height_m=None,maximum_operating_height_m=None,
        bottom_stabilisation='unselected: dry-ground anchorage/tensioning, variable length and outlet require independent design',
        supplier_device_selected=False,physical_validation=False)


def chute_guideway_path(*,towards_adjacent,door_sill_height_m=20.,diameter_m=1.2,standoff_m=1.,assumed_sway_m=.5):
    """Swept vertical chute AABB at one illustrative midspan door station."""
    e=chute_geometry(door_sill_height_m,diameter_m=diameter_m,standoff_m=standoff_m,assumed_sway_m=assumed_sway_m)
    direction=1 if towards_adjacent else -1;cy=-1.9+direction*(2.65/2+standoff_m);radius=diameter_m/2+assumed_sway_m
    low=[-radius,cy-radius,.3-door_sill_height_m];high=[radius,cy+radius,.3]
    hits=[p['id'] for p in beam_only_geometry()['parts'] if all(low[i]<=p['at_m'][i]+p['size_m'][i] and high[i]>=p['at_m'][i] for i in range(3))]
    state=assess_landing(e,surface='controlled-safe-dry-ground',clear_run_m=10,clear_width_m=5,usable_exits=1,obstruction_part_ids=hits)
    return dict(towards_adjacent=towards_adjacent,envelope=e,swept_bounds_m=[low,high],intersected_box_part_ids=hits,
        path_clear_of_modelled_structure=not hits,assessment=state,
        scope='Single hypothetical midspan door station against retained material boxes; door entry bridge, sag, all stop positions and actual route obstacles remain unsolved',**model.FLAGS)


def slide_geometry(height_m,angle_degrees,*,landing_clearance_m=3.,width_m=1.5,side_clearance_m=.5):
    for name,value in [('height',height_m),('angle',angle_degrees),('width',width_m)]:model.positive(value,name)
    for name,value in [('landing clearance',landing_clearance_m),('side clearance',side_clearance_m)]:model.positive(value,name,zero=True)
    if not 0<angle_degrees<90:raise ValueError('inclined geometric envelope requires angle in(0,90)')
    theta=math.radians(angle_degrees);run=height_m/math.tan(theta)
    return dict(height_m=height_m,angle_degrees=angle_degrees,straight_slide_length_m=height_m/math.sin(theta),
        horizontal_run_m=run,total_clear_run_with_landing_m=run+landing_clearance_m,
        clear_width_with_margins_m=width_m+2*side_clearance_m,
        landing_area_rectangle_m2=(run+landing_clearance_m)*(width_m+2*side_clearance_m),
        basis='Rigid straight-line envelope only; actual inflation sag, attachments, loading, bounce/runout and wind need supplier/test data',
        supplier_device_selected=False,physical_validation=False)


def assess_landing(envelope,*,surface,clear_run_m,clear_width_m,usable_exits,obstruction_part_ids=()):
    for key,value in [('clear run',clear_run_m),('clear width',clear_width_m)]:model.positive(value,key,zero=True)
    if type(usable_exits) is not int or usable_exits<0:raise ValueError('nonnegative exit count required')
    failures=[]
    if obstruction_part_ids:failures.append('modelled structure intersects the evacuation envelope: '+', '.join(obstruction_part_ids))
    if surface!='controlled-safe-dry-ground':failures.append('landing is not a controlled safe ground area: '+str(surface))
    if clear_run_m<envelope['total_clear_run_with_landing_m']:failures.append('insufficient deployment/landing run')
    if clear_width_m<envelope['clear_width_with_margins_m']:failures.append('insufficient lateral landing clearance')
    if not usable_exits:failures.append('no usable exit/landing path')
    return dict(state='rejected' if failures else 'hold',known_failures=failures,
        geometry_screen_pass=not failures,closure=[dict(id=k,state='unknown',accepted=False) for k in REQUIRED],
        safe_to_deploy=False,walkway_removal_approved=False,accepted=False,**model.FLAGS)


def flow_lower_bound(passengers,usable_exits,flow_persons_per_second,delay_seconds):
    if type(passengers) is not int or passengers<=0 or type(usable_exits) is not int or usable_exits<0:raise ValueError('valid passenger/exit counts required')
    model.positive(flow_persons_per_second,'assumed flow');model.positive(delay_seconds,'delay',zero=True)
    return dict(passengers=passengers,usable_exits=usable_exits,assumed_flow_persons_per_second_per_exit=flow_persons_per_second,
        optimistic_flow_time_lower_bound_s=delay_seconds+passengers/(usable_exits*flow_persons_per_second) if usable_exits else None,
        state='hold' if usable_exits else 'rejected',pedestrian_simulation_performed=False,validated_evacuation_time_s=None,
        limits='Assumes immediate equal passenger distribution and independent safe landings. Cabin queues, assistance, descent, crowd interactions, fire tenability and rescue access are not solved.',**model.FLAGS)


def adjacent_guideway_path(*,towards_adjacent,door_sill_height_m=8.,angle_degrees=30.):
    """Straight slide centreline against exact box regions of the retained bay.

    Known material intersections reject a path. Clearance of this line does not
    validate a full inflated envelope, crowd, deflection, wind or safe landing.
    """
    envelope=slide_geometry(door_sill_height_m,angle_degrees)
    # Left-hand running beam at y=-1.9m; provisional 2.65m cabin/floor at z=.3m.
    direction=1 if towards_adjacent else -1
    start=[0.,-1.9+direction*2.65/2,.3]
    end=[0.,start[1]+direction*envelope['horizontal_run_m'],.3-door_sill_height_m]
    hits=[]
    for part in beam_only_geometry()['parts']:
        lower,upper=0.,1.
        for axis in range(3):
            delta=end[axis]-start[axis];lo=part['at_m'][axis];hi=lo+part['size_m'][axis]
            if abs(delta)<1e-12:
                if start[axis]<lo or start[axis]>hi:upper=-1;break
            else:
                near,far=sorted(((lo-start[axis])/delta,(hi-start[axis])/delta))
                lower=max(lower,near);upper=min(upper,far)
        if lower<=upper and upper>=0 and lower<=1:hits.append(part['id'])
    state=assess_landing(envelope,surface='controlled-safe-dry-ground',clear_run_m=30,clear_width_m=4,
                         usable_exits=1,obstruction_part_ids=hits)
    return dict(towards_adjacent=towards_adjacent,start_m=start,end_m=end,intersected_box_part_ids=hits,
        path_clear_of_modelled_structure=not hits,assessment=state,
        scope='Provisional straight centreline/box-region intersection only; full inflated volume, wind, attachment and route environment unverified',**model.FLAGS)


def beam_only_geometry():
    source=geometry.civil_bay();removed=[p for p in source['parts'] if p['id'].startswith('walkway-')]
    parts=[deepcopy(p) for p in source['parts'] if not p['id'].startswith('walkway-')]
    ids={p['id'] for p in parts};stages=[dict(id=s['id'],parts=[key for key in s['parts'] if key in ids]) for s in source['construction_stages'] if any(key in ids for key in s['parts'])]
    result=geometry.finish('OSR-V05-CIVIL-BEAM-ONLY',parts,stages,
        scope='One integrated guidebeam per direction without continuous walkway; necessary iron faces and unreduced support/foundation envelopes retained',
        holds=['Alternative evacuation is unproved; no walkway removal release',
          'Concrete is the structural carrier, not a substitute for ferromagnetic reaction faces',
          'Passenger egress, responder access, maintenance access and safe landing at every stop position',
          'Ground/settlement, reinforcement/prestress, bearings/joints, reaction-face mounts and local magnetic loads',
          'Wind/seismic/torsion, lifting, temporary stability and construction-stage strength',
          'Support/cap geometry and interfaces require redesign; no credit for shrinking foundations or caps'])
    result['removed_reference_part_ids']=[p['id'] for p in removed]
    result['removed_modelled_walkway_mass_kg']=sum(p['modelled_mass_kg'] for p in removed)
    result['evacuation_release']=False
    result['foundation_selected']=False;result['construction_stage_strength_verified']=False
    return result


def study():
    a=load();g=a['geometry'];t=a['train'];f=a['flow']
    envelopes=[slide_geometry(h,angle,landing_clearance_m=g['landing_clearance_screen_m'],width_m=g['slide_width_screen_m'],side_clearance_m=g['lateral_clearance_each_side_screen_m'])
               for h,angle in itertools.product(g['door_sill_height_screens_m'],g['slide_slope_screens_degrees'])]
    example=slide_geometry(8,30)
    one_side=t['cars_screen']*t['doors_per_side_per_car_screen'];packs=one_side*t['sides']
    cases=[dict(surface=surface,**assess_landing(example,surface=surface,clear_run_m=30,clear_width_m=4,usable_exits=one_side))
           for surface in ('controlled-safe-dry-ground','live-road','roof','water','obstructed-land')]
    cases.append(dict(surface='narrow-street',**assess_landing(example,surface='controlled-safe-dry-ground',clear_run_m=5,clear_width_m=4,usable_exits=one_side)))
    flows=[flow_lower_bound(t['aw3_passengers_screen'],exits,rate,f['deployment_delay_screen_seconds'])
           for exits,rate in itertools.product((0,1,max(1,one_side//2),one_side),f['assumed_flow_screens_persons_per_second_per_exit'])]
    c=a['chute']
    chutes=[chute_geometry(h,diameter_m=c['outer_diameter_screen_m'],standoff_m=c['door_standoff_screen_m'],assumed_sway_m=c['assumed_lateral_sway_screen_m'],landing_clearance_m=c['landing_clearance_screen_m']) for h in c['door_sill_height_screens_m']]
    chute_cases=[dict(surface=surface,**assess_landing(chutes[0],surface=surface,clear_run_m=10,clear_width_m=5,usable_exits=one_side)) for surface in ('controlled-safe-dry-ground','live-road','roof','water','obstructed-land')]
    claim_bounds=[dict(basis='Unverified supplier building-product throughput claim, not measured rail flow',claim_url=c['flow_claim_url'],**flow_lower_bound(t['aw3_passengers_screen'],exits,c['published_building_flow_claim_persons_per_minute']/60,f['deployment_delay_screen_seconds'])) for exits in (0,1,max(1,one_side//2),one_side)]
    definition=beam_only_geometry()
    return dict(schema='osr-beam-only-evacuation-study/1',architecture=a['architecture'],assumptions=a,
        source_sha256={p.relative_to(model.ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),INPUT,Path(geometry.__file__),Path(model.__file__))},
        preferred_candidate='vertical-controlled-descent-chute; spiral or cell variants require supplier selection',
        chute_envelopes=chutes,chute_landing_cases=chute_cases,chute_building_claim_flow_bounds=claim_bounds,
        chute_guideway_paths=[chute_guideway_path(towards_adjacent=side) for side in (False,True)],
        chute_outward_extended_standoff_path=chute_guideway_path(towards_adjacent=False,standoff_m=2.),
        chute_operating_height_approved_m=None,chute_descent_simulation_performed=False,
        chute_supplier_comparison=[
            dict(name='Axel Thoms',mechanism='vertical internal spiral; controlled descent',application='site-specific building/industrial escape',
                 url='https://escape-chute.net/en/stationary-escape-chute/',origin_url='https://escape-chute.net/en/',
                 uk_supply_url=c['flow_claim_url'],manufacturing_country='Germany',uk_manufacture_confirmed=False,
                 height_claim_m=[4,120],height_claim_source=c['flow_claim_url'],railway_accepted=False),
            dict(name='Survitec MarinArk 2',mechanism='enclosed helical slide path',application='marine evacuation to liferafts',
                 url='https://survitecgroup.com/marine-evacuation-systems/marin-ark-2',
                 manufacturing_country=None,uk_manufacture_confirmed=False,railway_accepted=False,
                 limitation='Marine bowsing/liferaft interface requires a different dry-ground rail design; no rail throughput or height imported'),
            dict(name='VIKING Basic EVAC',mechanism='cell chute with speed-restricting slide elements',application='fixed offshore evacuation to sea level',
                 url='https://www.viking-life.com/products/evacuation-systems/offshore-evacuation-systems/chute-systems/viking-basic-evac-evacuation-system/',
                 manufacturing_country=None,uk_manufacture_confirmed=False,published_max_installation_height_m=35,railway_accepted=False,
                 limitation='Offshore stabilisation/outlet does not establish dry-ground train suitability')],
        geometry_envelopes=envelopes,illustrative_8m_30degree_envelope=example,landing_cases=cases,optimistic_flow_bounds=flows,
        adjacent_guideway_paths=[adjacent_guideway_path(towards_adjacent=side) for side in (False,True)],
        installed_door_pack_count_hypothesis=packs,actual_door_configuration=None,
        added_mass_sensitivities=[dict(assumed_pack_kg=m,added_kg_per_car=m*t['doors_per_side_per_car_screen']*t['sides'],added_kg_per_train=m*packs,physical_validation=False) for m in t['installed_slide_pack_mass_screens_kg']],
        selected_added_mass_kg=None,procurement_and_lifetime_cost_usd=None,net_system_saving_usd=None,
        beam_only_part_count=len(definition['parts']),removed_reference_walkway_parts=len(definition['removed_reference_part_ids']),
        removed_modelled_walkway_kg_per_25m_bay=definition['removed_modelled_walkway_mass_kg'],
        mandatory_evidence=[dict(id=k,state='unknown',accepted=False) for k in REQUIRED],
        supplier_lead=dict(name='Survitec',product_family='Marine evacuation slides/chutes; analogy and supplier investigation only',
          product_url='https://survitecgroup.com/Marine-Evacuation-Systems/SurvitecZodiac-Evacuation-Slide-System-ESS',
          uk_service_evidence='https://www.gov.uk/service-life-saving-maritime-appliances/survitec-services-uk-birkenhead',
          exact_model_uk_manufacture_confirmed=False,rail_height_wind_accessibility_fit_accepted=False,quote_received=False,
          limits='Published ESS is for low-freeboard vessels. UK service listing does not prove UK manufacture of the proposed device or railway suitability.'),
        default_action='Non-fire breakdown: retain passengers in tenable secured train and recover to station/qualified rescue transfer. Fire/emergency alternatives need independent route-specific design.',
        walkway_removal_approved=False,operational_deployment_authorised=False,**model.FLAGS,references=SOURCES)


def envelope_svg(result):
    e=result['illustrative_8m_30degree_envelope'];c=result['chute_envelopes'][0]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="580" viewBox="0 0 1000 580" role="img" aria-label="Inclined slide compared with hypothetical vertical spiral chute">
<rect width="1000" height="580" fill="#f1f5f9"/><g font-family="sans-serif" fill="#172c42">
<text x="25" y="32" font-size="23">Beam-only evacuation research: spiral chute versus inclined slide</text>
<text x="25" y="65" font-size="16">8 m door-height example. Preferred research: enclosed, controlled vertical descent.</text>
<path d="M65 130 V410 H575 M635 130 V410 H940" fill="none" stroke="#526879" stroke-width="3"/>
<path d="M65 130 L550 410" stroke="#df8053" stroke-width="10"/>
<text x="60" y="108" font-size="19">Inclined slide comparator</text>
<text x="60" y="440" font-size="16">16 m slide; 13.86 m horizontal reach</text>
<text x="60" y="465" font-size="16">+ 3 m illustrative landing clearance</text>
<rect x="670" y="130" width="42" height="280" rx="15" fill="#b5dbd4" stroke="#087f78" stroke-width="3"/>
<path d="M680 140 Q716 158 680 176 Q716 194 680 212 Q716 230 680 248 Q716 266 680 284 Q716 302 680 320 Q716 338 680 356 Q716 374 680 392" fill="none" stroke="#087f78" stroke-width="3"/>
<text x="635" y="108" font-size="19">Vertical spiral concept</text>
<text x="635" y="440" font-size="16">Assumed diameter {c['outer_diameter_m']:.1f} m; sway ±{c['assumed_lateral_sway_m']:.1f} m</text>
<text x="635" y="465" font-size="16">Stand-off + envelope + landing: {c['total_clear_run_with_landing_m']:.1f} m</text>
<text x="25" y="510" font-size="16">Chute dimensions and sway are hypotheses. Diagram does not simulate descent, wind or accessibility.</text>
<text x="25" y="540" font-size="16">Both require safe landing, secure anchorage and validated passenger flow. No walkway removal approved.</text>
</g></svg>'''.encode()


def native_sources():
    from . import media
    paths=[Path(__file__),INPUT,Path(geometry.__file__),Path(media.__file__),
           model.ROOT/'engineering/factory_examples/native.py',model.ROOT/'engineering/factory_examples/models.py']
    return {p.relative_to(model.ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in paths}


def seal_native(output):
    output=Path(output)
    names={'definition.json','model.FCStd','model.step.gz','native-cad.json','native-mesh.json.gz',
           'overview.png','assembly-visibility.mp4','visual-receipt.json'}
    manifest=dict(schema='osr-beam-only-native/1',source_sha256=native_sources(),
        files_sha256={name:sha256((output/name).read_bytes()).hexdigest() for name in sorted(names)},
        evacuation_accepted=False,walkway_removal_approved=False,**model.FLAGS)
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    return verify_native(output)


def verify_native(output):
    output=Path(output);m=json.loads((output/'manifest.json').read_text())
    names={'definition.json','model.FCStd','model.step.gz','native-cad.json','native-mesh.json.gz',
           'overview.png','assembly-visibility.mp4','visual-receipt.json'}
    if m['schema']!='osr-beam-only-native/1' or m['source_sha256']!=native_sources():raise ValueError('beam-only native source/identity differs')
    if set(m['files_sha256'])!=names or {p.name for p in output.iterdir()}!=names|{'manifest.json'}:raise ValueError('exact beam-only native inventory required')
    if any(m.get(k) is not False for k in (*model.FLAGS,'evacuation_accepted','walkway_removal_approved')):raise ValueError('unqualified beam-only release claim')
    for name,digest in m['files_sha256'].items():
        p=output/name
        if p.is_symlink() or sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('beam-only native file differs: '+name)
    if json.loads((output/'definition.json').read_text())!=beam_only_geometry():raise ValueError('beam-only native definition differs')
    r=json.loads((output/'native-cad.json').read_text())
    if not r['fcstd_reopened'] or not r['step_reopened'] or r['part_count']!=len(beam_only_geometry()['parts']):raise ValueError('beam-only native reopening/part evidence differs')
    if r['input_sha256']!=sha256((output/'definition.json').read_bytes()).hexdigest():raise ValueError('beam-only native input differs')
    visual=json.loads((output/'visual-receipt.json').read_text())
    for rec in (r,visual):
        if rec.get('physical_release') is not False:raise ValueError('native evidence asserted physical release')
        for name,digest in rec['files_sha256'].items():
            if name!=Path(name).name or sha256((output/name).read_bytes()).hexdigest()!=digest:raise ValueError('beam-only native evidence checksum differs')
    if visual['mesh_sha256']!=sha256((output/'native-mesh.json.gz').read_bytes()).hexdigest():raise ValueError('beam-only visual mesh differs')
    return m


def publish_native(output):
    import gzip
    import os
    import tempfile
    from engineering.factory_examples.native import generate
    from . import media
    output=Path(output);before=native_sources()
    if output.exists() and any(output.iterdir()):
        owned=json.loads((output/'manifest.json').read_text())
        if owned.get('schema')!='osr-beam-only-native/1':raise ValueError('destination is not an owned beam-only packet')
        expected=set(owned['files_sha256'])|{'manifest.json'}
        if {p.name for p in output.iterdir()}!=expected:raise ValueError('unexpected file in beam-only packet')
    work=model.ROOT/'build';work.mkdir(parents=True,exist_ok=True)
    # Export to a fresh directory so FreeCAD cannot create undeclared backups.
    with tempfile.TemporaryDirectory(prefix='beam-only-native-',dir=work) as temporary:
        target=Path(temporary);path=target/'definition.json'
        path.write_text(json.dumps(beam_only_geometry(),indent=2,sort_keys=True)+'\n')
        receipt=generate(path,target,model.ROOT)
        step=target/'model.step';data=step.read_bytes();zipped=target/'model.step.gz';zipped.write_bytes(gzip.compress(data,mtime=0))
        receipt['files_sha256'].pop('model.step');receipt['files_sha256']['model.step.gz']=sha256(zipped.read_bytes()).hexdigest()
        receipt['step_uncompressed_sha256']=sha256(data).hexdigest();step.unlink()
        (target/'native-cad.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        media.native_views(target)
        if before!=native_sources():raise ValueError('beam-only native sources changed during export')
        manifest=seal_native(target);output.mkdir(parents=True,exist_ok=True)
        for name in [*manifest['files_sha256'],'manifest.json']:os.replace(target/name,output/name)
    return verify_native(output)
