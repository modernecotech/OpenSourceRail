"""Joined structural material regions, native interference and geometry-derived mass.

A complete inventory of this candidate's defined stock is not an equipped train
or a manufacturing release. Unqualified joints, materials, magnetic forces and
omitted equipment remain explicit acceptance holds.
"""
from copy import deepcopy
from hashlib import sha256
import gzip
import io
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import zipfile

from . import closure, configuration, geometry, model, station_native, station_structure as structure
from engineering.factory_examples import models, native

ROOT=model.ROOT
INPUT=Path(__file__).with_name('assembled-body.toml')
LEGACY=Path(__file__).with_name('data')/'assembled-body-legacy-interface.json'
REJECTED=Path(__file__).with_name('data')/'assembled-body-rejected-eight-bolt.json'
REJECTED_FLANGE=Path(__file__).with_name('data')/'assembled-body-rejected-twelve-bolt.json'
TEST=ROOT/'engineering/analysis/tests/test_ferrite_maglev_assembled_body.py'
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/assembled-body'
SCHEMA='osr-assembled-structural-body/1'
FILES={'definition.json','study.json.gz','README.md','cut-list.csv','sections.svg',
       'model.FCStd','model.step.gz','native-cad.json','native-mesh.json.gz','mass-properties.json',
       'legacy-collision-control.json','tool-access.json','overview.png','frame-cutaway.png','six-car.png',
       'assembly-visibility.mp4','visual-receipt.json'}
MAX_BYTES=64*1024*1024
MAX_RAW=256*1024*1024
FLAGS={**model.FLAGS,'engineering_accepted':False}


def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()

def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!=SCHEMA or any(a[k] is not False for k in ('material_properties_qualified','complete_equipped_vehicle','adopt_mass_or_stiffness_in_city_defaults')):
        raise ValueError('provisional non-adopted body required')
    for group in ('geometry','hardpoint','render'):
        for k,v in a[group].items():
            if isinstance(v,list):
                if not v or len(v)!=len(set(v)) or any(type(x) not in (int,float) or not math.isfinite(x) for x in v):raise ValueError('finite distinct geometry coordinates required')
            elif type(v) not in (int,float) or not math.isfinite(v) or (v<=0 and k not in {'collector_lower_z_m','arm_lower_z_m','cantilever_lower_z_m'}):
                raise ValueError('finite positive bounded geometry required: '+k)
    h=a['hardpoint']
    if type(h['bolts']) is not int or h['bolts']!=len(h['columns_x_m'])*len(h['rows_z_m']) or not 4<=h['bolts']<=16:raise ValueError('bounded exact bolt-grid candidate required')
    if not h['bolt_hole_m']>h['bolt_diameter_m'] or not h['spacer_bore_m']>=h['bolt_hole_m']:raise ValueError('positive bolt/bore clearance required')
    if h['prying_multiplier']<1 or h['carrier_width_m']<=2*h['carrier_wall_m'] or h['carrier_depth_m']<=2*h['carrier_wall_m']:raise ValueError('valid carrier and explicit prying factor required')
    if not 0<h['mesh_relative_volume_tolerance']<=.03:raise ValueError('bounded mesh approximation tolerance required')
    if a['geometry']['arm_outer_y_m']!=configuration.selected().formation.arm_width_m/2:raise ValueError('selected arm envelope must be retained')
    old=json.loads(LEGACY.read_text())
    if (old['schema']!='osr-retained-interface-negative-control/1' or old['accepted'] is not False
            or sha256(encoded(old['definition'])).hexdigest()!=old['definition_sha256']
            or sha256(encoded(old['historical_native_manifest'])).hexdigest()!=old['historical_native_manifest_sha256']
            or old['historical_native_manifest']['files_sha256']['interface/definition.json']!=old['definition_sha256']):
        raise ValueError('immutable historical native control identity differs')
    rejected=json.loads(REJECTED.read_text())
    if (rejected['schema']!='osr-rejected-assembled-body-candidate/1'
            or sha256(encoded(rejected['definition'])).hexdigest()!=rejected['definition_sha256']
            or rejected['configuration']['hardpoint']['bolts']!=8
            or rejected['tension_per_bolt_n']<=rejected['inboard_wall_pullthrough_capacity_n']
            or rejected['eligible_for_assembled_adoption'] is not False or rejected['accepted'] is not False):
        raise ValueError('retained failed eight-bolt revision differs')
    rejected=json.loads(REJECTED_FLANGE.read_text())
    if (rejected['schema']!='osr-rejected-assembled-body-candidate/1' or sha256(encoded(rejected['definition'])).hexdigest()!=rejected['definition_sha256']
            or rejected['configuration']['hardpoint']['bolts']!=12 or rejected['tension_per_bolt_n']<=rejected['inboard_wall_pullthrough_capacity_n']
            or rejected['eligible_for_assembled_adoption'] is not False or rejected['accepted'] is not False):raise ValueError('retained failed flange-plane twelve-bolt revision differs')
    return a


def source_paths():
    return sorted({Path(__file__),INPUT,LEGACY,REJECTED,REJECTED_FLANGE,TEST,Path(native.__file__),Path(models.__file__),
        Path(geometry.__file__),Path(station_native.__file__),*closure.source_paths()})

def sources():return {p.relative_to(ROOT).as_posix():digest(p) for p in source_paths()}


def tube_regions(identity,size,at,axis,wall,material,role,*,holes=None):
    """Four disjoint native wall regions; through-bolts cut actual walls only."""
    uv=[i for i in range(3) if i!=axis];u,v=uv;out=[]
    for coord,label in ((u,'u'),(v,'v')):
        for side in (-1,1):
            sz=list(size);pos=list(at);sz[coord]=wall
            if side>0:pos[coord]+=size[coord]-wall
            if coord==v:sz[u]-=2*wall;pos[u]+=wall
            hs=[]
            for hole in holes or []:
                if 'xyz'.index(hole['axis'])!=coord:continue
                other=[i for i in range(3) if i!=coord]
                if all(pos[i]+hole['diameter_m']/2<hole['centre_m'][i]<pos[i]+sz[i]-hole['diameter_m']/2 for i in other):
                    hs.append(dict(axis=hole['axis'],diameter_m=hole['diameter_m'],
                        **{'xyz'[i]+'_m':hole['centre_m'][i]-pos[i] for i in other}))
            p=geometry.part(identity+f'/wall-{label}-{side}',sz,pos,material,role=role)
            if hs:p['holes']=hs
            p['parent_member_id']=identity;out.append(p)
    return out


def definition():
    a=load();d=closure.load();b=d['body'];f=d['frame_remainder'];cfg=configuration.selected()
    bd=structure.body();L,W,H=(bd['envelope_m'][k] for k in ('length','width','height'))
    st=structure.load()['body']['cases']['central'];g=a['geometry'];hp=a['hardpoint']
    upper=[(st['upper_face_each_m'],'gfrp'),(st['upper_core_m'],'core-80'),(st['upper_face_each_m'],'gfrp'),(st['upper_bond_finish_kg_m2']/1000,'bond-surface')]
    floor=[(st['floor_faces_total_m']/2,'gfrp'),(st['floor_core_m'],'core-100'),(st['floor_faces_total_m']/2,'gfrp'),(st['floor_bond_finish_kg_m2']/1000,'bond-surface')]
    t=sum(x[0] for x in upper);ft=sum(x[0] for x in floor);floor_top=.3;floor_bottom=floor_top-ft;roof_bottom=floor_top+H-t
    bond=g['panel_corner_bond_m'];wall_top=roof_bottom-bond;wall_bottom=floor_top+bond
    rib_top=floor_bottom;rib_bottom=rib_top-b['rib_depth_m'];stringer_top=rib_bottom;stringer_bottom=stringer_top-b['stringer_outer_depth_m'];sz=(stringer_top+stringer_bottom)/2
    parts=[];groups={};members=[];interfaces=[]
    def add(identity,size,at,material,group,**kw):
        p=geometry.part(identity,size,at,material,role=group,**kw);parts.append(p);groups.setdefault(group,[]).append(identity);return p
    def tube(identity,size,at,axis,wall,material,group,source_id=None,holes=None):
        ps=tube_regions(identity,size,at,axis,wall,material,group,holes=holes)
        parts.extend(ps);groups.setdefault(group,[]).extend(p['id'] for p in ps)
        members.append(dict(id=identity,source_member_id=source_id,size_m=list(size),at_m=list(at),axis=axis,wall_m=wall,material=material,part_ids=[p['id'] for p in ps]))
    def plate(identity,size,at,material,group,centres=(),axis='y'):
        p=add(identity,size,at,material,group)
        if centres:
            other=[i for i in range(3) if i!='xyz'.index(axis)]
            p['holes']=[dict(axis=axis,diameter_m=hp['bolt_hole_m'],**{'xyz'[i]+'_m':c[i]-at[i] for i in other}) for c in centres]
        return p
    # Sandwich corners are real butt joints with separately counted 1mm bond.
    def panel(name,width,height,holes,axis,fixed,origin,layers):
        offset=0.
        for layer,(thick,mat) in enumerate(layers):
            for index,(x,y,dx,dy) in enumerate(structure._rectangles(width,height,holes)):
                size=[dx,dy,thick] if axis=='z' else [dx,thick,dy] if axis=='y' else [thick,dx,dy]
                pos=[origin[0]+x,origin[1]+y,fixed+offset] if axis=='z' else [origin[0]+x,fixed+offset,origin[1]+y] if axis=='y' else [fixed+offset,origin[0]+x,origin[1]+y]
                add(f'panel/{name}/layer-{layer}/region-{index}',size,pos,mat,'panel-'+name.split('-')[0])
            offset+=thick
    panel('floor',L,W,[],'z',floor_bottom,[-L/2,-W/2],floor)
    panel('roof',L,W,[],'z',roof_bottom,[-L/2,-W/2],upper)
    side_len=L-2*(t+bond);side_x=-L/2+t+bond;side_height=wall_top-wall_bottom
    sideholes=[]
    for c in (-4.5,4.5):sideholes.append((c-.7-side_x,0.,c+.7-side_x,2.1-(wall_bottom-floor_top)))
    for c in (-6.5,-1.5,1.5,6.5):sideholes.append((c-1-side_x,.9-(wall_bottom-floor_top),c+1-side_x,2.4-(wall_bottom-floor_top)))
    endholes=[(W/2-.65,0.,W/2+.65,2.5-(wall_bottom-floor_top))]
    for side in (-1,1):
        y=-W/2 if side<0 else W/2-t
        panel('side-'+str(side),side_len,side_height,sideholes,'y',y,[side_x,wall_bottom],upper)
        x=-L/2 if side<0 else L/2-t
        panel('end-'+str(side),W,side_height,endholes,'x',x,[-W/2,wall_bottom],upper)
        # The bonding perimeter is segmented to leave door/gangway openings free.
        for k,(xx,yy,dx,dy) in enumerate(structure._rectangles(side_len,side_height,sideholes)):
            if abs(yy)<1e-10:
                add(f'bond/side-{side}/floor-{k}',[dx,t,bond],[side_x+xx,y,floor_top],'bond-surface','corner-bonds')
        add(f'bond/side-{side}/roof',[side_len,t,bond],[side_x,y,wall_top],'bond-surface','corner-bonds')
        for end in (-1,1):
            xx=-L/2+t if end<0 else L/2-t-bond
            add(f'bond/side-{side}/end-{end}',[bond,t,side_height],[xx,y,wall_bottom],'bond-surface','corner-bonds')
        add(f'bond/end-{side}/roof',[t,W,bond],[x,-W/2,wall_top],'bond-surface','corner-bonds')
        for edge in (-1,1):
            yy=-W/2 if edge<0 else .65
            add(f'bond/end-{side}/floor-{edge}',[t,W/2-.65,bond],[x,yy,floor_top],'bond-surface','corner-bonds')
    # Eight through-bolts, each with a full-bore crush spacer; two walls drilled.
    bolt_centres={}
    for side in (-1,1):
        for j in range(12):
            x=j-5.5;bolt_centres[side,j]=[[x+dx,side*1.1,sz+dz] for dx in hp['columns_x_m'] for dz in hp['rows_z_m']]
    for side in (-1,1):
        holes=[dict(axis='y',centre_m=c,diameter_m=hp['bolt_hole_m']) for (s,j),cs in bolt_centres.items() if s==side for c in cs]
        tube(f'frame/lower-stringer-{side}',[L,b['stringer_outer_width_m'],b['stringer_outer_depth_m']],[-L/2,side*1.1-b['stringer_outer_width_m']/2,stringer_bottom],0,b['stringer_wall_m'],'gfrp','primary-frame',f'primary-frame/lower-stringer-{side}',holes)
        inner_y=side*(W/2-t)
        ry=inner_y-f['roof_rail_width_m'] if side>0 else inner_y
        tube(f'frame/roof-longitudinal-{side}',[L-2*(t+bond),f['roof_rail_width_m'],f['roof_rail_depth_m']],[side_x,ry,roof_bottom-bond-f['roof_rail_depth_m']],0,f['roof_rail_wall_m'],'gfrp','primary-frame',f'primary-frame/roof-longitudinal-{side}')
    for i in range(b['floor_ribs']):
        x=-L/2+(i+1)*L/(b['floor_ribs']+1)
        tube(f'frame/floor-rib-{i}',[b['rib_width_m'],2.34,b['rib_depth_m']],[x-b['rib_width_m']/2,-1.17,rib_bottom],1,b['rib_wall_m'],'aluminium','primary-frame',f'primary-frame/floor-rib-{i}')
    post_top=roof_bottom-bond-f['roof_rail_depth_m']
    for end in (-1,1):
        x=-L/2+t+bond if end<0 else L/2-t-bond-f['end_frame_width_m']
        for edge in (-1,1):
            y=-W/2+t if edge<0 else W/2-t-f['end_frame_depth_m']
            tube(f'frame/end-{end}-post-{edge}',[f['end_frame_width_m'],f['end_frame_depth_m'],post_top-wall_bottom],[x,y,wall_bottom],2,f['end_frame_wall_m'],'gfrp','primary-frame',f'primary-frame/end-{end}-post-{edge}')
        inner=W/2-t-f['end_frame_depth_m'];z=roof_bottom-bond-f['end_frame_depth_m']
        tube(f'frame/end-{end}-cross-1',[f['end_frame_width_m'],2*inner,f['end_frame_depth_m']],[x,-inner,z],1,f['end_frame_wall_m'],'gfrp','primary-frame',f'primary-frame/end-{end}-cross-1')
        # Preserve the gangway opening: lower stock becomes two independent cuts.
        for edge in (-1,1):
            y=-inner if edge<0 else .65
            tube(f'frame/end-{end}-cross-0/segment-{edge}',[f['end_frame_width_m'],inner-.65,f['end_frame_depth_m']],[x,y,wall_bottom],1,f['end_frame_wall_m'],'gfrp','primary-frame',f'primary-frame/end-{end}-cross-0')
    clear_roof_width=W-2*(t+f['roof_rail_width_m'])
    for i in range(f['roof_crossmembers']):
        x=-L/2+(i+1)*L/(f['roof_crossmembers']+1)
        tube(f'frame/roof-cross-{i}',[f['post_width_m'],clear_roof_width,f['post_depth_m']],[x-f['post_width_m']/2,-clear_roof_width/2,post_top],1,f['post_wall_m'],'gfrp','primary-frame',f'primary-frame/roof-cross-{i}')
    for side in (-1,1):
        y=-W/2+t if side<0 else W/2-t-f['post_depth_m']
        for i,c in enumerate((-7.5,-2.8,2.8,7.5)):
            x=c-f['post_width_m'] if c==-7.5 else c
            tube(f'frame/side-{side}-post-{i}',[f['post_width_m'],f['post_depth_m'],post_top-wall_bottom],[x,y,wall_bottom],2,f['post_wall_m'],'gfrp','primary-frame',f'primary-frame/side-{side}-post-{i}')
        for c in (-4.5,4.5):
            for edge in (-1,1):
                x=c+edge*.7-(f['door_frame_width_m'] if edge<0 else 0)
                tube(f'frame/door-{side}-{c}-post-{edge}',[f['door_frame_width_m'],f['door_frame_depth_m'],2.1-(wall_bottom-floor_top)],[x,y,wall_bottom],2,f['door_frame_wall_m'],'gfrp','primary-frame',f'primary-frame/door-{side}-{c}-post-{edge}')
            for level in (0,1):
                z=floor_bottom-f['door_frame_depth_m'] if level==0 else floor_top+2.1
                hy=-W/2+t if side<0 else W/2-t-f['door_frame_width_m']
                tube(f'frame/door-{side}-{c}-header-{level}',[1.4,f['door_frame_width_m'],f['door_frame_depth_m']],[c-.7,hy,z],0,f['door_frame_wall_m'],'gfrp','primary-frame',f'primary-frame/door-{side}-{c}-header-{level}')
    # Accessible flanged joints attach independent outboard load paths. No member crosses concrete.
    for side in (-1,1):
        collector_y=side*.88-.04
        tube(f'carrier/collector-{side}',[12.,.08,.08],[-6.,collector_y,g['collector_lower_z_m']],0,.006,'steel','magnetic-load-path')
        for j in range(12):
            x=j-5.5;uid=f'hardpoint/{side}/{j:02d}';cs=bolt_centres[side,j]
            def mirrored_y(inner,thickness):return inner if side>0 else -inner-thickness
            plate(uid+'/laminate',[hp['plate_width_m'],.018,.22],[x-hp['plate_width_m']/2,mirrored_y(1.17,.018),sz-.11],'gfrp','hardpoints',cs)
            plate(uid+'/spreader',[hp['plate_width_m'],.012,.22],[x-hp['plate_width_m']/2,mirrored_y(1.188,.012),sz-.11],'aluminium','hardpoints',cs)
            plate(uid+'/carrier-flange',[hp['plate_width_m'],hp['carrier_flange_m'],hp['carrier_flange_height_m']],[x-hp['plate_width_m']/2,mirrored_y(1.2,hp['carrier_flange_m']),sz-hp['carrier_flange_height_m']/2],'aluminium','hardpoints',cs)
            start=1.2+hp['carrier_flange_m'];run=1.4-start
            tube(uid+'/carrier-box',[hp['carrier_width_m'],run,hp['carrier_depth_m']],[x-hp['carrier_width_m']/2,mirrored_y(start,run),sz-hp['carrier_depth_m']/2],1,hp['carrier_wall_m'],'aluminium','hardpoints')
            top=sz+hp['carrier_depth_m']/2
            access=[dict(axis='y',centre_m=c,diameter_m=hp['service_access_bore_m']) for c in cs]
            tube(f'carrier/upright-{side}-{j}',[hp['upright_width_m'],.08,top-g['arm_lower_z_m']],[x-hp['upright_width_m']/2,mirrored_y(1.4,.08),g['arm_lower_z_m']],2,hp['upright_wall_m'],'steel','magnetic-load-path',holes=access)
            tube(f'carrier/cantilever-{side}-{j}',[.12,.64,.16],[x-.06,mirrored_y(.84,.64),g['cantilever_lower_z_m']],1,.012,'steel','magnetic-load-path')
            for k,c in enumerate(cs):
                # Source holes use actual global x/z coordinates; positive-y native cylinders mirror by lower bound.
                cx,_,cz=c;bp=uid+f'/bolt-{k}'
                def cyl(name,diam,run,inner,holes=False):
                    p=add(name,[diam,diam,run],[cx-diam/2,mirrored_y(inner,run),cz-diam/2],'steel','fasteners',kind='cylinder',cylinder_axis='y')
                    if holes:p['holes']=[dict(axis='y',x_m=diam/2,z_m=diam/2,diameter_m=hp['spacer_bore_m'],length_m=run)]
                cyl(bp+'/shank',hp['bolt_diameter_m'],hp['bolt_length_m'],1.027)
                cyl(bp+'/head',.020,hp['bolt_head_m'],1.027-hp['bolt_head_m'])
                cyl(bp+'/washer-in',hp['washer_diameter_m'],hp['washer_m'],1.027,True)
                outer_washer=hp['outer_column_washer_diameter_m'] if abs(cx-x)>hp['carrier_width_m']/2 else hp['washer_diameter_m']
                cyl(bp+'/washer-out',outer_washer,hp['washer_m'],1.2+hp['carrier_flange_m'],True)
                cyl(bp+'/nut',.022,hp['nut_m'],1.2+hp['carrier_flange_m']+hp['washer_m'],True)
                cyl(bp+'/crush-spacer',hp['spacer_outer_diameter_m'],.116,1.042,True)
            interfaces.append(dict(id=uid,normal_axis='y',bolt_count=len(cs),bolt_centres_m=cs,
                stringer_outer_wall_m=b['stringer_wall_m'],tube_bore_crush_spacer_length_m=.116,
                laminate_m=.018,spreader_m=.012,carrier_flange_m=hp['carrier_flange_m'],
                washer_and_socket_access_from='inboard stringer face and outboard carrier via actual32mm upright access bores; no concealed captive nut',
                weld_interfaces=['carrier-flange to tube end','carrier tube to outer upright','upright to lower cantilever','cantilever to longitudinal collector'],
                welding_procedure_qualified=False,tool_and_edge_screen='study.hardpoint_screen'))
    # Native-cleared serial cartridge solids are installed at the retained 24 positions.
    raw=geometry.interface();cartridge_parts=[deepcopy(p) for p in raw['parts'] if p['id'].startswith('cartridge/')]
    for p in cartridge_parts:
        for key in ('volume_m3','density_assumption_kg_m3','modelled_mass_kg','revision','production_released'):p.pop(key,None)
        p['role']='magnetic-envelopes' if p['material']=='winding-envelope' else 'magnetic-cartridges'
        parts.append(p);groups.setdefault(p['role'],[]).append(p['id'])
    # Explicit external corner laps avoid both the inner frame and door openings.
    for level,xs in [('roof',[-7.,-5.,-3.,-1.,1.,3.,5.,7.]),('floor',[-7.8,-2.7,0.,2.7,7.8])]:
        for side in (-1,1):
            for i,x in enumerate(xs):
                outside=W/2;pos=lambda y,w:y if side>0 else -y-w
                if level=='roof':
                    zz=floor_top+H;vbottom=zz-.10;vheight=.104;hbottom=zz+.001;bz=zz
                else:
                    zz=floor_bottom;vbottom=zz-.004;vheight=.104;hbottom=zz-.004;bz=zz-.001
                uid=f'lap/{level}/{side}/{i}'
                add(uid+'/vertical',[.30,.003,vheight],[x-.15,pos(outside+.001,.003),vbottom],'gfrp','corner-laps')
                add(uid+'/horizontal',[.30,.10,.003],[x-.15,pos(outside-.099,.10),hbottom],'gfrp','corner-laps')
                add(uid+'/wall-bond',[.30,.001,.10],[x-.15,pos(outside,.001),zz-.10 if level=='roof' else zz],'bond-surface','corner-laps')
                add(uid+'/face-bond',[.30,.099,.001],[x-.15,pos(outside-.099,.099),bz],'bond-surface','corner-laps')
    # Retained guideway is context only, included in native all-pair checks but excluded from vehicle mass.
    for p in geometry.beam_parts('context/guideway',cfg.civil.span_m):
        p['role']='guideway-context';parts.append(p);groups.setdefault('guideway-context',[]).append(p['id'])
    for p in parts:
        p['volume_m3']=models.volume(p);p['density_assumption_kg_m3']=geometry.MATERIALS[p['material']]
        p['production_released']=False;p['revision']=a['revision']
    if len(parts)!=len({p['id'] for p in parts}):raise ValueError('duplicate assembled material identity')
    old_ids={p['id'] for p in closure.primary_frame_definition()['parts']}
    represented={m['source_member_id'] for m in members if m['source_member_id']}
    if represented!=old_ids:raise ValueError('defined primary stock member coverage differs')
    order=['primary-frame','magnetic-load-path','hardpoints','fasteners','magnetic-cartridges','magnetic-envelopes','panel-floor','panel-side','panel-end','panel-roof','corner-bonds','corner-laps','guideway-context']
    stages=[dict(id=k,parts=groups[k]) for k in order if k in groups]
    return dict(schema=SCHEMA,id='OSR-ASSEMBLED-STRUCTURAL-BODY-CANDIDATE',revision=a['revision'],parts=parts,
        construction_stages=stages,retain_native_tessellation=True,interference_roles=list(groups),
        members=members,interfaces=interfaces,source_primary_stock_count=len(old_ids),installed_primary_member_count=sum(m['source_member_id'] is not None for m in members),
        datums=dict(length_m=L,width_m=W,height_m=H,floor_top_m=floor_top,floor_bottom_m=floor_bottom,roof_bottom_m=roof_bottom,stringer_bottom_m=stringer_bottom,stringer_top_m=stringer_top),
        material_density_assumptions_kg_m3=geometry.MATERIALS,
        envelope_assumptions=dict(car_length_m=L,cabin_width_m=W,arm_width_m=2*g['arm_outer_y_m'],external_corner_lap_width_m=W+.008,external_lap_height_m=H+.008),
        intended_contact_policy='Butt, bonded-lap and bolted interfaces contact surfaces; no intended positive shared material volume is exempted',
        complete_defined_structural_inventory=True,complete_equipped_vehicle=False,accepted_manufacturing_drawings=False,
        omitted=['door leaves/drive/interlocks/glazing/interior/HVAC/battery/wiring/couplers/capture brake equipment',
            'grade-qualified winding/core/guidance/propulsion magnetic circuit; winding volumes are packaging envelopes only',
            'production weld metal/bevel/heat-affected zone, qualified adhesive and laminate process/property cards',
            'legacy128 unlocated joint straps and48 allowance connectors are not inherited as manufactured components; actual visible corner laps are counted instead'],
        holds=['Full body strength/buckling/fatigue/crash and all joined load paths remain unqualified','Actual structural and magnetic material density assumptions require supplier/serial measurements',
            'Carrier-flange bending/prying, welds, upright service-bore shear/net section, tube-wall shear/crush, spacer preload/creep and hot/wet fatigue require independent qualification',
            'Defined structural mass/CG/inertia excludes all omitted equipment and homogenised winding envelopes; no whole-car tare or plant stiffness promotion'],**FLAGS)


def joint_geometry(value=None):
    """Read actual positive-side material/member placements for the force cut."""
    value=definition() if value is None else value;parts={p['id']:p for p in value['parts']};members={p['id']:p for p in value['members']}
    flange=parts['hardpoint/1/00/carrier-flange'];collector=members['carrier/collector-1'];upright=members['carrier/upright-1-0'];stringer=members['frame/lower-stringer-1']
    return dict(loaded_flange_face_y_m=flange['at_m'][1]+flange['size_m'][1],flange_base_y_m=flange['at_m'][1],
        collector_y_m=collector['at_m'][1]+collector['size_m'][1]/2,upright_y_m=upright['at_m'][1]+upright['size_m'][1]/2,stringer_y_m=stringer['at_m'][1]+stringer['size_m'][1]/2,
        cut_scope='Conservative outboard loaded carrier-flange face; no stringer-centre lever credit for bolt-group demand')


def hardpoint_screen(value=None):
    value=definition() if value is None else value;a=load();h=a['hardpoint'];c=closure.load();b=c['body'];m=c['materials']
    demand=h['maximum_gross_car_mass_kg']*9.81*b['normal_load_multiplier']*b['unequal_cartridge_multiplier']/(24-b['failed_cartridges'])
    joint=joint_geometry(value);rows=h['rows_z_m'];pitch=max(rows)-min(rows);per_row=len(h['columns_x_m']);shear=demand/h['bolts'];force_offset=joint['loaded_flange_face_y_m']-joint['collector_y_m'];moment=demand*force_offset
    tension=h['prying_multiplier']*moment/(pitch*per_row)
    cap_s=b['bolt_thread_area_m2']*m['bolt_shear_pa'];cap_t=b['bolt_thread_area_m2']*m['bolt_tension_pa']
    pull=math.pi*h['washer_diameter_m']*b['hardpoint_solid_laminate_m']*m['gfrp_punching_shear_pa']*m['hot_strength_retention']
    wall_pull=math.pi*h['washer_diameter_m']*b['stringer_wall_m']*m['gfrp_punching_shear_pa']*m['hot_strength_retention']
    bearing=shear/(h['bolt_diameter_m']*b['hardpoint_solid_laminate_m']);interaction=math.hypot(shear/cap_s,tension/cap_t)
    plate_height=.22;edge=min(h['plate_width_m']/2-max(map(abs,h['columns_x_m'])),plate_height/2-max(map(abs,rows)))
    edge_required=a['geometry']['minimum_bolt_centre_edge_diameters']*h['bolt_diameter_m']
    washer_clear=min(h['plate_width_m']/2-max(map(abs,h['columns_x_m'])),plate_height/2-max(map(abs,rows)))-h['washer_diameter_m']/2
    innerx=h['carrier_width_m']/2-h['carrier_wall_m'];innerz=h['carrier_depth_m']/2-h['carrier_wall_m']
    socket_clear=min(innerx-max(abs(x) for x in h['columns_x_m'] if abs(x)<h['carrier_width_m']/2)-h['socket_outer_diameter_m']/2,innerz-max(map(abs,rows))-h['socket_outer_diameter_m']/2,
        min(abs(x) for x in h['columns_x_m'] if abs(x)>h['carrier_width_m']/2)-h['carrier_width_m']/2-h['socket_outer_diameter_m']/2)
    spacer_area=math.pi*(h['spacer_outer_diameter_m']**2-h['spacer_bore_m']**2)/4
    preload_assumption_n=12000.;spacer_compression=(preload_assumption_n+tension)/spacer_area
    stringer=closure._tube(b['stringer_outer_width_m'],b['stringer_outer_depth_m'],b['stringer_wall_m'])
    net_at_bolt_column=stringer['area_m2']-2*len(rows)*h['bolt_hole_m']*b['stringer_wall_m']
    nut_end=1.2+h['carrier_flange_m']+h['washer_m']+h['nut_m'];projection=1.027+h['bolt_length_m']-nut_end;required_projection=h['thread_pitch_m']*h['minimum_projection_pitches']
    checks=dict(thread_projection=projection>=required_projection,bolt_interaction=interaction<=1.,laminate_bearing=bearing<=m['gfrp_bearing_pa']*m['hot_strength_retention'],washer_pullthrough=tension<=pull,inboard_tube_wall_pullthrough=tension<=wall_pull,
        edge_distance=edge>=edge_required,washer_access=washer_clear>=0,socket_access=socket_clear>=0,spacer_compression=spacer_compression<=m['steel_allowable_pa'],positive_net_section=net_at_bolt_column>0)
    original_tension=h['prying_multiplier']*moment/(.08*2)
    return dict(car_mass_kg=h['maximum_gross_car_mass_kg'],maximum_interface_force_n=demand,joint_geometry=joint,geometric_force_offset_m=force_offset,retained_old_assumed_force_offset_m=b['hardpoint_force_offset_m'],moment_nm=moment,
        bolt_count=h['bolts'],bolt_axis='y',bolt_length_m=h['bolt_length_m'],projection_beyond_nut_m=projection,required_thread_projection_m=required_projection,bolt_rows_z_m=rows,actual_moment_lever_arm_m=pitch,prying_multiplier=h['prying_multiplier'],shear_per_bolt_n=shear,tension_per_bolt_n=tension,
        bolt_shear_capacity_n=cap_s,bolt_tension_capacity_n=cap_t,interaction_ratio=interaction,pullthrough_capacity_n=pull,inboard_tube_wall_pullthrough_capacity_n=wall_pull,laminate_bearing_pa=bearing,
        minimum_centre_edge_m=edge,required_study_edge_m=edge_required,washer_clearance_m=washer_clear,socket_clearance_m=socket_clear,
        crush_spacer_area_m2=spacer_area,assumed_preload_per_bolt_n=preload_assumption_n,spacer_compression_pa=spacer_compression,
        stringer_gross_area_m2=stringer['area_m2'],stringer_minimum_hole_net_area_m2=net_at_bolt_column,
        checks=checks,analytical_screen_pass=all(checks.values()),qualified_allowables=False,
        rejected_four_bolt_120x80=dict(tension_with_same_prying_n=original_tension,pullthrough_capacity_n=pull,screen_pass=original_tension<=pull,reason='Small moment lever arm and two tension-side bolts fail assumed pull-through; not adopted'),
        old_200x180_pattern=dict(fits_200x120_carrier=False,reason='180mm transverse row pitch exceeds120mm box width; outer centres have no carrier flange/support'),**FLAGS)


def axial_screen():
    c=closure.load();b=c['body'];m=c['materials'];L=structure.body()['envelope_m']['length'];s=closure._tube(b['stringer_outer_width_m'],b['stringer_outer_depth_m'],b['stringer_wall_m'])
    count=b['stringers'];E=m['gfrp_longitudinal_e_pa'];area=s['area_m2'];K=count*E*area/L
    # Two half-body axial paths plus coupler are one full car-length contribution.
    joint=c['coupler']['target_stiffness_n_m'];series=1/(1/K+1/joint)
    hp=load()['hardpoint'];radius=hp['bolt_hole_m']/2;n=1000;dx=2*radius/n
    def inverse_area(x):
        removed=2*len(hp['rows_z_m'])*b['stringer_wall_m']*2*math.sqrt(max(0.,radius*radius-x*x))
        return 1/(area-removed)
    integral=dx/3*(inverse_area(-radius)+inverse_area(radius)+math.fsum((4 if i%2 else 2)*inverse_area(-radius+i*dx) for i in range(1,n)))
    sites=12*len(hp['columns_x_m']);compliance=((L-sites*2*radius)/area+sites*integral)/(count*E)
    perforated=1/compliance;perforated_series=1/(compliance+1/joint)
    return dict(assumed_longitudinal_E_pa=E,stringers=count,gross_area_per_stringer_m2=area,length_m=L,
        gross_body_axial_stiffness_n_m=K,body_axial_compliance_m_n=1/K,
        assumed_coupler_stiffness_n_m=joint,body_and_coupler_series_stiffness_n_m=series,
        series_to_current_coupler_only_ratio=series/joint,
        drilled_body_axial_stiffness_n_m=perforated,drilled_body_axial_compliance_m_n=compliance,drilled_body_and_coupler_series_stiffness_n_m=perforated_series,
        hole_compliance_model='Axial compliance integral1/(E A(x)) through both actual drilled walls; circular chord removal,1000-step Simpson rule per hole site. Uniform load sharing/orthotropic E remains assumed.',definition='Two half-car end load paths (one full car-length) in series with the100MN/m coupler; only two longitudinal tubes credited',
        body_under_100kn_extension_m=100000/K,series_under_100kn_extension_m=100000/series,
        stiffness_is_upper_bound=True,missing=['actual joined node/coupler-hardpoint compliance','drilled net sections and composite orthotropy','shell participation, shear-lag and flexural coupling','measured end load introduction/creep/hot-wet properties'],
        plant_stiffness_promoted=False,**FLAGS)


def carrier_load_path_screen():
    """Fresh free-body/section screens of the counted outboard load path."""
    h=load()['hardpoint'];c=closure.load();m=c['materials'];force=hardpoint_screen()['maximum_interface_force_n']
    joint=joint_geometry();collector_y=joint['collector_y_m'];upright_y=joint['upright_y_m'];stringer_y=joint['stringer_y_m'];cut_y=joint['loaded_flange_face_y_m']
    lower_arm=upright_y-collector_y;upper_arm=upright_y-cut_y
    joint_couple=force*(cut_y-collector_y)
    # Cut at the actual loaded carrier-flange face: F*upper_arm plus joint couple equals the
    # lower cantilever moment. This checks the moment path instead of omitting it.
    moment=force*lower_arm
    equilibrium_error=moment-(force*upper_arm+joint_couple)
    arm=closure._tube(.12,.16,.012);upright=closure._tube(h['upright_width_m'],.08,h['upright_wall_m'])
    arm_stress=moment/(arm['vertical_inertia_m4']/(.16/2))
    arm_deflection=force*lower_arm**3/(3*m['steel_young_pa']*arm['vertical_inertia_m4'])
    # Service bores remove material from both y walls at every actual column.
    removed_width=len(h['columns_x_m'])*h['service_access_bore_m'];wall=h['upright_wall_m']
    removed_area=2*wall*removed_width
    removed_I=2*removed_width*((.08/2)**3-(.08/2-wall)**3)/3
    net_area=upright['area_m2']-removed_area;net_I=upright['vertical_inertia_m4']-removed_I
    upright_stress=moment/(net_I/(.08/2))+force/net_area
    carrier=closure._tube(h['carrier_width_m'],h['carrier_depth_m'],h['carrier_wall_m'])
    carrier_stress=force*upper_arm/(carrier['vertical_inertia_m4']/(h['carrier_depth_m']/2))
    bolt_tension=hardpoint_screen()['tension_per_bolt_n'];plate_outstand=max(h['columns_x_m'])-h['carrier_width_m']/2
    strip_width=min(y-x for x,y in zip(h['columns_x_m'],h['columns_x_m'][1:]));flange_stress=bolt_tension*plate_outstand/(strip_width*h['carrier_flange_m']**2/6)
    thin=closure._tube(.10,.08,.006);thin_stress=moment/(thin['vertical_inertia_m4']/.04)
    thin_flange_stress=bolt_tension*plate_outstand/(strip_width*.012**2/6)
    checks=dict(moment_equilibrium=abs(equilibrium_error)<1e-8,cantilever_bending=arm_stress<=m['steel_allowable_pa'],
        upright_net_bending_and_axial=upright_stress<=m['steel_allowable_pa'],carrier_bending=carrier_stress<=m['aluminium_allowable_pa'],flange_strip_bending=flange_stress<=m['aluminium_allowable_pa'])
    return dict(interface_force_n=force,collector_y_m=collector_y,upright_y_m=upright_y,stringer_y_m=stringer_y,loaded_joint_cut_y_m=cut_y,
        lower_arm_m=lower_arm,upper_arm_m=upper_arm,body_joint_couple_nm=joint_couple,lower_cantilever_moment_nm=moment,moment_equilibrium_residual_nm=equilibrium_error,
        cantilever_section_m=[.12,.16,.012],cantilever_bending_stress_pa=arm_stress,cantilever_tip_deflection_m=arm_deflection,
        upright_section_m=[h['upright_width_m'],.08,h['upright_wall_m']],upright_service_bore_net_area_m2=net_area,upright_service_bore_net_I_m4=net_I,upright_bending_plus_axial_stress_pa=upright_stress,
        carrier_bending_stress_pa=carrier_stress,flange_outstand_m=plate_outstand,flange_effective_strip_width_m=strip_width,flange_strip_bending_stress_pa=flange_stress,
        rejected_thin_100x80x6_arm=dict(stress_pa=thin_stress,allowable_assumption_pa=m['steel_allowable_pa'],screen_pass=thin_stress<=m['steel_allowable_pa']),
        rejected_12mm_flange=dict(stress_pa=thin_flange_stress,allowable_assumption_pa=m['aluminium_allowable_pa'],screen_pass=thin_flange_stress<=m['aluminium_allowable_pa']),
        checks=checks,analytical_screen_pass=all(checks.values()),qualified_properties=False,
        unverified=['weld and flange stiffness/prying correlation','local plate instability and shear/torsion','service-bore stress concentration and fatigue','rail-capture and all magnetic normal/thrust reactions','full body and guideway dynamic coupling'],**FLAGS)


def study():
    value=definition();a=load();legacy=json.loads(LEGACY.read_text());src=sources()
    return dict(schema=SCHEMA,revision=a['revision'],source_sha256=src,configuration_revision=configuration.selected().revision,
        definition_sha256=sha256(encoded(value)).hexdigest(),part_count=len(value['parts']),source_primary_stock_count=value['source_primary_stock_count'],
        installed_primary_member_count=value['installed_primary_member_count'],member_cut_list=value['members'],mesh_verification=mesh_control(),hardpoint_screen=hardpoint_screen(value),carrier_load_path_screen=carrier_load_path_screen(),axial_screen=axial_screen(),
        tolerance_budget=[dict(term=term,allocated_m=nom,qualified=False) for term,nom in [('bolt_diametral_clearance',a['hardpoint']['bolt_hole_m']-a['hardpoint']['bolt_diameter_m']),('panel_corner_bond_target',a['geometry']['panel_corner_bond_m']),('rail_to_outboard_upright_nominal',.04)]]+
            [dict(term=term,allocated_m=None,qualified=False) for term in ['pultruded wall and fibre placement','cure shrinkage and thermal expansion','hole positional/squareness','beam twist/rail erection','joint slip and deformation','body/track dynamic gaps']],
        interfaces=value['interfaces'],defined_structural_inventory_modelled=True,complete_equipped_vehicle=False,default_mass_or_stiffness_changed=False,
        rejected_twelve_bolt_candidate=dict(fixture_sha256=digest(REJECTED_FLANGE),definition_sha256=json.loads(REJECTED_FLANGE.read_text())['definition_sha256'],tension_per_bolt_n=json.loads(REJECTED_FLANGE.read_text())['tension_per_bolt_n'],inboard_wall_pullthrough_capacity_n=json.loads(REJECTED_FLANGE.read_text())['inboard_wall_pullthrough_capacity_n'],eligible_for_assembled_adoption=False),
        rejected_eight_bolt_candidate=dict(fixture_sha256=digest(REJECTED),definition_sha256=json.loads(REJECTED.read_text())['definition_sha256'],tension_per_bolt_n=json.loads(REJECTED.read_text())['tension_per_bolt_n'],inboard_wall_pullthrough_capacity_n=json.loads(REJECTED.read_text())['inboard_wall_pullthrough_capacity_n'],eligible_for_assembled_adoption=False),
        legacy_negative_control=dict(definition_sha256=legacy['definition_sha256'],historical_native_manifest_sha256=legacy['historical_native_manifest_sha256'],
            part_ids=[p['id'] for p in legacy['definition']['parts'] if p['id'].startswith('frame/lower-crosshead-')],
            exact_configuration_revision=legacy['captured_configuration_revision'],eligible_for_assembled_adoption=False,
            reason='Full-width lower crossheads pass through deep concrete beam; actual native common volumes are retained in legacy-collision-control.json'),
        holds=value['holds'],omitted=value['omitted'],**FLAGS)


def _native_shape(p,App,Part):
    size=[x*1000 for x in p['size_m']];at=[x*1000 for x in p['at_m']]
    shape=Part.makeBox(*size,App.Vector(*at))
    if p['kind']=='tube':
        inner=size.copy();start=at.copy()
        for i in range(3):
            if i!=p['axis']:inner[i]-=2*p['wall_m']*1000;start[i]+=p['wall_m']*1000
        shape=shape.cut(Part.makeBox(*inner,App.Vector(*start)))
    return shape


def socket_paths(value=None):
    """Exact finite nominal insertion sweeps; mirrored on the two body sides."""
    value=definition() if value is None else value;hp=load()['hardpoint'];paths=[]
    nut_end=1.2+hp['carrier_flange_m']+hp['washer_m']+hp['nut_m']
    for interface in value['interfaces']:
        side=int(interface['id'].split('/')[1])
        for index,c in enumerate(interface['bolt_centres_m']):
            for direction,lo,hi in [('outboard',nut_end+.0001,1.51),('inboard',.70,1.027-hp['bolt_head_m']-.0001)]:
                start=lo if side>0 else -hi
                paths.append(dict(interface=interface['id'],bolt_index=index,direction=direction,axis='y',start_m=[c[0],start,c[2]],start_y_m=start,length_m=hi-lo,
                    outer_diameter_m=hp['socket_outer_diameter_m'],inner_diameter_m=.014 if direction=='outboard' else 0.))
    return paths


def native_export(model_path,output):
    """Run inside FreeCAD: reuse the maintained exporter, then independently inspect reopened solids."""
    import FreeCAD as App
    import Part
    output=Path(output);model_path=Path(model_path);value=json.loads(model_path.read_text());settings=load();positive_limit=settings['geometry']['positive_intersection_limit_mm3']
    native.export_native(model_path,output)
    # A translated unit cube independently establishes inertia units and centre convention.
    cube=Part.makeBox(1000,1000,1000,App.Vector(3000,4000,5000))
    control=cube.MatrixOfInertia
    if not math.isclose(control.A11/1e15,1/6,rel_tol=1e-10) or not math.isclose(control.A22/1e15,1/6,rel_tol=1e-10):
        raise ValueError('native inertia control: SI conversion or centroid convention differs')
    doc=App.openDocument(str(output/'model.FCStd'));byid={o.DesignId:o for o in doc.Objects if 'DesignId' in o.PropertiesList}
    regions=[];native_shapes={};validity={}
    for p in value['parts']:
        obj=byid[p['id']];shape=obj.Shape;native_shapes[p['id']]=shape;solids=shape.Solids;V=shape.Volume/1e9
        validity[p['id']]=shape.isValid() and bool(solids)
        if not validity[p['id']]:raise ValueError('reopened assembled material shape invalid: '+p['id'])
        cv=[math.fsum(s.Volume*tuple(s.CenterOfMass)[i] for s in solids)/shape.Volume/1000 for i in range(3)]
        central=[[0.]*3 for _ in range(3)]
        for solid in solids:
            centre=[x/1000 for x in tuple(solid.CenterOfMass)];delta=[centre[i]-cv[i] for i in range(3)];rr=sum(x*x for x in delta);matrix=solid.MatrixOfInertia
            for i in range(3):
                for j in range(3):central[i][j]+=getattr(matrix,'A'+str(i+1)+str(j+1))/1e15+solid.Volume/1e9*((rr if i==j else 0)-delta[i]*delta[j])
        density=p['density_assumption_kg_m3'];included=p['role'] not in {'guideway-context','magnetic-envelopes'}
        regions.append(dict(id=p['id'],material=p['material'],role=p['role'],volume_m3=shape.Volume/1e9,
            density_assumption_kg_m3=density,included_in_defined_vehicle_material_mass=included,
            mass_kg=shape.Volume/1e9*density if included else None,
            centre_of_volume_m=cv,
            inertia_at_region_centroid_kg_m2=[[central[i][j]*density for j in range(3)] for i in range(3)] if included else None))
    selected=[r for r in regions if r['included_in_defined_vehicle_material_mass']]
    mass=math.fsum(r['mass_kg'] for r in selected);cg=[math.fsum(r['mass_kg']*r['centre_of_volume_m'][i] for r in selected)/mass for i in range(3)]
    inertia=[[0.]*3 for _ in range(3)]
    for r in selected:
        delta=[r['centre_of_volume_m'][i]-cg[i] for i in range(3)];rr=math.fsum(x*x for x in delta)
        for i in range(3):
            for j in range(3):inertia[i][j]+=r['inertia_at_region_centroid_kg_m2'][i][j]+r['mass_kg']*((rr if i==j else 0)-delta[i]*delta[j])
    cfg=configuration.selected();pitch=cfg.formation.body_length_m+cfg.formation.coupling_gap_assumption_m
    centres=[(i-(cfg.formation.cars-1)/2)*pitch for i in range(cfg.formation.cars)]
    sixI=[[cfg.formation.cars*inertia[i][j]+(mass*math.fsum(x*x for x in centres) if i==j and i in (1,2) else 0) for j in range(3)] for i in range(3)]
    material_totals={}
    for r in selected:material_totals[r['material']]=material_totals.get(r['material'],0)+r['mass_kg']
    result=dict(schema='osr-native-assembled-mass-properties/1',definition_sha256=digest(model_path),
        calculation='Reopened OpenCascade solid volumes, centroids and centroid inertia; material density assumptions and exact parallel-axis sums',
        native_inertia_unit_control=dict(translated_unit_cube_volume_m3=cube.Volume/1e9,centroid_m=[x/1000 for x in tuple(cube.CenterOfMass)],centroid_Ixx_m5=control.A11/1e15,expected_Ixx_m5=1/6,passed=True),
        regions=regions,part_count=len(regions),included_region_count=len(selected),
        defined_vehicle_material_mass_kg=mass,defined_vehicle_material_cg_m=cg,defined_vehicle_material_inertia_kg_m2=inertia,material_mass_kg=material_totals,
        density_assumptions_are_measured=False,whole_equipped_vehicle_mass_kg=None,
        excluded_context_volume_m3=math.fsum(r['volume_m3'] for r in regions if r['role']=='guideway-context'),
        excluded_winding_envelope_volume_m3=math.fsum(r['volume_m3'] for r in regions if r['role']=='magnetic-envelopes'),
        six_car_repetition=dict(cars=cfg.formation.cars,pitch_m=pitch,body_centres_x_m=centres,
            instanced_defined_vehicle_mass_kg=cfg.formation.cars*mass,instanced_cg_m=cg,instanced_inertia_kg_m2=sixI,
            repetition_is_identical_structural_units=True,coupler_gangway_and_equipment_mass_included=False),**FLAGS)
    (output/'mass-properties.json').write_bytes(encoded(result));App.closeDocument(doc.Name)
    cad=json.loads((output/'native-cad.json').read_text())
    for p in cad['parts']:p['valid']=validity[p['id']]
    cad['assembled_inspector_sha256']=digest(__file__)
    (output/'native-cad.json').write_bytes(encoded(cad))
    paths=[];tool_failures=[]
    for spec in socket_paths(value):
        outer=Part.makeCylinder(spec['outer_diameter_m']*500,spec['length_m']*1000,App.Vector(*(x*1000 for x in spec['start_m'])),App.Vector(0,1,0))
        tool=outer
        if spec['inner_diameter_m']:
            bore=Part.makeCylinder(spec['inner_diameter_m']*500,spec['length_m']*1000,App.Vector(*(x*1000 for x in spec['start_m'])),App.Vector(0,1,0))
            tool=outer.cut(bore)
        checked=0
        for pid,shape in native_shapes.items():
            if tool.BoundBox.intersect(shape.BoundBox):
                checked+=1;common=tool.common(shape).Volume
                if common>positive_limit:
                    tool_failures.append(dict(interface=spec['interface'],bolt_index=spec['bolt_index'],direction=spec['direction'],part_id=pid,common_volume_mm3=common))
        paths.append(dict(spec,nearby_solids_checked=checked))
    access=dict(schema='osr-native-socket-insertion/1',definition_sha256=digest(model_path),path_count=len(paths),paths=paths,
        failures=tool_failures,actual_native_common_checks_executed=True,nominal_socket_insertion_clear=not tool_failures,
        unverified=['wrench swing and torque reaction','hand access and nut starting','weld metal/build distortion','positional tolerances and manufacturing capability'],**FLAGS)
    (output/'tool-access.json').write_bytes(encoded(access))
    if tool_failures:raise ValueError('Actual socket insertion interference: '+str(tool_failures[:10]))
    old=json.loads(LEGACY.read_text());legacy=old['definition']['parts']
    beams=[p for p in legacy if p['material']=='concrete'];heads=[p for p in legacy if p['id'].startswith('frame/lower-crosshead-')]
    collisions=[]
    for head in heads:
        hs=_native_shape(head,App,Part)
        for beam in beams:
            bs=_native_shape(beam,App,Part)
            if hs.BoundBox.intersect(bs.BoundBox):
                overlap=hs.common(bs).Volume
                if overlap>positive_limit:
                    collisions.append(dict(left=head['id'],right=beam['id'],common_volume_mm3=overlap))
    if len(heads)!=2 or not collisions:raise ValueError('legacy full-width crosshead control must fail actual native common-volume test')
    failure=dict(schema='osr-native-legacy-crosshead-control/1',legacy_definition_sha256=old['definition_sha256'],historical_native_manifest_sha256=old['historical_native_manifest_sha256'],
        retained_fixture_sha256=digest(LEGACY),configuration_revision=old['captured_configuration_revision'],
        evaluated_part_ids=[p['id'] for p in heads],collisions=collisions,total_common_volume_mm3=math.fsum(c['common_volume_mm3'] for c in collisions),
        native_common_volume_executed=True,expected_failure_observed=True,eligible_for_assembled_adoption=False,
        disqualification_scope='Only this exact retained full-width crosshead geometry on this retained2.5m-deep beam; no inference against every ferrite maglev candidate',**FLAGS)
    (output/'legacy-collision-control.json').write_bytes(encoded(failure))


def _generate(model_path,output):
    work=ROOT/'build/assembled-body-native';work.mkdir(parents=True,exist_ok=True);script=work/'generate.py';ok=work/'completed';ok.unlink(missing_ok=True)
    script.write_text('import sys\nfrom pathlib import Path\nsys.path[:0]='+repr([str(ROOT)])+'\nfrom engineering.ferrite_maglev.assembled_body import native_export\nnative_export('+repr(str(Path(model_path).resolve()))+','+repr(str(Path(output).resolve()))+')\nPath('+repr(str(ok))+').write_text("complete")\n')
    binary=shutil.which('FreeCADCmd') or shutil.which('freecadcmd')
    command=[binary] if binary else ['flatpak','run','--filesystem='+str(ROOT),'--command=FreeCADCmd','org.freecad.FreeCAD']
    with (work/'freecad.log').open('w') as log:
        subprocess.run([*command,str(script)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1800,check=True)
    if not ok.is_file():raise RuntimeError('Native assembly incomplete; inspect '+str(work/'freecad.log'))


def sections_svg(value):
    d=value['datums'];h=load()['hardpoint'];s=hardpoint_screen(value);scale=110
    lines=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="760" viewBox="0 0 1200 760">','<rect width="1200" height="760" fill="#f4f7fa"/>','<g font-family="sans-serif" fill="#15334c">',
        '<text x="30" y="35" font-size="24">Assembled structural candidate — dimensioned sections</text>',
        '<text x="30" y="65" font-size="15">Unqualified material regions and interfaces; not a manufacturing drawing or whole equipped car</text>']
    # Actual y/z cross section through cartridge/arm location; coordinates in metres.
    yz=[]
    for p in value['parts']:
        if p['kind']=='box' and p['at_m'][0]-.0001<=.5<=p['at_m'][0]+p['size_m'][0]+.0001:
            y,z=p['at_m'][1:];sy,sz=p['size_m'][1:]
            colour={'concrete':'#abb7bf','steel':'#647f99','gfrp':'#15998a','aluminium':'#8cabc2','ferrite':'#d37b58','core-80':'#d6bd74','core-100':'#bda166','bond-surface':'#ba8a9b','winding-envelope':'#dfb747'}[p['material']]
            yz.append(f'<rect x="{300+y*scale:.3f}" y="{430-(z+sz)*scale:.3f}" width="{sy*scale:.3f}" height="{sz*scale:.3f}" fill="{colour}" stroke="#294556" stroke-width=".25"/>')
    lines+=yz
    labels=[f'Cabin width {d["width_m"]:.3f}m; rail-clear arm width2.960m',f'Floor datum z={d["floor_top_m"]:.4f}m; floor underside={d["floor_bottom_m"]:.4f}m',f'Stringer z={d["stringer_bottom_m"]:.4f}..{d["stringer_top_m"]:.4f}m',
        f'{h["bolts"]}×M12 bolts per interface; rows z={h["rows_z_m"]}m',f'Columns x={h["columns_x_m"]}m; bolt length{h["bolt_length_m"]*1000:g}mm',f'Bore spacer OD25/ID13 ×116mm; holes{h["bolt_hole_m"]*1000:g}mm',f'Laminate18 + spreader12 + carrier flange{h["carrier_flange_m"]*1000:g}mm',f'Carrier tube{h["carrier_width_m"]*1000:g}×{h["carrier_depth_m"]*1000:g}×{h["carrier_wall_m"]*1000:g}mm; length{(1.4-1.2-h["carrier_flange_m"])*1000:g}mm',f'Socket clearance{s["socket_clearance_m"]*1000:.1f}mm; thread projection{s["projection_beyond_nut_m"]*1000:g}mm',f'Assumed{h["maximum_gross_car_mass_kg"]/1000:g}t AW3 force/interface{s["maximum_interface_force_n"]:,.1f}N',f'Prying factor{h["prying_multiplier"]:g}, bolt interaction{s["interaction_ratio"]:.3f}',
        'Final positive shared-volume exemptions: NONE', 'All surfaces/holes/joints are source-revision bound.', 'Full fatigue/crash/weld/adhesive/force/thermal qualification remains open.']
    for i,label in enumerate(labels):lines.append(f'<text x="610" y="{110+i*31}" font-size="15">{label}</text>')
    lines+=['<text x="25" y="735" font-size="14">View at x=0.5m. Context beam is not vehicle mass. Winding windows are unqualified packaging volumes.</text>','</g></svg>']
    return '\n'.join(lines)+'\n'


def display_surface(part,segments=8):
    """Display envelope only: subpixel through-bores are deliberately omitted."""
    lo=part['at_m'];size=models.global_size(part)
    if part['kind']=='box':
        vertices=[[lo[0]+x*size[0],lo[1]+y*size[1],lo[2]+z*size[2]] for z in (0,1) for y in (0,1) for x in (0,1)]
        triangles=[[0,2,3],[0,3,1],[4,5,7],[4,7,6],[0,1,5],[0,5,4],[2,6,7],[2,7,3],[0,4,6],[0,6,2],[1,3,7],[1,7,5]]
    elif part['kind']=='cylinder':
        axis='xyz'.index(part.get('cylinder_axis','z'));u=(axis+1)%3;v=(axis+2)%3;vertices=[]
        for end in (0,1):
            for i in range(segments):
                p=[lo[j]+size[j]/2 for j in range(3)];p[axis]=lo[axis]+end*size[axis];p[u]+=size[u]/2*math.cos(2*math.pi*i/segments);p[v]+=size[v]/2*math.sin(2*math.pi*i/segments);vertices.append(p)
        triangles=[]
        for i in range(1,segments-1):triangles.extend([[0,i+1,i],[segments,segments+i,segments+i+1]])
        for i in range(segments):
            j=(i+1)%segments;triangles.extend([[i,j,segments+j],[i,segments+j,segments+i]])
    else:raise ValueError('Unsupported display primitive')
    return dict(id=part['id'],material=part['material'],vertices_m=vertices,triangles=triangles)


def display_lod_receipt(value,mesh):
    visible=[p for p in value['parts'] if p['role']!='guideway-context']
    return dict(schema='osr-assembled-display-lod/1',cylinder_segments=8,
        native_triangle_count=sum(len(p['triangles']) for p in mesh['parts']),
        display_triangle_count=sum(12 if p['kind']=='box' else 28 for p in visible),represented_material_region_count=len(visible),
        native_geometry_unchanged=True,display_mesh_is_acceptance_evidence=False,
        omitted_display_features='Small through-bores, annular bores and subpixel surface detail; cylinders use8display facets',
        source='Exact primitive placements and external bounds checked against reopened native-solid receipts; full native geometry remains downloadable and verified')


def render(output):
    """Animate explicitly simplified native-verified display envelopes only."""
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    import numpy as np
    output=Path(output);mesh=json.loads(gzip.decompress((output/'native-mesh.json.gz').read_bytes()));value=json.loads((output/'definition.json').read_text());byid={p['id']:p for p in mesh['parts']}
    native_receipt=json.loads((output/'native-cad.json').read_text());solid_bounds={p['id']:p['bounds_m'] for p in native_receipt['parts']}
    roles={p['id']:p['role'] for p in value['parts']};colours={'concrete':'#b6c0c8','steel':'#526f8c','gfrp':'#179b8c','aluminium':'#a9bdcb','ferrite':'#d47b58','core-80':'#d9c482','core-100':'#bea566','bond-surface':'#bd8ea0','winding-envelope':'#d9af3f'}
    body=[display_surface(p) for p in value['parts'] if p['role']!='guideway-context'];lod=display_lod_receipt(value,mesh)
    for p in body:
        actual=solid_bounds[p['id']];display=np.array(p['vertices_m'])
        if not np.allclose(actual[:3],display.min(0),rtol=0,atol=1e-8) or not np.allclose(actual[3:],display.max(0),rtol=0,atol=1e-8):raise ValueError('display LOD may not change native envelope placement')
    bounds=np.array([v for p in body for v in p['vertices_m']]);lo=bounds.min(0);hi=bounds.max(0)
    def image(path,caption,visible,offsets=None,six=False,cutaway=False):
        fig=plt.figure(figsize=(12,6.75),dpi=100,facecolor='#f3f7fa');ax=fig.add_subplot(projection='3d');ax.set_facecolor('#f3f7fa');offsets=offsets or {};centres=[0.]
        if six:centres=[(i-2.5)*(17+configuration.selected().formation.coupling_gap_assumption_m) for i in range(6)]
        face_groups={}
        for centre in centres:
            for p in body:
                if p['id'] not in visible:continue
                if cutaway and roles[p['id']] in {'panel-floor','panel-roof','panel-side','panel-end','corner-laps','corner-bonds'}:continue
                vertices=np.array(p['vertices_m'])+np.array(offsets.get(p['id'],[0.,0.,0.]))+np.array([centre,0.,0.])
                face_groups.setdefault(p['material'],[]).extend(vertices[np.array(p['triangles'])])
        for mat,faces in face_groups.items():
            ax.add_collection3d(Poly3DCollection(faces,facecolors=colours[mat],edgecolors='#23445b',linewidths=.025,alpha=1))
        actual_lo=lo+np.array([min(centres),0,0]);actual_hi=hi+np.array([max(centres),0,0])
        if offsets:actual_lo-=.8;actual_hi+=.8
        span=actual_hi-actual_lo;mid=(actual_hi+actual_lo)/2
        for setter,i in [(ax.set_xlim,0),(ax.set_ylim,1),(ax.set_zlim,2)]:setter(mid[i]-span[i]*.55,mid[i]+span[i]*.55)
        ax.set_box_aspect(span,zoom=1.02);ax.view_init(elev=18,azim=-65);ax.set_axis_off()
        fig.suptitle(caption,fontsize=15);fig.text(.025,.055,'Display LOD: native-verified primitive envelopes; small bores and surface details omitted. Full native geometry retained.',fontsize=10)
        fig.text(.025,.025,'Installation offsets illustrate sequence; no path collision, lifting, tooling or construction-stage acceptance.',fontsize=10)
        fig.subplots_adjust(left=0,right=1,bottom=.08,top=.92);fig.savefig(path,metadata={'Software':'OpenSourceRail assembled native geometry'});plt.close(fig)
    ids=set(byid);image(output/'overview.png','Joined structural body and 24 cartridge material assemblies (display LOD)',ids)
    image(output/'frame-cutaway.png','Joined frame, drilled hardpoints and outboard magnetic load paths',ids,cutaway=True)
    image(output/'six-car.png','Six repeated structural units — omitted equipment and couplers remain open',ids,six=True)
    frames=[];stages=[s for s in value['construction_stages'] if s['id']!='guideway-context'];visible=set();n=load()['render']['frames_per_stage'];fps=load()['render']['frames_per_second']
    with tempfile.TemporaryDirectory(prefix='osr-assembled-movie-') as tmp:
        for stage in stages:
            incoming=set(stage['parts']);group=stage['id'];direction=[0.,0.,.5]
            if group=='panel-side':direction=[0.,.55,0.]
            elif group=='panel-end':direction=[.7,0.,0.]
            elif group in {'magnetic-cartridges','magnetic-envelopes'}:direction=[0.,.6,-.3]
            for frame in range(n):
                alpha=1-frame/(n-1);offsets={pid:[alpha*x for x in direction] for pid in incoming}
                path=Path(tmp)/f'{len(frames):04d}.png';image(path,'Illustrative assembly: '+group,visible|incoming,offsets);frames.append(path)
            visible|=incoming
        subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(fps),'-i',str(Path(tmp)/'%04d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-vf','pad=ceil(iw/2)*2:ceil(ih/2)*2,fps=24','-movflags','+faststart',str(output/'assembly-visibility.mp4')],check=True,timeout=180)
    names=['overview.png','frame-cutaway.png','six-car.png','assembly-visibility.mp4']
    receipt=dict(schema='osr-assembled-body-visuals/1',definition_sha256=digest(output/'definition.json'),mesh_sha256=digest(output/'native-mesh.json.gz'),renderer_sha256=digest(__file__),
        stages=stages,frames_per_stage=n,source_frames_per_second=fps,source_frame_count=len(frames),display_lod=lod,
        moving_offsets_are_measured_assembly_trajectories=False,path_collision_verification=False,
        scope='Illustrative translations of display-only primitive envelopes verified against exact native placements; small bores/details are omitted and cylinders simplified. Full native interference checks do not verify assembly motion',
        files_sha256={name:digest(output/name) for name in names},**FLAGS)
    (output/'visual-receipt.json').write_bytes(encoded(receipt))


def _primitive_properties(p):
    """Independent signed primitive integrals for checks on actual native output."""
    axis='xyz'.index(p.get('cylinder_axis','z'));size=models.global_size(p);at=p['at_m']
    def box(sz,pos):
        v=math.prod(sz);centre=[pos[i]+sz[i]/2 for i in range(3)]
        I=[[v*sum(sz[k]**2 for k in range(3) if k!=i)/12 if i==j else 0. for j in range(3)] for i in range(3)]
        return v,centre,I
    def cylinder(diameter,run,pos,idx):
        v=math.pi*(diameter/2)**2*run;centre=list(pos);centre[idx]+=run/2
        I=[[v*(diameter**2/8 if i==idx else (3*diameter**2/4+run**2)/12) if i==j else 0. for j in range(3)] for i in range(3)]
        return v,centre,I
    if p['kind']=='cylinder':
        origin=[at[i] if i==axis else at[i]+p['size_m'][0]/2 for i in range(3)]
        pieces=[(1,cylinder(p['size_m'][0],p['size_m'][2],origin,axis))]
    elif p['kind']=='box':pieces=[(1,box(size,at))]
    else:raise ValueError('assembled regions must be independent boxes/cylinders')
    for h in p.get('holes',[]):
        idx='xyz'.index(h.get('axis','z'));pos=[at[i]+(h.get('start_m',0) if i==idx else h['xyz'[i]+'_m']) for i in range(3)]
        pieces.append((-1,cylinder(h['diameter_m'],h.get('length_m',p['size_m'][idx]),pos,idx)))
    V=math.fsum(s*x[0] for s,x in pieces);centre=[math.fsum(s*x[0]*x[1][i] for s,x in pieces)/V for i in range(3)]
    I=[[0.]*3 for _ in range(3)]
    for sign,(vol,c,local) in pieces:
        delta=[c[i]-centre[i] for i in range(3)];rr=sum(x*x for x in delta)
        for i in range(3):
            for j in range(3):I[i][j]+=sign*(local[i][j]+vol*((rr if i==j else 0)-delta[i]*delta[j]))
    return V,centre,I


def _mass_check(value,mass):
    if (mass.get('schema')!='osr-native-assembled-mass-properties/1' or mass.get('definition_sha256')!=sha256(encoded(value)).hexdigest()
            or len(mass.get('regions',[]))!=len(value['parts']) or mass.get('whole_equipped_vehicle_mass_kg') is not None
            or mass.get('density_assumptions_are_measured') is not False):raise ValueError('native material property identity differs')
    selected=[]
    for p,r in zip(value['parts'],mass['regions']):
        V,c,I=_primitive_properties(p);rho=p['density_assumption_kg_m3'];included=p['role'] not in {'guideway-context','magnetic-envelopes'}
        if (r.get('id')!=p['id'] or r.get('material')!=p['material'] or r.get('role')!=p['role']
                or r.get('density_assumption_kg_m3')!=rho or r.get('included_in_defined_vehicle_material_mass') is not included
                or not math.isclose(r.get('volume_m3',-1),V,rel_tol=1e-7,abs_tol=1e-12)
                or len(r.get('centre_of_volume_m',[]))!=3 or any(type(x) not in (int,float) or not math.isfinite(x) or abs(x-y)>1e-8 for x,y in zip(r['centre_of_volume_m'],c))):raise ValueError('native centroid/material volume differs')
        if included:
            matrix=r.get('inertia_at_region_centroid_kg_m2')
            if not isinstance(matrix,list) or len(matrix)!=3 or any(not isinstance(row,list) or len(row)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in row) for row in matrix):raise ValueError('finite native inertia tensor required')
            if not math.isclose(r['mass_kg'],V*rho,rel_tol=1e-7):raise ValueError('native density mass differs')
            if any(not math.isclose(r['inertia_at_region_centroid_kg_m2'][i][j],I[i][j]*rho,rel_tol=1e-6,abs_tol=1e-8) for i in range(3) for j in range(3)):
                raise ValueError('native independent inertia integral differs')
            selected.append(r)
        elif r.get('mass_kg') is not None or r.get('inertia_at_region_centroid_kg_m2') is not None:raise ValueError('context/envelope mass may not become vehicle mass')
    total=math.fsum(r['mass_kg'] for r in selected);cg=[math.fsum(r['mass_kg']*r['centre_of_volume_m'][i] for r in selected)/total for i in range(3)]
    I=[[0.]*3 for _ in range(3)]
    for r in selected:
        delta=[r['centre_of_volume_m'][i]-cg[i] for i in range(3)];rr=sum(x*x for x in delta)
        for i in range(3):
            for j in range(3):I[i][j]+=r['inertia_at_region_centroid_kg_m2'][i][j]+r['mass_kg']*((rr if i==j else 0)-delta[i]*delta[j])
    if (not math.isclose(mass['defined_vehicle_material_mass_kg'],total,rel_tol=1e-10)
            or len(mass.get('defined_vehicle_material_cg_m',[]))!=3 or any(type(x) not in (int,float) or not math.isfinite(x) or abs(x-y)>1e-9 for x,y in zip(mass['defined_vehicle_material_cg_m'],cg))
            or any(not math.isclose(mass['defined_vehicle_material_inertia_kg_m2'][i][j],I[i][j],rel_tol=1e-9,abs_tol=1e-8) for i in range(3) for j in range(3))):
        raise ValueError('native assembled parallel-axis sum differs')
    six=mass['six_car_repetition'];cfg=configuration.selected();centres=[(i-2.5)*(17+cfg.formation.coupling_gap_assumption_m) for i in range(6)]
    if six['cars']!=6 or six['body_centres_x_m']!=centres or not math.isclose(six['instanced_defined_vehicle_mass_kg'],6*total,rel_tol=1e-10):raise ValueError('six-car material repetition differs')
    sixI=[[6*I[i][j]+(total*sum(x*x for x in centres) if i==j and i in (1,2) else 0) for j in range(3)] for i in range(3)]
    if any(not math.isclose(six['instanced_inertia_kg_m2'][i][j],sixI[i][j],rel_tol=1e-9,abs_tol=1e-8) for i in range(3) for j in range(3)):raise ValueError('six-car parallel-axis inertia differs')
    if any(mass.get(k) is not False for k in FLAGS):raise ValueError('native geometry cannot release hardware')
    return total


def cut_list(value):
    import csv
    stream=io.StringIO();writer=csv.writer(stream,lineterminator='\n');writer.writerow(['member_id','source_stock_id','material','cut_axis','cut_length_m','size_x_m','size_y_m','size_z_m','wall_m','wall_region_count','release'])
    for m in value['members']:writer.writerow([m['id'],m.get('source_member_id') or '',m['material'],'xyz'[m['axis']],f"{m['size_m'][m['axis']]:.9f}",*[f'{x:.9f}' for x in m['size_m']],f"{m['wall_m']:.9f}",len(m['part_ids']),'provisional'])
    return stream.getvalue()


def mesh_properties(part):
    """Independent welded-edge topology and translated tetrahedron integrals."""
    vertices=part['vertices_m'];faces=part['triangles']
    if not 4<=len(vertices)<=1000000 or not 4<=len(faces)<=2000000:raise ValueError('bounded closed assembled mesh required')
    if any(len(p)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in p) for p in vertices):raise ValueError('finite mesh coordinates required')
    identities=[tuple(round(x,9) for x in p) for p in vertices];edges={};terms=[];origin=vertices[0];used=set();adj={}
    for face in faces:
        if len(face)!=3 or len(set(face))!=3 or any(type(i) is not int or not 0<=i<len(vertices) for i in face):raise ValueError('mesh face indices differ')
        p,q,r=[[vertices[i][k]-origin[k] for k in range(3)] for i in face]
        terms.append(p[0]*(q[1]*r[2]-q[2]*r[1])+p[1]*(q[2]*r[0]-q[0]*r[2])+p[2]*(q[0]*r[1]-q[1]*r[0]))
        for i,j in zip(face,face[1:]+face[:1]):
            first,last=identities[i],identities[j]
            if first==last:raise ValueError('collapsed assembled mesh edge')
            used.update((first,last));adj.setdefault(first,set()).add(last);adj.setdefault(last,set()).add(first)
            key=tuple(sorted((first,last)));count,balance=edges.get(key,(0,0));edges[key]=(count+1,balance+(1 if first<last else -1))
    if any(count!=2 or balance!=0 for count,balance in edges.values()):raise ValueError('assembled mesh is not a closed oriented shell')
    if used!=set(identities):raise ValueError('orphan assembled mesh vertices')
    reached=set();pending=[next(iter(used))]
    while pending:
        point=pending.pop()
        if point not in reached:reached.add(point);pending.extend(adj[point]-reached)
    if reached!=used:raise ValueError('disconnected assembled material shell')
    volume=math.fsum(terms)/6
    if volume<=0:raise ValueError('assembled mesh must face outward with positive signed volume')
    return dict(signed_volume_m3=volume,euler_characteristic=len(used)-len(edges)+len(faces),
        bounds_m=[min(p[i] for p in vertices) for i in range(3)]+[max(p[i] for p in vertices) for i in range(3)])



def mesh_bounds_tolerances(part,mesh):
    """Exact planar extrema; radial chord sagitta for native cylinder facets."""
    tolerance=[1e-8]*3
    if part['kind']!='cylinder':return tolerance
    axis='xyz'.index(part.get('cylinder_axis','z'));uv=[i for i in range(3) if i!=axis];lo=part['at_m'];size=models.global_size(part)
    centre=[lo[i]+size[i]/2 for i in range(3)];radius=size[uv[0]]/2;end_angles=[set(),set()]
    for vertex in mesh['vertices_m']:
        radial=math.hypot(*(vertex[i]-centre[i] for i in uv));on_outer=abs(radial-radius)<=1e-8
        at_end=[abs(vertex[axis]-(lo[axis]+end*size[axis]))<=1e-8 for end in (0,1)]
        # This retained native exporter uses boundary-circle vertices only
        # (verified on every actual cylinder). Reject unsupported cap Steiner
        # points rather than allowing altered bore or cap geometry to hide.
        if not on_outer and not any(abs(radial-h['diameter_m']/2)<=1e-8 for h in part.get('holes',[])):
            raise ValueError('cylinder mesh vertex left exact native outer/bore radius')
        if on_outer:
            angle=math.atan2(vertex[uv[1]]-centre[uv[1]],vertex[uv[0]]-centre[uv[0]])%(2*math.pi)
            for end in (0,1):
                if at_end[end]:end_angles[end].add(round(angle,12))
    maximum_gap=0.
    for angles in end_angles:
        angles=sorted(angles)
        if len(angles)<8:raise ValueError('native cylinder endcap outer ring coverage incomplete')
        gap=max(y-x for x,y in zip(angles,angles[1:]+[angles[0]+2*math.pi]))
        if gap>math.pi/4+1e-9:raise ValueError('native cylinder angular facet gap too coarse')
        maximum_gap=max(maximum_gap,gap)
    sagitta=radius*(1-math.cos(maximum_gap/2))
    for i in uv:tolerance[i]+=sagitta
    return tolerance


def mesh_control():
    """A regular16-sided unit cylinder gives an independently known volume."""
    settings=load();count=16;vertices=[[math.cos(2*math.pi*i/count),math.sin(2*math.pi*i/count),z] for z in (0.,1.) for i in range(count)]
    triangles=[]
    for i in range(1,count-1):triangles.extend([[0,i+1,i],[count,count+i,count+i+1]])
    for i in range(count):
        j=(i+1)%count;triangles.extend([[i,j,count+j],[i,count+j,count+i]])
    got=mesh_properties(dict(vertices_m=vertices,triangles=triangles))
    analytical_polygon_volume=count*math.sin(2*math.pi/count)/2
    relative_circle_error=1-analytical_polygon_volume/math.pi
    if not math.isclose(got['signed_volume_m3'],analytical_polygon_volume,rel_tol=1e-12) or got['euler_characteristic']!=2:raise ValueError('independent cylinder mesh control failed')
    return dict(native_tessellation_deflection_mm=10.,weld_coordinate_rounding_m=1e-9,
        curved_or_through_hole_relative_volume_tolerance=settings['hardpoint']['mesh_relative_volume_tolerance'],plain_box_relative_volume_tolerance=1e-7,cylinder_radial_extrema='Actual outer-ring angular-gap chord sagitta; maxgap45degrees, exact endplanes and every outer/bore vertex radius, boundary-circle vertices only, minimum8outervertices/endcap',
        control=dict(sides=count,radius_m=1.,length_m=1.,signed_mesh_volume_m3=got['signed_volume_m3'],analytical_polygon_volume_m3=analytical_polygon_volume,analytical_circle_volume_m3=math.pi,relative_circle_volume_error=relative_circle_error,passed=relative_circle_error<settings['hardpoint']['mesh_relative_volume_tolerance']),
        scope='Each retained material shell must be connected, closed, consistently outward oriented, preserve each through-hole Euler topology, reproduce exact planar extrema and bounded cylinder chord extrema, and reproduce native volume within the declared tessellation tolerance. Mesh approximation is not a manufacturing dimensional tolerance.')


def readme(result,mass,legacy):
    c=result['hardpoint_screen'];ax=result['axial_screen'];kg=mass['defined_vehicle_material_mass_kg'];cg=mass['defined_vehicle_material_cg_m'];I=mass['defined_vehicle_material_inertia_kg_m2'];h=load()['hardpoint'];total_bolts=len(result['interfaces'])*h['bolts']
    return f'''# Joined structural-body candidate

The packet assembles every one of the63 previously defined primary/opening stock members into65 fitted member pieces: the two lower end members are split to keep the gangway open. Sandwich corners, openings, external corner laps, drilled through-bolt hardpoints and independent outboard magnetic load paths have actual placements. The existing24 cartridge retention assemblies are retained. Every native material pair, including the current2.5m-deep guidebeam context, is checked for unintended positive shared volume; no positive-volume exemption is allowed for a supposed joint or lap.

[Native assembled view](overview.png) · [Frame and hardpoint cutaway](frame-cutaway.png) · [Six repeated units](six-car.png) · [Assembly illustration](assembly-visibility.mp4) · [Dimensioned sections](sections.svg) · [Cut list](cut-list.csv)

The reopened FreeCAD solids contain **{kg:,.3f}kg of defined vehicle materials** at assumed densities. Partial-material CG is [{', '.join(f'{x:.6f}' for x in cg)}]m; centroid inertias Ixx/Iyy/Izz are {I[0][0]:,.3f}/{I[1][1]:,.3f}/{I[2][2]:,.3f}kg·m². These are geometry-derived structural/cartridge quantities, not the26.4t equipped AW3 car or a new tare claim. Guideway concrete/steel and unqualified winding packaging envelopes are excluded. Missing doors, glazing, HVAC, battery, controls, couplers, capture/brakes and other fitout remain outside this mass/CG/inertia result. The six-car view repeats the same defined unit using the selected body pitch; it includes no unmodelled gangway or coupler mass.

The fitted joint uses{h['bolts']}×M12×{h['bolt_length_m']*1000:g}mm through-bolts per interface, actual{h['bolt_hole_m']*1000:g}mm holes through both stringer walls,116mm bore crush spacers,18mm local laminate,12mm spreader and{h['carrier_flange_m']*1000:g}mm carrier flange. The rows are{(max(h['rows_z_m'])-min(h['rows_z_m']))*1000:g}mm apart vertically across{len(h['columns_x_m'])} longitudinal columns. The carrier is{h['carrier_width_m']*1000:g}×{h['carrier_depth_m']*1000:g}×{h['carrier_wall_m']*1000:g}mm and{(1.4-1.2-h['carrier_flange_m'])*1000:g}mm long. Smaller{h['outer_column_washer_diameter_m']*1000:g}mm outboard washers on the{sum(abs(x)>h['carrier_width_m']/2 for x in h['columns_x_m'])} outer columns clear the carrier; all inboard washers remain40mm. Actual{h['service_access_bore_m']*1000:g}mm service bores provide nominal socket insertion, with{c['projection_beyond_nut_m']*1000:g}mm bolt projection beyond the nut. The total{total_bolts} bolts, spacers, heads, washers and nuts are native material regions, not free allowances. At the assumed26.4t AW3 case, force/interface is{c['maximum_interface_force_n']:,.3f}N. A{h['prying_multiplier']:g} prying multiplier gives{c['tension_per_bolt_n']:,.3f}N tension/bolt and interaction{c['interaction_ratio']:.3f} against unqualified study allowables. The inboard12mm tube-wall pull-through assumption is checked separately from the18mm patch. The rejected eight-bolt and twelve-bolt exact geometries/revisions remain source-bound because they failed that tube-wall screen. The twelve-bolt rejection corrects a previously understated stringer-centre moment: the conservative freebody cut is now at the actual loaded flange face, y={c['joint_geometry']['loaded_flange_face_y_m']:g}m, giving a{c['geometric_force_offset_m']:g}m collector lever. Fatigue, welds, flange stiffness, joint rotation, wall net section, creep, fire and material qualification remain open.

The smaller120×80mm four-bolt idea is retained as a rejected analytical control. The historical200×180mm isolated pattern did not fit its120mm-wide carrier. The earlier full-width lower crossheads also pass through the deep concrete beam. Actual native common-volume checks reproduce{legacy['total_common_volume_mm3']:,.3f}mm³ of intersection on exact retained part IDs, bound to definition `{legacy['legacy_definition_sha256']}` and historical native manifest `{legacy['historical_native_manifest_sha256']}`. That exact old geometry is ineligible for assembled adoption. It remains an immutable rejected control; the new candidate routes each side independently below its winding envelope and outside the passive rails.

The two unperforated GFRP longitudinal tubes alone give an assumed gross axial stiffness{ax['gross_body_axial_stiffness_n_m']/1e6:.3f}MN/m. In series with the existing100MN/m coupler assumption, the pairwise value is{ax['body_and_coupler_series_stiffness_n_m']/1e6:.3f}MN/m before joint/hole/thermal compliance. Rigid-car moving studies cannot inherit this body's mass, inertias or100MN/m end-to-end stiffness. No city, mass or plant stiffness is promoted.

The overview, cutaway, six-car picture and movie use explicit display-only LOD: exact native-verified primitive positions/envelopes, eight-facet cylinders and omitted small through-bores. Every defined body material region is represented. The full native CAD/STEP/tessellation, holes, mass properties and tool checks remain unchanged. The movie translates these display envelopes through an illustrative assembly sequence. It is not an accepted assembly trajectory, collision-free path, lifting plan or construction-stage analysis. The final native no-interference result is separate from those unperformed checks.

[Native FreeCAD](model.FCStd) · [Compressed STEP](model.step.gz) · [Native reopen/interference receipt](native-cad.json) · [Geometry mass/CG/inertia](mass-properties.json) · [Retained failed legacy control](legacy-collision-control.json) · [Complete analytical and interface study](study.json.gz) · [Source and payload receipt](manifest.json)

All equipment, manufacturing and physical acceptance gates remain open. This is a provisional joined structural candidate, not a complete equipped train or a manufacturing release.
'''


def _read(path,maximum=MAX_BYTES):
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size>maximum:raise ValueError('bounded ordinary assembled file required')
    return path.read_bytes()


def _unzip(path):
    with gzip.GzipFile(fileobj=io.BytesIO(_read(path)),mode='rb') as stream:raw=stream.read(MAX_RAW+1)
    if len(raw)>MAX_RAW:raise ValueError('assembled decompression bound exceeded')
    return raw


def legacy_expected_collisions():
    """Independent axis-aligned outer-minus-bore volumes for the retained control."""
    old=json.loads(LEGACY.read_text());parts=old['definition']['parts'];rows=[];positive_limit=load()['geometry']['positive_intersection_limit_mm3']
    def common(size,at,other):
        return math.prod(max(0.,min(at[i]+size[i],other['at_m'][i]+other['size_m'][i])-max(at[i],other['at_m'][i])) for i in range(3))
    for head in [p for p in parts if p['id'].startswith('frame/lower-crosshead-')]:
        inner=head['size_m'].copy();start=head['at_m'].copy()
        for i in range(3):
            if i!=head['axis']:inner[i]-=2*head['wall_m'];start[i]+=head['wall_m']
        for beam in [p for p in parts if p['material']=='concrete']:
            volume=(common(head['size_m'],head['at_m'],beam)-common(inner,start,beam))*1e9
            if volume>positive_limit:
                rows.append(dict(left=head['id'],right=beam['id'],common_volume_mm3=volume))
    return rows


def publish(output=OUTPUT):
    before=sources();value=definition();result=study();output=Path(output)
    if output.is_symlink() or (output.exists() and (not output.is_dir() or any(p.is_symlink() or p.name not in FILES|{'manifest.json'} for p in output.iterdir()))):raise ValueError('owned assembled body output required')
    output.parent.mkdir(parents=True,exist_ok=True)
    # A staged packet avoids half-updated native material/receipt combinations.
    with tempfile.TemporaryDirectory(prefix='.assembled-body-',dir=output.parent) as temporary:
        stage=Path(temporary);(stage/'definition.json').write_bytes(encoded(value));_generate(stage/'definition.json',stage)
        receipt=json.loads((stage/'native-cad.json').read_text());raw=_read(stage/'model.step',MAX_RAW)
        (stage/'model.step.gz').write_bytes(gzip.compress(raw,mtime=0));(stage/'model.step').unlink()
        receipt['files_sha256'].pop('model.step');receipt['files_sha256']['model.step.gz']=digest(stage/'model.step.gz');receipt['step_uncompressed_sha256']=sha256(raw).hexdigest()
        (stage/'native-cad.json').write_bytes(encoded(receipt));mass=json.loads((stage/'mass-properties.json').read_text());legacy=json.loads((stage/'legacy-collision-control.json').read_text());_mass_check(value,mass)
        (stage/'study.json.gz').write_bytes(gzip.compress(encoded(result),mtime=0));(stage/'cut-list.csv').write_text(cut_list(value));(stage/'sections.svg').write_text(sections_svg(value))
        render(stage);(stage/'README.md').write_text(readme(result,mass,legacy))
        if sources()!=before:raise ValueError('assembled body sources changed during native export')
        manifest=dict(schema=SCHEMA,source_sha256=before,files_sha256={name:digest(stage/name) for name in sorted(FILES)},part_count=len(value['parts']),
            all_defined_material_pairs_native_checked=True,unintended_intersection_count=0,defined_vehicle_material_mass_kg=mass['defined_vehicle_material_mass_kg'],
            legacy_expected_collision_observed=True,complete_equipped_vehicle=False,default_mass_or_stiffness_changed=False,movie=station_native._probe(stage/'assembly-visibility.mp4'),**FLAGS)
        (stage/'manifest.json').write_bytes(encoded(manifest));verify(stage)
        output.mkdir(parents=True,exist_ok=True)
        for name in [*sorted(FILES),'manifest.json']:(stage/name).replace(output/name)
    return verify(output)


def verify(output=OUTPUT):
    output=Path(output);settings=load()
    if output.is_symlink() or not output.is_dir() or set(p.name for p in output.iterdir())!=FILES|{'manifest.json'}:raise ValueError('exact assembled packet inventory required')
    manifest=json.loads(_read(output/'manifest.json'))
    if manifest.get('schema')!=SCHEMA or manifest.get('source_sha256')!=sources():raise ValueError('assembled body sources stale')
    if set(manifest.get('files_sha256',{}))!=FILES or any(sha256(_read(output/name)).hexdigest()!=hash for name,hash in manifest['files_sha256'].items()):raise ValueError('assembled payload checksums differ')
    value=json.loads(_read(output/'definition.json'));expected=definition();result=json.loads(_unzip(output/'study.json.gz'))
    if value!=expected or result!=study():raise ValueError('assembled definition or recalculated study differs')
    if any(row.get(k) is not False for row in (manifest,value,result) for k in FLAGS) or manifest.get('part_count')!=len(value['parts']) or manifest.get('all_defined_material_pairs_native_checked') is not True or manifest.get('unintended_intersection_count')!=0 or manifest.get('legacy_expected_collision_observed') is not True or manifest.get('complete_equipped_vehicle') is not False or manifest.get('default_mass_or_stiffness_changed') is not False:raise ValueError('assembled geometry has no release or promotion authority')
    receipt=json.loads(_read(output/'native-cad.json'));mass=json.loads(_read(output/'mass-properties.json'));legacy=json.loads(_read(output/'legacy-collision-control.json'));visual=json.loads(_read(output/'visual-receipt.json'))
    ids=[p['id'] for p in value['parts']]
    if (receipt.get('fcstd_reopened') is not True or receipt.get('step_reopened') is not True or receipt.get('part_count')!=len(ids)
            or receipt.get('input_sha256')!=manifest['files_sha256']['definition.json'] or [p['id'] for p in receipt.get('parts',[])]!=ids
            or receipt.get('checked_interference_roles')!=value['interference_roles'] or receipt.get('interference_checked_ids')!=ids
            or receipt.get('exporter_sha256')!=manifest['source_sha256']['engineering/factory_examples/native.py']
            or receipt.get('geometry_helpers_sha256')!=manifest['source_sha256']['engineering/factory_examples/models.py']
            or receipt.get('assembled_inspector_sha256')!=manifest['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]):raise ValueError('actual reopened all-pair native evidence differs')
    for p,r in zip(value['parts'],receipt['parts']):
        size=models.global_size(p);bounds=p['at_m']+[p['at_m'][i]+size[i] for i in range(3)]
        if r.get('valid') is not True or not math.isclose(r['volume_m3'],models.volume(p),rel_tol=1e-7) or len(r['bounds_m'])!=6 or any(abs(x-y)>1e-8 for x,y in zip(r['bounds_m'],bounds)):raise ValueError('native solid validity, volume or bounds differ')
    _mass_check(value,mass)
    access=json.loads(_read(output/'tool-access.json'))
    expected_paths=len(value['interfaces'])*settings['hardpoint']['bolts']*2
    if (access.get('schema')!='osr-native-socket-insertion/1' or access.get('definition_sha256')!=manifest['files_sha256']['definition.json']
            or access.get('path_count')!=expected_paths or len(access.get('paths',[]))!=expected_paths or access.get('failures')!=[]
            or access.get('actual_native_common_checks_executed') is not True or access.get('nominal_socket_insertion_clear') is not True
            or any(access.get(k) is not False for k in FLAGS)):
        raise ValueError('actual socket insertion evidence differs')
    expected_sweeps=socket_paths(value);actual=access['paths']
    if ([{k:v for k,v in row.items() if k!='nearby_solids_checked'} for row in actual]!=expected_sweeps
            or len({(r['interface'],r['bolt_index'],r['direction']) for r in actual})!=expected_paths
            or any(type(r.get('nearby_solids_checked')) is not int or not 0<=r['nearby_solids_checked']<=len(ids) for r in actual)):
        raise ValueError('socket path identity, placement, dimensions or unique coverage differs')
    if not math.isclose(manifest['defined_vehicle_material_mass_kg'],mass['defined_vehicle_material_mass_kg'],rel_tol=1e-10):raise ValueError('native mass summary differs')
    old=json.loads(LEGACY.read_text())
    if (legacy.get('legacy_definition_sha256')!=old['definition_sha256'] or legacy.get('historical_native_manifest_sha256')!=old['historical_native_manifest_sha256']
            or legacy.get('retained_fixture_sha256')!=digest(LEGACY) or legacy.get('native_common_volume_executed') is not True or legacy.get('expected_failure_observed') is not True
            or legacy.get('eligible_for_assembled_adoption') is not False or not legacy.get('collisions') or legacy['total_common_volume_mm3']<=0):raise ValueError('legacy actual failed collision control differs')
    expected_collisions=legacy_expected_collisions()
    if ([(r['left'],r['right']) for r in legacy['collisions']]!=[(r['left'],r['right']) for r in expected_collisions]
            or any(not math.isclose(x['common_volume_mm3'],y['common_volume_mm3'],rel_tol=1e-7) for x,y in zip(legacy['collisions'],expected_collisions))
            or not math.isclose(legacy['total_common_volume_mm3'],sum(r['common_volume_mm3'] for r in expected_collisions),rel_tol=1e-7)):
        raise ValueError('native legacy collision volumes differ from independent tube/bore control')
    mesh=json.loads(_unzip(output/'native-mesh.json.gz'))
    if mesh.get('input_sha256')!=manifest['files_sha256']['definition.json'] or [p['id'] for p in mesh['parts']]!=ids:raise ValueError('assembled native mesh identity differs')
    for p,r in zip(value['parts'],mesh['parts']):
        lo=p['at_m'];size=models.global_size(p);hi=[lo[i]+size[i] for i in range(3)];vertices=r['vertices_m'];triangles=r['triangles']
        if (r['material']!=p['material'] or not math.isclose(r['volume_m3'],models.volume(p),rel_tol=1e-7) or not vertices or not triangles
                or len(vertices)>1000000 or len(triangles)>2000000
                or any(len(v)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) or not lo[i]-1e-8<=x<=hi[i]+1e-8 for i,x in enumerate(v)) for v in vertices)
                or any(len(t)!=3 or any(type(i) is not int or not 0<=i<len(vertices) for i in t) for t in triangles)):raise ValueError('bounded assembled native mesh differs')
        props=mesh_properties(r);expected_bounds=lo+hi;bounds_tolerance=mesh_bounds_tolerances(p,r)*2
        tolerance=settings['hardpoint']['mesh_relative_volume_tolerance'] if p.get('holes') or p['kind']=='cylinder' else 1e-7
        if (props['euler_characteristic']!=2-2*len(p.get('holes',[]))
                or any(abs(x-y)>tol for x,y,tol in zip(props['bounds_m'],expected_bounds,bounds_tolerance))
                or not math.isclose(props['signed_volume_m3'],models.volume(p),rel_tol=tolerance,abs_tol=1e-12)):
            raise ValueError('closed mesh hole topology, occupied extrema or signed volume differs')
    step_raw=_unzip(output/'model.step.gz')
    if not step_raw.startswith(b'ISO-10303-21;'):raise ValueError('native STEP required')
    if sha256(step_raw).hexdigest()!=receipt['step_uncompressed_sha256']:raise ValueError('native STEP digest differs')
    with zipfile.ZipFile(output/'model.FCStd') as archive:
        entries=archive.infolist()
        if ('Document.xml' not in archive.namelist() or len(entries)!=len(set(archive.namelist())) or any(x.file_size>MAX_RAW or Path(x.filename).is_absolute() or '..' in Path(x.filename).parts for x in entries)
                or sum(x.file_size for x in entries)>MAX_RAW or archive.testzip() is not None):raise ValueError('bounded native FreeCAD archive required')
    for row,names in ((receipt,{'model.FCStd','model.step.gz','native-mesh.json.gz'}),(visual,{'overview.png','frame-cutaway.png','six-car.png','assembly-visibility.mp4'})):
        if set(row.get('files_sha256',{}))!=names or any(manifest['files_sha256'][name]!=h for name,h in row['files_sha256'].items()):raise ValueError('nested assembled evidence checksum differs')
    if (visual.get('renderer_sha256')!=manifest['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()] or visual.get('definition_sha256')!=manifest['files_sha256']['definition.json'] or visual.get('mesh_sha256')!=manifest['files_sha256']['native-mesh.json.gz']
            or visual.get('moving_offsets_are_measured_assembly_trajectories') is not False or visual.get('path_collision_verification') is not False or visual.get('display_lod')!=display_lod_receipt(value,mesh)):raise ValueError('assembly visual scope differs')
    for name in ('overview.png','frame-cutaway.png','six-car.png'):
        raw=_read(output/name)
        if not raw.startswith(b'\x89PNG\r\n\x1a\n') or [int.from_bytes(raw[i:i+4],'big') for i in (16,20)]!=[1200,675]:raise ValueError('assembled PNG dimensions differ')
    if station_native._probe(output/'assembly-visibility.mp4')!=manifest['movie']:raise ValueError('assembled movie differs')
    if ((output/'README.md').read_text()!=readme(result,mass,legacy) or (output/'cut-list.csv').read_text()!=cut_list(value) or (output/'sections.svg').read_text()!=sections_svg(value)):raise ValueError('assembled drawings or presentation differ')
    return manifest


def read_summary(output=OUTPUT):
    manifest=verify(output);result=json.loads(_unzip(Path(output)/'study.json.gz'));mass=json.loads(_read(Path(output)/'mass-properties.json'))
    return dict(schema=SCHEMA,part_count=manifest['part_count'],source_primary_stock_count=result['source_primary_stock_count'],installed_primary_member_count=result['installed_primary_member_count'],
        all_defined_material_pairs_native_checked=True,unintended_intersection_count=0,
        defined_vehicle_material_mass_kg=mass['defined_vehicle_material_mass_kg'],defined_vehicle_material_cg_m=mass['defined_vehicle_material_cg_m'],
        defined_vehicle_material_inertia_kg_m2=mass['defined_vehicle_material_inertia_kg_m2'],legacy_expected_collision_observed=True,
        hardpoint_analytical_screen_pass=result['hardpoint_screen']['analytical_screen_pass'],axial_screen=result['axial_screen'],
        complete_equipped_vehicle=False,default_mass_or_stiffness_changed=False,**FLAGS)
