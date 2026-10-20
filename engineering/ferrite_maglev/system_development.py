"""Linked doorway CAD, civil load-path variants and actual offline Rust sequencing.

Complete chute/vehicle loads, capacity, ground, deployment motion and passenger
behaviour are not established. Every result is a provisional research object.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import csv
import gzip
import io
import itertools
import json
import math
import os
import subprocess
import tempfile
import tomllib

from . import model, geometry, evacuation, media, coupled

INPUT=Path(__file__).with_suffix('.toml')
OUTPUT=model.ROOT/'docs/design-engine/ferrite-maglev/system-development'


def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!={'version':1,'family':'ferrite-pm-maglev-study'}:raise ValueError('explicit system study required')
    if not a['acceptance'] or any(v is not False for v in a['acceptance'].values()):raise ValueError('no system physical acceptance adapter supplied')
    for name,value in a['mechanical'].items():model.positive(value,name)
    m=a['mechanical']
    if m['frame_wall_m']>=m['frame_section_m']/2:raise ValueError('frame tube wall consumes bore')
    if m['cassette_panel_m']>=min(m['cassette_depth_m'],m['cassette_height_m'])/2:raise ValueError('cassette panel consumes interior')
    if m['entry_outlet_standoff_m']<=m['entry_opening_m']/2+.1:raise ValueError('insufficient entry approach before outlet opening')
    for name in ('column_scales','cap_scales','foundation_scales','additional_equipment_mass_screens_kg_per_car'):
        values=a['civil'][name]
        if not isinstance(values,list) or not 1<=len(values)<=6:raise ValueError('bounded civil variants required')
        for value in values:
            model.positive(value,name,zero=name.startswith('additional'))
            if name.endswith('scales') and not .5<=value<=1:raise ValueError('bounded geometric reduction hypothesis required')
            if name=='cap_scales' and value*7<4.6:raise ValueError('cap does not span both reference beam seat footprints')
    model.positive(a['civil']['passenger_payload_kg_per_car'],'payload')
    return a


def entry_geometry(standoff_m=None):
    m=load()['mechanical'];part=geometry.part;s=m['frame_section_m'];wall=m['frame_wall_m']
    width=m['door_clear_width_m']+2*s;height=m['door_clear_height_m'];parts=[]
    for side in (-1,1):
        x=-width/2 if side<0 else width/2-s
        parts.append(part(f'entry/jamb-{side}',[s,s,height],[x,-s/2,0],'steel',kind='tube',axis=2,wall_m=wall,role='frame-member'))
        for z in (.3,1.6):
            parts.append(part(f'entry/anchor-{side}-{z}',[.12,.012,.2],[side*(width/2-s/2)-.06,-s/2-.012,z],'steel',role='mount-plate',
                holes=[dict(axis='y',x_m=.06,z_m=zz,diameter_m=.012) for zz in (.04,.16)]))
    for name,z in [('sill',-s),('header',height)]:
        parts.append(part('entry/'+name,[width,s,s],[-width/2,-s/2,z],'steel',kind='tube',axis=0,wall_m=wall,role='frame-member'))
    # Six butt-jointed shell panels. Empty space is not fabric, gas or a selected product.
    d=m['cassette_depth_m'];h=m['cassette_height_m'];t=m['cassette_panel_m'];z=height+s;y=-s/2
    for name,size,at in [
        ('bottom',[width,d,t],[-width/2,y,z]),('top',[width,d,t],[-width/2,y,z+h-t]),
        ('left',[t,d,h-2*t],[-width/2,y,z+t]),('right',[t,d,h-2*t],[width/2-t,y,z+t]),
        ('back',[width-2*t,t,h-2*t],[-width/2+t,y,z+t]),('front',[width-2*t,t,h-2*t],[-width/2+t,y+d-t,z+t])]:
        parts.append(part('cassette/'+name,size,at,'aluminium',role='case-panel'))
    reach=m['entry_outlet_standoff_m'] if standoff_m is None else model.positive(standoff_m,'stand-off');opening=m['entry_opening_m'];end=reach+opening/2+.08;approach=reach-opening/2
    if approach<=.04:raise ValueError('entry stand-off consumes approach floor')
    for side in (-1,1):
        x=-width/2 if side<0 else width/2-s
        parts.append(part(f'bridge/stringer-{side}',[s,end-.04,s],[x,.04,-s],'steel',kind='tube',axis=1,wall_m=wall,role='frame-member'))
        parts.append(part(f'bridge/guard-{side}',[s,.04,1.0],[x,approach-.04,0],'steel',kind='tube',axis=2,wall_m=wall,role='frame-member'))
    parts.append(part('bridge/approach-floor',[width-2*s,approach-.04,m['entry_floor_thickness_m']],[-width/2+s,.04,-m['entry_floor_thickness_m']],'aluminium',role='deck-panel'))
    parts.append(part('bridge/outlet-end',[width-2*s,.08,s],[-width/2+s,end-.08,-s],'steel',kind='tube',axis=0,wall_m=wall,role='frame-member'))
    r=geometry.finish('OSR-V05-EGRESS-ENTRY',parts,[
        dict(id='structural-frame-and-anchor-plates',parts=[p['id'] for p in parts if p['id'].startswith('entry/')]),
        dict(id='empty-cassette-shell',parts=[p['id'] for p in parts if p['id'].startswith('cassette/')]),
        dict(id='extended-entry-concept',parts=[p['id'] for p in parts if p['id'].startswith('bridge/')])],
        scope='Local doorway datum: x along vehicle, y outward, z up; sill z=0. Extended entry concept, not a deployable mechanism or selected chute.',
        holds=['No packed fabric, attachment bolts, hinges/locks, descent mechanism, guards enclosure or selected emergency equipment',
            'No deployed/stowed kinematics, collision trajectory or retention proof; extended hardware does not fit normal travel envelope',
            'Anchor strength, vehicle-body load path, fatigue, fire, rescue and accessibility remain open',
            'Modelled hardware mass is a partial lower scope; cannot replace the unknown complete chute/cassette installed mass'])
    for p in r['parts']:p['revision']='V05-EGRESS-ENTRY-1'
    r['interference_roles']=['frame-member','mount-plate','case-panel','deck-panel']
    r.update(door_clear_opening_m=[m['door_clear_width_m'],height],outlet_centre_local_m=[0,reach,0],
        complete_module_mass_kg=None,deployable_mechanism_defined=False,normal_travel_envelope_accepted=False)
    return r


def support_geometry(column_scale=.8,foundation_scale=.85,cap_scale=.75,*,span=None,pier_height=None):
    if not .5<=column_scale<=1 or not .5<=foundation_scale<=1 or not 4.6/7<=cap_scale<=1:raise ValueError('bounded support scales required')
    source=geometry.civil_bay(span,pier_height=pier_height);parts=[]
    origin=min(p['at_m'][0]+p['size_m'][0]/2 for p in source['parts'] if p['id'].endswith('/cap'))
    prefix=next(p['id'].rsplit('/',1)[0] for p in source['parts'] if p['id'].endswith('/cap') and p['at_m'][0]<0)
    for p in source['parts']:
        if not p['id'].startswith(prefix+'/'):continue
        p=deepcopy(p);p['id']=p['id'].replace(prefix,'study-support');p['at_m'][0]-=origin
        scale=column_scale if p['id'].endswith('/column') else foundation_scale if p['id'].endswith('/foundation-envelope') else cap_scale
        for axis in ((1,) if p['id'].endswith('/cap') else (0,1)):
            centre=p['at_m'][axis]+p['size_m'][axis]/2;p['size_m'][axis]*=scale;p['at_m'][axis]=centre-p['size_m'][axis]/2
        parts.append(p)
    r=geometry.finish('OSR-V05-COMPACT-SUPPORT',parts,[dict(id='foundation-envelope',parts=[p['id'] for p in parts if p['role']=='ground-assumption']),
        dict(id='column-and-cap',parts=[p['id'] for p in parts if p['role']!='ground-assumption'])],
        scope='One interior shared support: cap transverse width, column and shallow-foundation envelope widths varied independently. No qualified foundation family selected.',
        holds=['Ground/settlement, reinforcement/prestress, wind/seismic, axial-bending/shear/fatigue and connections unresolved',
            'Reduced dimensions are alternatives for demand screening, not accepted savings or production designs'])
    for p in r['parts']:p['revision']='V05-COMPACT-SUPPORT-1'
    r.update(column_scale=column_scale,foundation_scale=foundation_scale,cap_scale=cap_scale,foundation_selected=False)
    return r


def support_demands(*,column_scale=1.,foundation_scale=1.,cap_scale=1.,walkway=True,load_case='both-trains',additional_equipment_kg_per_car=0.,pier_height=None,_context=None):
    model.positive(additional_equipment_kg_per_car,'additional equipment mass',zero=True)
    if load_case not in {'empty','both-trains','one-train','one-beam-erection'}:raise ValueError('declared load case required')
    cfg,c=_context if _context is not None else (load(),model.load()[1]);span=c['civil']['reference_span_m'];g=9.81
    if cfg['civil']['passenger_payload_kg_per_car']!=c['vehicle']['aw3_passengers_per_car']*c['vehicle']['passenger_mass_screen_kg']:raise ValueError('matched full passenger load required')
    box=c['civil']['narrow_box_screen']
    native=geometry.civil_bay(span,width=box['outer_width_m'],depth=box['outer_depth_m'],web=box['web_thickness_m'],flange=box['flange_thickness_m']);support=support_geometry(column_scale,foundation_scale,cap_scale,span=span,pier_height=pier_height)
    # A continuous interior support receives half of each of two adjacent equal spans.
    beam=sum(p['modelled_mass_kg'] for p in native['parts'] if p['id'].startswith('beam-1/'))
    walks=sum(p['modelled_mass_kg'] for p in native['parts'] if p['id'].startswith('walkway-1-')) if walkway else 0.
    vehicle=model.mass(c,c['mass']['ferrite_base'],c['power']['gross_battery_matched_kwh_per_car'])
    live=(vehicle['tare_kg']+cfg['civil']['passenger_payload_kg_per_car']+additional_equipment_kg_per_car)/c['vehicle']['nominal_car_length_m']*span
    # Added equipment is an independent sensitivity, not a selected chute mass.
    masses=[beam+walks,beam+walks]
    if load_case=='both-trains':masses=[v+live for v in masses]
    if load_case=='one-train':masses[0]+=live
    if load_case=='one-beam-erection':masses=[beam,0.]
    cap,column,foundation=[next(p for p in support['parts'] if p['id'].endswith('/'+key)) for key in ('cap','column','foundation-envelope')]
    n_top=sum(masses)*g;moment=(masses[1]-masses[0])*1.9*g
    n_column=n_top+cap['modelled_mass_kg']*g
    n_base=n_column+column['modelled_mass_kg']*g
    n_ground=n_base+foundation['modelled_mass_kg']*g
    area=column['size_m'][0]*column['size_m'][1]
    section_modulus=column['size_m'][0]*column['size_m'][1]**2/6
    footing_area=foundation['size_m'][0]*foundation['size_m'][1]
    footing_z=foundation['size_m'][0]*foundation['size_m'][1]**2/6
    qmin=n_ground/footing_area-abs(moment)/footing_z;qmax=n_ground/footing_area+abs(moment)/footing_z
    return dict(column_scale=column_scale,foundation_scale=foundation_scale,cap_scale=cap_scale,walkway_included=walkway,load_case=load_case,
        additional_equipment_mass_sensitivity_kg_per_car=additional_equipment_kg_per_car,
        pier_height_m=column['size_m'][2],
        column_geometric_slenderness=[column['size_m'][2]/(d/math.sqrt(12)) for d in column['size_m'][:2]],
        tributary_span_m=span,track_vertical_reactions_n=[v*g for v in masses],column_top_axial_n=n_column,
        transverse_eccentric_moment_nm=moment,column_base_axial_n=n_base,ground_vertical_n=n_ground,
        column_nominal_extreme_stress_pa=[n_base/area-abs(moment)/section_modulus,n_base/area+abs(moment)/section_modulus],
        rectangular_footing_linear_contact_pa=[qmin,qmax],compression_only_linear_contact_admissible=qmin>=0,
        support_modelled_concrete_mass_kg=sum(p['modelled_mass_kg'] for p in support['parts']),
        soil_bearing_limit_pa=None,capacity_utilisation=None,approved_dimension_reduction=None,
        accepted=False,scope='Unfactored gravity/axial-eccentricity demand only. Linear footing contact assumes full contact; negative pressure invalidates that assumption. No pile/soil, settlement, wind/seismic/braking, prestress/rebar or stability acceptance.',**model.FLAGS)


def study():
    cfg=load();context=(cfg,model.load()[1]);entry=entry_geometry();doors=evacuation.load()['train'];per_car=doors['doors_per_side_per_car_screen']*doors['sides']
    extras=[*cfg['civil']['additional_equipment_mass_screens_kg_per_car'],entry['modelled_material_mass_kg']*per_car]
    rows=[support_demands(column_scale=cs,foundation_scale=fs,cap_scale=cap,walkway=walk,load_case=case,additional_equipment_kg_per_car=extra,_context=context)
        for cs,fs,cap,walk,case,extra in itertools.product(cfg['civil']['column_scales'],cfg['civil']['foundation_scales'],cfg['civil']['cap_scales'],(True,False),
            ('empty','both-trains','one-train','one-beam-erection'),extras)]
    entry=entry_geometry();reference=support_demands(_context=context);bare=support_demands(walkway=False,_context=context)
    variants=[]
    for reach in (.8,1.2,1.6,2.):
        hardware=entry_geometry(reach);path=evacuation.chute_guideway_path(towards_adjacent=False,standoff_m=reach)
        variants.append(dict(id=f'entry-outlet-{reach:g}m',standoff_m=reach,partial_hardware_mass_kg=hardware['modelled_material_mass_kg'],
            chute_path_clear_of_modelled_structure=path['path_clear_of_modelled_structure'],
            intersected_part_ids=path['intersected_box_part_ids'],complete_module_mass_kg=None,accepted=False))
    return dict(schema='osr-system-development-study/1',mechanical_variants=variants,assumptions=cfg,entry_hardware_part_count=len(entry['parts']),
        entry_partial_material_mass_kg=entry['modelled_material_mass_kg'],entry_units_per_car_hypothesis=per_car,
        entry_partial_material_mass_kg_per_car=entry['modelled_material_mass_kg']*per_car,
        entry_mass_is_gross_addition_sensitivity=True,net_added_egress_mass_kg_per_car=None,complete_module_mass_kg=None,
        support_cases=rows,support_case_count=len(rows),reference_loaded_support=reference,no_walkway_loaded_support=bare,
        gravity_reaction_reduction_percent=100*(reference['column_top_axial_n']-bare['column_top_axial_n'])/reference['column_top_axial_n'],
        separate_walkway_unit_placements_avoided_per_route_km=800,
        placement_basis='20 reference walkway cassettes per twin 25 m bay x 40 bays/km. Separate placements avoided only if separately erected; preassembled walkway/beam shipments may combine lifts.',
        actual_crane_cycles_saved=None,erection_working_days_saved=None,net_lifecycle_cost_saving_usd=None,
        mechanical_holds=entry['holds'],construction_stage_hold='One-beam erection has eccentric gravity demand; temporary stability and connection completion require independent design.',
        civil_acceptance=False,**model.FLAGS)


def sources():
    names=[*geometry.configuration.source_paths(),Path(__file__),INPUT,Path(coupled.__file__),Path(geometry.__file__),Path(evacuation.__file__),evacuation.INPUT,Path(media.__file__),
        Path(model.__file__),model.INPUT,model.ROOT/'engineering/factory_examples/native.py',model.ROOT/'engineering/factory_examples/models.py',
        model.ROOT/'Cargo.toml',model.ROOT/'Cargo.lock',model.ROOT/'rust-toolchain.toml',model.ROOT/'crates/osr-maglev-control/Cargo.toml']
    names+=list((model.ROOT/'crates/osr-maglev-control').rglob('*.rs'))
    names+=[model.ROOT/'docs/design-engine/ferrite-maglev/native/manifest.json',
            model.ROOT/'docs/design-engine/ferrite-maglev/native/civil-bay/native-mesh.json.gz']
    return {p.relative_to(model.ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(set(names))}


def software_replays():
    command=['cargo','build','--locked','--release','-p','osr-maglev-control','--example','egress_replay','--message-format=json']
    built=subprocess.run(command,cwd=model.ROOT,capture_output=True,text=True,check=True,timeout=180)
    executable=None
    for line in built.stdout.splitlines():
        event=json.loads(line)
        if event.get('reason')=='compiler-artifact' and event.get('target',{}).get('name')=='egress_replay' and event.get('executable'):executable=Path(event['executable'])
    if executable is None:raise ValueError('Cargo did not report egress replay executable')
    identity=sha256(encoded(entry_geometry())).hexdigest();revision=int(identity[:16],16)
    cases=[]
    for name,inner,height,surface in [('outward-20m',False,20.,'controlled-safe-dry-ground'),('inward-clash',True,20.,'controlled-safe-dry-ground'),
                                    ('height-gap-10m',False,10.,'controlled-safe-dry-ground'),('road-landing',False,20.,'live-road')]:
        path=evacuation.chute_guideway_path(towards_adjacent=inner,door_sill_height_m=height,standoff_m=load()['mechanical']['entry_outlet_standoff_m'])
        landing=evacuation.assess_landing(path['envelope'],surface=surface,clear_run_m=10,clear_width_m=5,usable_exits=1,obstruction_part_ids=path['intersected_box_part_ids'])
        heights=evacuation.assess_exit_heights([height],[8.,12.,20.,30.])
        arguments=[str(executable),str(revision),str(landing['geometry_screen_pass']).lower(),str(heights['all_sampled_heights_match']).lower()]
        raw=subprocess.run(arguments,cwd=model.ROOT,capture_output=True,text=True,check=True,timeout=30).stdout
        replay=json.loads(raw)
        if replay.get('physical_output_authorised') is not False or any(f['physical_output_authorised'] is not False for f in replay['frames']):raise ValueError('egress replay asserted physical output')
        cases.append(dict(id=name,entry_definition_sha256=identity,revision_tag=str(revision),landing=landing,height_coverage=heights,replay=replay))
    return dict(schema='osr-system-egress-execution/1',build_command=command,rustc=subprocess.check_output(['rustc','--version'],text=True,cwd=model.ROOT).strip(),
        executable_sha256=sha256(executable.read_bytes()).hexdigest(),cases=cases,
        limits='Actual Rust execution using calculated hypothetical geometry/height gates. Other readiness/assistance/security inputs are synthetic facts, not verified sensor or safety evidence.',physical_output_authorised=False)


def publish(output=OUTPUT):
    from engineering.factory_examples.native import generate
    before=sources();output=Path(output)
    if output.exists() and any(output.iterdir()):verify(output,require_current=False)
    work=model.ROOT/'build';work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='osr-system-development-',dir=work) as temp:
        target=Path(temp)
        for name,definition in [('entry',entry_geometry()),('compact-support',support_geometry())]:
            folder=target/name;folder.mkdir();path=folder/'definition.json';path.write_bytes(encoded(definition))
            receipt=generate(path,folder,model.ROOT);step=folder/'model.step';raw=step.read_bytes()
            (folder/'model.step.gz').write_bytes(gzip.compress(raw,mtime=0));step.unlink()
            receipt['files_sha256'].pop('model.step');receipt['files_sha256']['model.step.gz']=sha256((folder/'model.step.gz').read_bytes()).hexdigest()
            receipt['step_uncompressed_sha256']=sha256(raw).hexdigest();(folder/'native-cad.json').write_bytes(encoded(receipt));media.native_views(folder)
        result=study();(target/'study.json.gz').write_bytes(gzip.compress(encoded(result),mtime=0))
        (target/'software-replay.json').write_bytes(encoded(software_replays()))
        native_folder=model.ROOT/'docs/design-engine/ferrite-maglev/native'
        geometry.verify_native(native_folder)
        mesh=json.loads(gzip.decompress((native_folder/'civil-bay/native-mesh.json.gz').read_bytes()))
        native_mass=sum(p['volume_m3']*geometry.MATERIALS[p['material']] for p in mesh['parts'] if p['id'].startswith('beam-1/'))
        cv=geometry.configuration.selected().civil;span=cv.span_m
        section=model.section(cv.width_m,cv.depth_m,cv.web_m,cv.flange_m)
        assumptions=coupled.BeamAssumptions(span_m=span,line_mass_kg_m=native_mass/span,second_moment_m4=section['vertical_i_m4'])
        executable,execution=coupled._build_bridge()
        matched=dict(schema='osr-native-derived-guideway-coupling/1',native_beam_line_mass_kg_m=native_mass/span,
            native_mesh_sha256=before['docs/design-engine/ferrite-maglev/native/civil-bay/native-mesh.json.gz'],
            section_basis='Analytical reference box inertia; line mass recovered from native kernel volumes; no material/force-map validation',
            car_mass_kg=27750.+result['entry_partial_material_mass_kg_per_car'],complete_egress_system_included=False,
            partial_entry_hardware_mass_added_kg=result['entry_partial_material_mass_kg_per_car'],execution=execution,
            static_controls=coupled.static_benchmark(assumptions),replay=coupled.cosimulate(executable,assumptions=assumptions,car_mass_kg=27750.+result['entry_partial_material_mass_kg_per_car']),
            physical_output_authorised=False,structural_acceptance=False)
        (target/'native-derived-coupling.json').write_bytes(encoded(matched))
        stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=['id','revision','material','kind','length_m','width_m','height_m','modelled_mass_kg','production_released'])
        writer.writeheader()
        for p in entry_geometry()['parts']:
            writer.writerow(dict(id=p['id'],revision=p['revision'],material=p['material'],kind=p['kind'],length_m=p['size_m'][0],width_m=p['size_m'][1],height_m=p['size_m'][2],modelled_mass_kg=p['modelled_mass_kg'],production_released=False))
        (target/'entry-material-list.csv').write_text(stream.getvalue())
        rows=result['support_cases'];stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=['column_scale','foundation_scale','cap_scale','walkway_included','load_case','additional_equipment_mass_sensitivity_kg_per_car','column_top_axial_n','transverse_eccentric_moment_nm','ground_vertical_n','compression_only_linear_contact_admissible'])
        writer.writeheader();writer.writerows({k:r[k] for k in writer.fieldnames} for r in rows);(target/'support-demands.csv').write_text(stream.getvalue())
        if sources()!=before:raise ValueError('system sources changed during execution')
        manifest=dict(schema='osr-system-development-packet/1',source_sha256=before,files_sha256={p.relative_to(target).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(target.rglob('*')) if p.is_file()},**model.FLAGS)
        (target/'manifest.json').write_bytes(encoded(manifest));verify(target)
        output.mkdir(parents=True,exist_ok=True)
        for name in [*manifest['files_sha256'],'manifest.json']:
            (output/name).parent.mkdir(parents=True,exist_ok=True);os.replace(target/name,output/name)
    return verify(output)


def verify(output=OUTPUT,*,require_current=True):
    output=Path(output);m=json.loads((output/'manifest.json').read_text())
    expected={f'{folder}/{name}' for folder in ('entry','compact-support') for name in ('definition.json','model.FCStd','model.step.gz','native-cad.json','native-mesh.json.gz','overview.png','assembly-visibility.mp4','visual-receipt.json')}|{'study.json.gz','software-replay.json','native-derived-coupling.json','support-demands.csv','entry-material-list.csv'}
    actual={p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}
    if m['schema']!='osr-system-development-packet/1' or set(m['files_sha256'])!=expected or actual!=expected|{'manifest.json'}:raise ValueError('exact system packet identity/inventory required')
    if any(m.get(k) is not False for k in model.FLAGS):raise ValueError('system physical/manufacturing claim unsupported')
    if require_current and m['source_sha256']!=sources():raise ValueError('system packet source differs')
    for name,digest in m['files_sha256'].items():
        p=output/name
        if p.is_symlink() or sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('system packet file differs: '+name)
    if not require_current:return m
    if json.loads(gzip.decompress((output/'study.json.gz').read_bytes()))!=study():raise ValueError('system study differs from exact calculations')
    for name,definition in [('entry',entry_geometry()),('compact-support',support_geometry())]:
        folder=output/name;r=json.loads((folder/'native-cad.json').read_text());visual=json.loads((folder/'visual-receipt.json').read_text())
        if json.loads((folder/'definition.json').read_text())!=definition or r['input_sha256']!=sha256((folder/'definition.json').read_bytes()).hexdigest():raise ValueError('system native definition differs')
        if not r['fcstd_reopened'] or not r['step_reopened'] or r['part_count']!=len(definition['parts']):raise ValueError('system native reopen evidence missing')
        for receipt in (r,visual):
            if receipt.get('physical_release') is not False:raise ValueError('system native physical release unsupported')
            for key,digest in receipt['files_sha256'].items():
                if key!=Path(key).name or m['files_sha256'].get(name+'/'+key)!=digest:raise ValueError('system nested receipt differs')
        if visual['mesh_sha256']!=m['files_sha256'][name+'/native-mesh.json.gz'] or visual['renderer_sha256']!=sha256(Path(media.__file__).read_bytes()).hexdigest():raise ValueError('system visual source/mesh differs')
    matched=json.loads((output/'native-derived-coupling.json').read_text())
    if matched['physical_output_authorised'] is not False or matched['structural_acceptance'] is not False or matched['complete_egress_system_included'] is not False:raise ValueError('native-derived coupling scope/authority differs')
    if any(matched['replay'].get(k) is not False for k in ('physical_output_authorised','structural_acceptance')):raise ValueError('coupled replay asserted authority')
    if matched['replay']['beam_assumptions']['line_mass_kg_m']!=matched['native_beam_line_mass_kg_m']:raise ValueError('native beam mass not used by coupled replay')
    if matched['replay']['car_mass_kg']!=matched['car_mass_kg'] or matched['car_mass_kg']!=27750.+study()['entry_partial_material_mass_kg_per_car']:raise ValueError('partial hardware mass not used by car/controller replay')
    if matched['native_mesh_sha256']!=m['source_sha256']['docs/design-engine/ferrite-maglev/native/civil-bay/native-mesh.json.gz']:raise ValueError('coupled replay native identity differs')
    executed=json.loads((output/'software-replay.json').read_text());identity=sha256(encoded(entry_geometry())).hexdigest()
    if executed['physical_output_authorised'] is not False or len(executed['cases'])!=4:raise ValueError('system replay identity differs')
    if {c['id'] for c in executed['cases']}!={'outward-20m','inward-clash','height-gap-10m','road-landing'}:raise ValueError('egress scenario coverage differs')
    for case in executed['cases']:
        if case['replay'].get('physical_output_authorised') is not False:raise ValueError('egress replay asserted physical authority')
        phases=[f['phase'] for f in case['replay']['frames']]
        if case['id']=='outward-20m' and phases!=['StopRequested','Assessing','Assessing','Ready','DeploymentStudy','FlowStudy','FlowStudy','CompleteHold','CompleteHold']:raise ValueError('egress positive sequence differs')
        if case['id']!='outward-20m' and any(p in {'Ready','DeploymentStudy','FlowStudy','CompleteHold'} for p in phases):raise ValueError('failed clearance/height case entered deployment sequence')
        if case['entry_definition_sha256']!=identity or case['revision_tag']!=str(int(identity[:16],16)):raise ValueError('system replay uses a different entry candidate')
        if any(frame['physical_output_authorised'] is not False for frame in case['replay']['frames']):raise ValueError('system replay claims physical output')
    return m
