"""Six-car station fit study, pier families and explicit emergency-energy hypotheses.

Native material regions are partial assemblies. No completed train, qualified
station structure, chute mechanism, actuator or installed programme price.
"""
from hashlib import sha256
from pathlib import Path
from copy import deepcopy
import gzip
import json
import math
from . import configuration,geometry,media,model,system_development,requirements,evacuation,station_structure,specification

OUTPUT=model.ROOT/'docs/design-engine/ferrite-maglev/baghdad-reference'

def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()


def station(cfg=None):
    cfg=cfg or configuration.selected();f=cfg.formation;s=cfg.station;cv=cfg.civil
    length=f.assumed_overall_length_m+2*s['end_allowance_assumption_m'];half=s['island_width_m']/2
    centre=half+f.arm_width_m/2+s['arm_clearance_assumption_m'];floor=s['floor_top_above_beam_m']
    # Split platform around an actual lift opening; the lift floor has the same
    # top z coordinate as the platform, rather than standing on its top surface.
    p=[];stages=[]
    bays=math.ceil(length/cv.span_m);bay_length=length/bays
    for side in (-1,1):
        for bay in range(bays):
            parts=geometry.beam_parts(f'guideway/{side}/bay-{bay+1}',bay_length,side*centre,
                width=cv.width_m,depth=cv.depth_m,web=cv.web_m,flange=cv.flange_m)
            for part in parts:part['at_m'][0]+=-length/2+(bay+.5)*bay_length
            p+=parts
    stages.append(dict(id='two-guidebeams-and-reaction-iron',parts=[v['id'] for v in p]))
    start=len(p)
    for side in (-1,1):
        x=-length/2 if side<0 else s['lift_length_m']/2
        p.append(geometry.part(f'platform/end-{side}',[(length-s['lift_length_m'])/2,s['island_width_m'],.08],[x,-half,floor-.08],'concrete'))
        y=-half if side<0 else s['lift_width_m']/2
        p.append(geometry.part(f'platform/lift-side-{side}',[s['lift_length_m'],(s['island_width_m']-s['lift_width_m'])/2,.08],[-s['lift_length_m']/2,y,floor-.08],'concrete'))
    stages.append(dict(id='platform-with-lift-opening',parts=[v['id'] for v in p[start:]]));start=len(p)
    p.append(geometry.part('lift/flush-floor',[s['lift_length_m'],s['lift_width_m'],.08],[-s['lift_length_m']/2,-s['lift_width_m']/2,floor-.08],'steel'))
    ground=-(cv.pier_height_m+cv.depth_m+.9)
    for x in (-s['lift_length_m']/2,s['lift_length_m']/2-.06):
        for y in (-s['lift_width_m']/2,s['lift_width_m']/2-.06):
            p.append(geometry.part(f'lift/shaft-frame-{x}-{y}',[.06,.06,floor-ground+2.2],[x,y,ground],'steel',kind='tube',wall_m=.005,axis=2))
    stages.append(dict(id='lift-frame-and-flush-floor',parts=[v['id'] for v in p[start:]]));start=len(p)
    frames=[v for v in geometry.interface()['parts'] if v['id'].startswith('frame/')]
    cars=[];doors=[]
    for index in range(f.cars):
        cx=-f.assumed_overall_length_m/2+f.body_length_m/2+index*(f.body_length_m+f.coupling_gap_assumption_m)
        cars.append(dict(car=index+1,centre_x_m=cx,body_bounds_x_m=[cx-f.body_length_m/2,cx+f.body_length_m/2]))
        for raw in frames:
            v=deepcopy(raw);v['id']=f'car-{index+1}/'+v['id'];v['at_m'][0]+=cx;v['at_m'][1]-=centre;p.append(v)
        for side in (-1,1):
            for door,x in enumerate(f.doors_per_side_x_m):doors.append(dict(car=index+1,side=side,door=door+1,x_m=cx+x,
                sill_y_m=-centre+side*f.cabin_width_m/2,normal_sill_z_m=floor,captured_sill_z_m=floor-s['capture_drop_assumption_m']))
    stages.append(dict(id='six-car-partial-floor-frames',parts=[v['id'] for v in p[start:]]))
    result=geometry.finish('OSR-V05-BAGHDAD-SIX-CAR-STATION',p,stages,
        scope='Two guidebeams, split island platform, centred lift frame and six repeated partial native floor frames. No complete cabin, magnetic cartridges, canopy, station support, stairs, charging device or qualified passenger installation.',
        holds=['Coupling/stopping/end allowances are assumptions; dynamic swept envelopes and bridge-plate accessibility open',
            'Station support, ground, connections, canopy, stairs, barriers, fire/egress and passenger capacity unqualified',
            'Charging devices and emergency chutes remain space/interface requirements, not selected hardware'])
    result.update(configuration_revision=cfg.revision,cars=cars,door_interfaces=doors,
        nominal_body_length_m=f.body_sum_m,assumed_overall_train_length_m=f.assumed_overall_length_m,
        manufactured_bays_per_direction=bays,beam_unit_length_m=bay_length,
        joints_and_bearings_qualified=False,platform_length_m=length,beam_centres_y_m=[-centre,centre],lift_centre_xy_m=[0.,0.],
        lift_threshold_step_m=0.,clear_passage_each_lift_side_m=(s['island_width_m']-s['lift_width_m'])/2,
        body_to_platform_horizontal_gap_m=centre-f.cabin_width_m/2-half,
        arm_to_platform_horizontal_clearance_m=centre-f.arm_width_m/2-half,
        captured_vertical_step_m=s['capture_drop_assumption_m'],passenger_bridge_plate_required=True,
        normal_floor_gap_accepted=False,charging_kw_per_train=cfg.operations['charger_kw_per_car']*f.cars,
        charging_equipment_selected=False,ground_level_relative_to_beam_m=ground,
        door_sill_to_ground_m=floor-ground)
    return result


def emergency_energy(stages,components):
    """Components supply power for each named phase; None keeps reserve open."""
    if not stages or not components:raise ValueError('explicit phases and consumers required')
    total=0.;missing=[];rows=[]
    for phase,duration_s in stages.items():
        model.positive(duration_s,'emergency duration',zero=True)
        for name,powers in components.items():
            power=powers.get(phase)
            if power is None:missing.append(name+'/'+phase);continue
            model.positive(power,'emergency power',zero=True)
            energy=power*duration_s/3600;total+=energy
            rows.append(dict(phase=phase,component=name,power_kw=power,duration_s=duration_s,energy_kwh=energy))
    return dict(rows=rows,known_energy_kwh=total,missing_power_terms=missing,
        calculated_total_kwh=None if missing else total,approved_reserve_kwh=None,
        scope='Assumed DC energy only; EOL, temperature, conversion, faults, redundancy and physical load measurements require acceptance',**model.FLAGS)


def study():
    cfg=configuration.selected();native=station(cfg)
    stages=dict(stop=60.,deploy=180.,evacuate=600.,rescue=1800.)
    cases=[]
    for support in (2.,5.,10.):
        components={name:{phase:power for phase in stages} for name,power in
            [('support',support*cfg.formation.cars),('controls',1.),('lights',.6),('communications',.2)]}
        components['deployment-hardware']={phase:None for phase in stages}
        cases.append(dict(assumed_support_kw_per_car=support,result=emergency_energy(stages,components)))
    families=[]
    for height in (8.,12.,20.,30.):
        d=system_development.support_demands(pier_height=height)
        families.append(dict(pier_height_m=height,door_sill_to_ground_m=height+cfg.civil.depth_m+1.2+cfg.station['floor_top_above_beam_m'],
            column_mass_kg=station_structure.civil(pier_height=height)['supports']['column_kg'],
            ground_level_assumed_m=cfg.civil.ground_level_m,demands=d,lateral_capacity=None,
            foundation_selected=False,erection_equipment_selected=False,installed_cost_usd=None))
    qty={}
    for p in native['parts']:
        if p['id'].startswith('car-'):continue
        q=qty.setdefault(p['material'],dict(volume_m3=0.,mass_kg=0.,unit_rate_usd=None,installed_rate_usd=None))
        q['volume_m3']+=p['volume_m3'];q['mass_kg']+=p['modelled_mass_kg']
    return dict(schema='osr-baghdad-reference-assembly/1',architecture='ferrite-pm-maglev-study',
        configuration_revision=cfg.revision,city='Baghdad',cars_per_train=6,publication_role='primary-provisional-design',
        financial_scope='Partial native station quantities; all rates and complete six-car/programme prices unresolved',
        selected_configuration=cfg.record(),station={k:v for k,v in native.items() if k not in {'parts','construction_stages'}},
        station_quantity_ledger=qty,station_installed_cost_usd=None,pier_height_families=families,
        emergency_stages_assumption_seconds=stages,emergency_energy_cases=cases,
        chute_net_mass_ledger=dict(devices_per_train=cfg.formation.devices,
            partial_entry_hardware_gross_kg=system_development.entry_geometry()['modelled_material_mass_kg']*cfg.formation.devices,
            overlapping_body_mass_to_remove_kg=None,fabric_and_deployment_mass_to_add_kg=None,
            net_train_addition_kg=None,cg_m=None,travel_stowage_qualified=False),
        open_design_tasks=['Complete stowed/deployed chute mechanism and measured net mass',
            'Supplier-grade representative electromagnetic module with converged force/loss maps and rig tests',
            'Six-car priced repeated/shared equipment MBOM and complete Baghdad programme scope',
            'Located corridor alignment, terminal closure, landing surveys, recovery and utility designs'],**model.FLAGS)


def sources():
    paths=[*station_structure.source_paths(),Path(specification.__file__),specification.INPUT,model.ROOT/'OpenSourceRail_Station_Powered_Maglev_Design_Specification.docx',Path(requirements.__file__),Path(evacuation.__file__),evacuation.INPUT,model.SPEC,Path(__file__),*configuration.source_paths(),Path(geometry.__file__),Path(media.__file__),
        Path(model.__file__),Path(system_development.__file__),system_development.INPUT,
        model.ROOT/'engineering/factory_examples/native.py',model.ROOT/'engineering/factory_examples/models.py']
    return {p.relative_to(model.ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in paths}


def publish(output=OUTPUT):
    from engineering.factory_examples.native import generate
    output=Path(output);output.mkdir(parents=True,exist_ok=True);before=sources()
    definition=station();folder=output/'station';folder.mkdir(exist_ok=True)
    (folder/'definition.json').write_bytes(encoded(definition));receipt=generate(folder/'definition.json',folder,model.ROOT)
    step=folder/'model.step';raw=step.read_bytes();(folder/'model.step.gz').write_bytes(gzip.compress(raw,mtime=0));step.unlink()
    receipt['files_sha256'].pop('model.step');receipt['files_sha256']['model.step.gz']=sha256((folder/'model.step.gz').read_bytes()).hexdigest()
    receipt['step_uncompressed_sha256']=sha256(raw).hexdigest();(folder/'native-cad.json').write_bytes(encoded(receipt));media.native_views(folder)
    (output/'README.md').write_text(readme())
    (output/'study.json').write_bytes(encoded(study()))
    (output/'configuration.json').write_bytes(encoded(configuration.selected().record()))
    (output/'requirements.json').write_bytes(encoded(requirements.register()))
    if before!=sources():raise ValueError('reference assembly inputs changed during native export')
    manifest=dict(schema='osr-baghdad-reference-packet/1',source_sha256=before,
        files_sha256={p.relative_to(output).as_posix():sha256(p.read_bytes()).hexdigest() for p in output.rglob('*') if p.is_file() and p.name!='manifest.json'},**model.FLAGS)
    (output/'manifest.json').write_bytes(encoded(manifest));return verify(output)


def verify(output=OUTPUT):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes())
    expected={'README.md','study.json','configuration.json','requirements.json'}|{'station/'+p for p in (
        'definition.json','model.FCStd','model.step.gz','native-cad.json','native-mesh.json.gz','overview.png','assembly-visibility.mp4','visual-receipt.json')}
    actual={p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}
    if m['schema']!='osr-baghdad-reference-packet/1' or m['source_sha256']!=sources():raise ValueError('reference assembly source/identity differs')
    if actual!=expected|{'manifest.json'} or set(m['files_sha256'])!=expected:raise ValueError('reference assembly inventory differs')
    if any(m.get(k) is not False for k in model.FLAGS):raise ValueError('reference assembly release asserted')
    for name,digest in m['files_sha256'].items():
        p=output/name
        if p.is_symlink() or sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('reference assembly payload differs')
    if json.loads((output/'station/definition.json').read_bytes())!=station():raise ValueError('reference assembly definition differs')
    if json.loads((output/'study.json').read_bytes())!=json.loads(encoded(study())):raise ValueError('reference assembly study differs')
    if json.loads((output/'configuration.json').read_bytes())!=json.loads(encoded(configuration.selected().record())) or json.loads((output/'requirements.json').read_bytes())!=json.loads(encoded(requirements.register())):raise ValueError('reference configuration/requirements differs')
    receipt=json.loads((output/'station/native-cad.json').read_bytes())
    if not receipt['fcstd_reopened'] or not receipt['step_reopened'] or receipt['input_sha256']!=m['files_sha256']['station/definition.json']:raise ValueError('reference native receipt differs')
    if receipt['part_count']!=len(station()['parts']):raise ValueError('reference native part count differs')
    visual=json.loads((output/'station/visual-receipt.json').read_bytes())
    if visual['renderer_sha256']!=sha256(Path(media.__file__).read_bytes()).hexdigest():raise ValueError('reference renderer changed')
    for record in (receipt,visual):
        if record.get('physical_release') is not False:raise ValueError('reference nested release asserted')
        for name,digest in record['files_sha256'].items():
            if Path(name).name!=name or m['files_sha256'].get('station/'+name)!=digest:raise ValueError('reference nested receipt differs')
    if visual['mesh_sha256']!=m['files_sha256']['station/native-mesh.json.gz']:raise ValueError('reference visual mesh differs')
    return m


def readme():
    return """# Baghdad six-car native reference study

Generated by `engineering.ferrite_maglev.reference_assembly`.
Architecture: ferrite PM maglev. Configuration: V05-BAGHDAD-SIX-CAR-2.
Role: current provisional primary design. Financial scope: partial station
quantities; complete train and installed programme remain unpriced.

[Study and quantity ledger](study.json) · [Selected configuration](configuration.json) ·
[79 requirements and conditional applicability](requirements.json) · [Manifest](manifest.json)

![Native six-car partial floor frames and station](station/overview.png)

[FreeCAD](station/model.FCStd) · [Compressed STEP](station/model.step.gz) ·
[Native reopen receipt](station/native-cad.json) ·
[Assembly visibility video](station/assembly-visibility.mp4)

Six 17 m bodies total 102 m. Assumed inter-car gaps give 104.5 m overall;
assumed end allowances give a 109.5 m platform. Coupling and stopping values
remain provisional. The centred lift floor is flush with the platform.
The 2.96 m arm envelope leaves a 0.255 m cabin-to-platform gap requiring
qualified bridge plates. Partial frames exclude the finished body and devices.

Pier heights 8/12/20/30 m propagate mass, gravity demand and geometric slenderness.
Wind, seismic, buckling, foundations, settlement and erection acceptance are open.
Emergency-energy phase accounting keeps missing deployment power and reserve open.
Gross partial entry-hardware mass is not the net installed chute mass.

Videos show part visibility at final positions; no motion or collision simulation.
Design completion, physical validation, manufacturing and physical release: false.
"""
