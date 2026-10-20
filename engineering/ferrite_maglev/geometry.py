"""Dimensioned magnetic-interface and civil-kit research solids, SI units.

These are physical material regions and explicit envelope hypotheses, not
released train designs. Missing magnetic circuit, joints, fastener qualification,
reinforcement, winding detail and soil evidence remain manufacturing holds.
"""
from hashlib import sha256
import gzip
import json
import math
from pathlib import Path
import subprocess
import sys

from . import model,configuration

MATERIALS={'steel':7850.,'aluminium':2700.,'ferrite':5000.,'concrete':2500.,'winding-envelope':5500.}


def part(identity,size,at,material,*,role=None,kind='box',**kw):
    if len(size)!=3 or len(at)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) for v in [*size,*at]) or min(size)<=0:
        raise ValueError('positive finite physical dimensions and finite placement required')
    return dict(id=identity,size_m=list(size),at_m=list(at),kind=kind,material=material,
                role=role or material,basis='OSR v0.5 dimensional hypothesis; material and manufacturing acceptance open',**kw)


def volume(p):
    size=p['size_m'];value=math.prod(size)
    if p['kind']=='tube':
        inner=list(size)
        for i in range(3):
            if i!=p['axis']:inner[i]-=2*p['wall_m']
        if min(inner)<=0:raise ValueError('tube wall consumes bore')
        value-=math.prod(inner)
    elif p['kind']=='cylinder':value=math.pi*size[0]*size[1]*size[2]/4
    for h in p.get('holes',[]):value-=math.pi*(h['diameter_m']/2)**2*h.get('length_m',size['xyz'.index(h.get('axis','z'))])
    if value<=0:raise ValueError('nonpositive net material volume')
    return value


def finish(identity,parts,stages,*,scope,holds):
    if len({p['id'] for p in parts})!=len(parts):raise ValueError('duplicate manufactured part identity')
    for p in parts:
        p['volume_m3']=volume(p);p['density_assumption_kg_m3']=MATERIALS[p['material']]
        p['modelled_mass_kg']=p['volume_m3']*MATERIALS[p['material']]
        p['revision']='V05-INTERFACE-1';p['production_released']=False
    total=sum(p['modelled_mass_kg'] for p in parts)
    cg=[sum(p['modelled_mass_kg']*(p['at_m'][i]+p['size_m'][i]/2) for p in parts)/total for i in range(3)]
    # This ledger is distinct from the whole-vehicle target. Coil envelopes use
    # homogenised density; no inference of actual winding or calibrated mass.
    return dict(schema='osr-maglev-development-solids/1',id=identity,parts=parts,construction_stages=stages,
                retain_native_tessellation=True,
                interference_roles=['ferrite','carrier','retainer','fastener','magnetic-rail'],
                material_density_assumptions_kg_m3=MATERIALS,modelled_material_mass_kg=total,modelled_cg_m=cg,
                scope=scope,holds=holds,physical_release=False,manufacturing_release=False,design_complete=False)


def beam_parts(prefix,span,centre_y=0,*,width=None,depth=None,web=None,flange=None):
    cv=configuration.selected().civil
    width=cv.width_m if width is None else width;depth=cv.depth_m if depth is None else depth
    web=cv.web_m if web is None else web;flange=cv.flange_m if flange is None else flange
    model.positive(span,'span')
    model.section(width,depth,web,flange)
    x=-span/2;y=centre_y;p=[]
    p.append(part(prefix+'/top-slab',[span,width,flange],[x,y-width/2,-flange],'concrete'))
    p.append(part(prefix+'/bottom-slab',[span,width,flange],[x,y-width/2,-depth],'concrete'))
    for side in (-1,1):
        at=y-width/2 if side<0 else y+width/2-web
        p.append(part(prefix+f'/web-{side}',[span,web,depth-2*flange],[x,at,-depth+flange],'concrete'))
        for index in range(math.ceil(span/cv.rail_pitch_m)):
            start=x+index*cv.rail_pitch_m;length=min(cv.rail_segment_length_m,span-(start-x))
            ry=y+width/2 if side>0 else y-width/2-cv.rail_width_m
            p.append(part(prefix+f'/lift-rail-{side}-{index}',[length,cv.rail_width_m,cv.rail_thickness_m],[start,ry,-.3], 'steel',role='magnetic-rail'))
    return p


def interface(variant='recessed-retainer'):
    if variant not in {'unrepaired','flat-retainer','recessed-retainer'}:raise ValueError('unknown cartridge variant')
    recessed=variant=='recessed-retainer'
    keeper_z=-.313 if recessed else -.308
    head_z=keeper_z+.002
    head_height=.003 if recessed else .004
    shank_length=head_z+.364
    bolt_offset=.2595 if variant=='unrepaired' else .258
    side_length=.968 if variant=='unrepaired' else .958
    side_start=-side_length/2
    hole_y=(.27-bolt_offset,.27+bolt_offset)
    p=beam_parts('guideway',configuration.selected().civil.span_m);groups={'guideway':[v['id'] for v in p]}
    frame=[]
    for side in (-1,1):
        frame.append(part(f'frame/stringer-{side}',[17,.1,.18],[-8.5,side*1.1-.05,.11],'steel',kind='tube',wall_m=.008,axis=0))
        frame.append(part(f'frame/lift-collector-{side}',[12,.08,.08],[-6,side*.88-.04,-.444],'steel',kind='tube',wall_m=.006,axis=0))
    for x in (-8,-6,-4,-2,0,2,4,6,8):
        frame.append(part(f'frame/crossmember-{x}',[.08,2.1,.1],[x-.04,-1.05,.19],'steel',kind='tube',wall_m=.005,axis=1))
    frame.append(part('frame/floor-material-region',[17,2.65,.01],[-8.5,-1.325,.29],'aluminium'))
    for x in (-6,6):
        frame.append(part(f'frame/lower-crosshead-{x}',[.1,2.96,.08],[x-.05,-1.48,-.524],'steel',kind='tube',wall_m=.006,axis=1))
        for side in (-1,1):
            frame.append(part(f'frame/u-arm-{x}-{side}',[.1,.08,.654],[x-.05,side*1.44-.04,-.444],'steel',kind='tube',wall_m=.006,axis=2))
            frame.append(part(f'frame/outrigger-{x}-{side}',[.1,.33,.08],[x-.05,1.15 if side>0 else -1.48,.21],'steel',kind='tube',wall_m=.006,axis=1))
    p+=frame;groups['frame']=[v['id'] for v in frame]
    modules=[];blocks=[]
    for side in (-1,1):
        y=side*.88
        for j in range(12):
            x=j-5.5;uid=f'cartridge/{side}/{j:02d}';mp=[]
            if recessed:
                mp.append(part(uid+'/ferrite-centre',[.87,.5,.05],[x-.435,y-.25,-.358],'ferrite'))
                for end in (-1,1):mp.append(part(uid+f'/ferrite-recess-{end}',[.04,.5,.045],[x+end*.455-.02,y-.25,-.358],'ferrite'))
            else:mp.append(part(uid+'/ferrite-region',[.95,.5,.05],[x-.475,y-.25,-.358],'ferrite'))
            mp.append(part(uid+'/tray',[.98,.54,.006],[x-.49,y-.27,-.364],'steel',role='carrier',holes=[
                dict(axis='z',x_m=xx,y_m=yy,diameter_m=.009) for xx in (.035,.945) for yy in hole_y]))
            for end in (-1,1):
                mp.append(part(uid+f'/end-wall-{end}',[.006,.54,.046],[x+end*.482-.003,y-.27,-.358],'steel',role='carrier'))
                mp.append(part(uid+f'/keeper-{end}',[.04,.54,.002],[x+end*.455-.02,y-.27,keeper_z],'steel',role='retainer',holes=[dict(axis='z',x_m=.02,y_m=yy,diameter_m=.009) for yy in hole_y]))
                for edge in (-1,1):
                    bx=x+end*.455;by=y+edge*bolt_offset
                    mp.append(part(uid+f'/bolt-{end}-{edge}/shank',[.008,.008,shank_length],[bx-.004,by-.004,-.364],'steel',role='fastener',kind='cylinder'))
                    mp.append(part(uid+f'/bolt-{end}-{edge}/head',[.012,.012,head_height],[bx-.006,by-.006,head_z],'steel',role='fastener',kind='cylinder'))
                    mp.append(part(uid+f'/bolt-{end}-{edge}/nut',[.014,.014,.006],[bx-.007,by-.007,-.370],'steel',role='fastener',kind='cylinder',holes=[dict(axis='z',x_m=.007,y_m=.007,diameter_m=.009)]))
            for edge in (-1,1):
                mp.append(part(uid+f'/side-wall-{edge}',[side_length,.008,.044 if recessed else .046],[x+side_start,y+edge*.266-.004,-.358],'steel',role='carrier'))
                mp.append(part(uid+f'/winding-window-{edge}',[.3,.1,.06],[x-.15,y+edge*.18-.05,-.424],'winding-envelope'))
            p+=mp;modules.append(dict(id=uid,centre_x_m=x,centre_y_m=y,part_ids=[v['id'] for v in mp],ferrite_blocks=190,
                                     ferrite_mass_kg=117.75 if recessed else 118.75,winding_turns=None,wire_section_mm2=None,calibrated_force_map=None))
            # Exact 50mm cube locations; native solid aggregates remain one
            # material region per cartridge. Polarity patterns are NOT invented.
            for a in range(19):
                for b in range(10):blocks.append(dict(id=uid+f'/block-{a:02d}-{b:02d}',size_m=[.05]*3,
                    at_m=[x-.475+a*.05,y-.25+b*.05,-.358],magnetisation_axis=None,supplier_grade=None,
                    edge_recess_m=dict(length=.04,depth=.005,at='left' if a==0 else 'right') if recessed and a in (0,18) else None))
    groups['cartridges']=[v for m in modules for v in m['part_ids']]
    stages=[dict(id=k,parts=ids) for k,ids in groups.items()]
    result=finish('OSR-V05-MAGNETIC-INTERFACE',p,stages,
        scope=f'One provisional 17m floor/frame and 24-cartridge lift interface on a {configuration.selected().civil.span_m:g}m guidebeam; no cabin fitout or functional propulsion circuit',
        holds=['force/thermal/demagnetisation map and grade selection','keeper/bolt/potting retention under fault/crash/fatigue',
               'gap/thermal/control/structure error budget and low-profile fastener qualification remain open',
               'supplier-ground ferrite edge recesses need crack/demagnetisation/dimensional qualification; not an accepted machining process',
               '2.96m below-floor arm envelope exceeds2.65m cabin; sweep/platform/egress revalidation',
               'rail faces/corbels/embedded anchors, structural joints and production winding detail',
               'body/doors/glazing/interior/HVAC/battery/capture/propulsion components not included in this partial model'])
    result.update(variant=variant,modules=modules,ferrite_block_inventory=blocks,
        magnet_budget=dict(total_allocated_kg=3000,lift_modelled_kg=2826 if recessed else 2850,guidance_propulsion_reserved_unmodelled_kg=174 if recessed else 150,
                           shared_magnetic_volume_demonstrated=False),
        clearances=dict(nominal_magnet_to_lift_face_m=.008,keeper_to_face_m=-.3-(keeper_z+.002),bolt_head_to_face_m=-.3-(head_z+head_height),
                        transverse_arm_to_rail_edge_on_tangent_m=.04,
                        full_error_budget_accepted=False),
        magnetic_area=dict(gross_lift_face_m2=24*.95*.5,keeper_obscured_area_screen_m2=24*.08*.5,
                           exposed_area_screen_m2=24*.87*.5,actual_effective_area_m2=None),
        whole_vehicle_mass_kg=None)
    return result


def guideway_quantities(span=None,*,width=None,depth=None,web=None,flange=None):
    """One source of material quantities, including actual segmented rail lengths.

    Magnetic attachments and winding hardware not represented in these solids
    remain unquantified. The former 100 kg/m is a historical comparator only.
    """
    if span is None:span=configuration.selected().civil.span_m
    parts=beam_parts('quantity',span,width=width,depth=depth,web=web,flange=flange)
    rail=sum(volume(p)*MATERIALS[p['material']] for p in parts if p['role']=='magnetic-rail')
    concrete=sum(volume(p)*MATERIALS[p['material']] for p in parts if p['material']=='concrete')
    return dict(span_m=span,magnetic_rail_mass_kg=rail,magnetic_rail_line_mass_kg_m=rail/span,
        beam_concrete_mass_kg=concrete,beam_concrete_line_mass_kg_m=concrete/span,
        total_line_mass_kg_m=(rail+concrete)/span,
        historical_magnetic_allowance_kg_m=100.,unmodelled_attachment_mass_kg=None)


def civil_bay(span=None,*,width=None,depth=None,web=None,flange=None,pier_height=None):
    cv=configuration.selected().civil
    span=cv.span_m if span is None else span;pier_height=cv.pier_height_m if pier_height is None else pier_height
    model.positive(pier_height,'pier height')
    depth=cv.depth_m if depth is None else depth
    p=[];stages=[]
    for side in (-1,1):p+=beam_parts(f'beam-{side}',span,side*1.9,width=width,depth=depth,web=web,flange=flange)
    stages.append(dict(id='beams-and-functional-rails',parts=[v['id'] for v in p]))
    sub=[]
    for x in (-span/2,span/2):
        sub.append(part(f'support-{x}/cap',[2.5,7,1.2],[x-1.25,-3.5,-depth-1.2],'concrete'))
        sub.append(part(f'support-{x}/column',[1.5,2,pier_height],[x-.75,-1,-depth-1.2-pier_height],'concrete'))
        sub.append(part(f'support-{x}/foundation-envelope',[4.5,4.5,1.2],[x-2.25,-2.25,-depth-2.4-pier_height],'concrete',role='ground-assumption'))
    p+=sub;stages.append(dict(id='support-ground-assumptions',parts=[v['id'] for v in sub]))
    walk=[]
    for side in (-1,1):
        for j in range(math.ceil(span/2.5)):
            x=-span/2+j*2.5
            walk.append(part(f'walkway-{side}-{j}',[min(2.49,span-j*2.5),1,.12],[x,3.6 if side>0 else -4.6,-.02],'concrete'))
    p+=walk;stages.append(dict(id='walkway-cassettes',parts=[v['id'] for v in walk]))
    r=finish('OSR-V05-CIVIL-BAY',p,stages,scope=f'Dual-direction {span:g}m geometric kit; solid cap and shallow foundation envelopes are alternative study inputs, not site designs',
        holds=['soil/pile/shallow-foundation selection and settlement','prestress/rebar/diaphragms and lifting inserts','corbels/bearings/joints/walkway brackets/anchors',
               'local magnetic loads, torsion, wind, seismic and fault/capture loads','transport/crane ground support and connection/strength development',
               'walkway supports and egress/platform swept envelope; no installed cost or structural release'])
    r['foundation_selected']=False;r['construction_stage_strength_verified']=False
    return r


def publish_native(output):
    """Execute actual FreeCAD exports and reopen checks using the retained native adapter."""
    from engineering.factory_examples.native import generate
    output=Path(output);output.mkdir(parents=True,exist_ok=True);receipts={}
    for definition in (interface(),civil_bay()):
        name='interface' if definition['id'].endswith('INTERFACE') else 'civil-bay'
        folder=output/name;folder.mkdir(parents=True,exist_ok=True)
        path=folder/'definition.json';path.write_text(json.dumps(definition,indent=2,sort_keys=True)+'\n')
        receipt=generate(path,folder,model.ROOT)
        # Retain compressed interchange, with a receipt updated to exact bytes.
        step=folder/'model.step';raw=step.read_bytes();compressed=folder/'model.step.gz';compressed.write_bytes(gzip.compress(raw,mtime=0))
        receipt['files_sha256'].pop('model.step');receipt['files_sha256']['model.step.gz']=sha256(compressed.read_bytes()).hexdigest()
        receipt['step_uncompressed_sha256']=sha256(raw).hexdigest();step.unlink()
        (folder/'native-cad.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');receipts[name]=receipt
    return receipts


def seal_native(output):
    """Bind actual exports and renders to this exact geometry revision."""
    output=Path(output)
    paths=[p for p in output.rglob('*') if p.is_file() and p.name!='manifest.json']
    manifest=dict(schema='osr-maglev-native-packet/1',
        geometry_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        geometry_sources_sha256={p.relative_to(model.ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in configuration.source_paths()},
        exporter_sha256=sha256((model.ROOT/'engineering/factory_examples/native.py').read_bytes()).hexdigest(),
        files_sha256={p.relative_to(output).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(paths)},
        physical_release=False,manufacturing_release=False)
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    return verify_native(output)


def verify_native(output):
    output=Path(output);manifest=json.loads((output/'manifest.json').read_text())
    if manifest['schema']!='osr-maglev-native-packet/1' or any(manifest.get(k) is not False for k in ('physical_release','manufacturing_release')):
        raise ValueError('native packet identity or release differs')
    if manifest.get('geometry_sources_sha256')!={p.relative_to(model.ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in configuration.source_paths()}:raise ValueError('native geometry configuration changed')
    actual={p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file() and p.name!='manifest.json'}
    required={folder+'/'+name for folder in ('interface','civil-bay') for name in (
        'definition.json','model.FCStd','model.step.gz','native-cad.json','native-mesh.json.gz',
        'overview.png','assembly-visibility.mp4','visual-receipt.json')}|{'interface/cartridge-detail.png'}
    if set(manifest['files_sha256'])!=required or actual!=required:raise ValueError('exact native packet inventory required')
    for key,path in [('geometry_sha256',Path(__file__)),('exporter_sha256',model.ROOT/'engineering/factory_examples/native.py')]:
        if manifest[key]!=sha256(path.read_bytes()).hexdigest():raise ValueError('native packet source changed')
    for name,digest in manifest['files_sha256'].items():
        p=Path(name)
        if p.is_absolute() or '..' in p.parts or p.as_posix()!=name:raise ValueError('unsafe native path')
        if (output/p).is_symlink() or sha256((output/p).read_bytes()).hexdigest()!=digest:raise ValueError('native packet file differs: '+name)
    for name,definition in [('interface',interface()),('civil-bay',civil_bay())]:
        folder=output/name
        if json.loads((folder/'definition.json').read_text())!=definition:raise ValueError('native definition changed')
        receipt=json.loads((folder/'native-cad.json').read_text())
        if receipt['input_sha256']!=sha256((folder/'definition.json').read_bytes()).hexdigest():raise ValueError('native input receipt differs')
        if not receipt['fcstd_reopened'] or not receipt['step_reopened']:raise ValueError('native reopen evidence missing')
        if receipt['part_count']!=len(definition['parts']):raise ValueError('native part inventory differs')
        visual=json.loads((folder/'visual-receipt.json').read_text())
        if visual['renderer_sha256']!=sha256(Path(__file__).with_name('media.py').read_bytes()).hexdigest():raise ValueError('native renderer source changed')
        if visual['mesh_sha256']!=sha256((folder/'native-mesh.json.gz').read_bytes()).hexdigest():raise ValueError('visual mesh identity differs')
        for rec in (receipt,visual):
            if rec.get('physical_release') is not False:raise ValueError('native evidence asserted release')
            for filename,digest in rec['files_sha256'].items():
                if filename!=Path(filename).name or sha256((folder/filename).read_bytes()).hexdigest()!=digest:raise ValueError('native evidence checksum differs')
    return manifest
