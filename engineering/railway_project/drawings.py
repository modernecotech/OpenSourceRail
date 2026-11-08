"""Source-bound research stock drawings; never finished-part or release authority.

Call describe() for stable geometry-variant IDs and SI dimension names, then
supply explicit per-variant inspection limits and source-referenced route times
to export(). No native application, CAD/STEP, FEM, ERP or supplier lookup runs.
"""
from copy import deepcopy
from math import isfinite, pi
from pathlib import Path
from collections import defaultdict
from xml.etree import ElementTree as ET
import re
import textwrap

from engineering.station_rail import ROOT
from engineering.station_rail.common import identity, encoded, digest
from engineering.pilot_delivery import model, review

SCHEMA='osr-controlled-stock-drawings/1'
PRODUCER='engineering/railway_project/drawings.py'
FLAGS=review.FLAGS
MAX_TYPES=12
MAX_VARIANTS=12
MAX_BYTES=50*1024**2
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)


def _number(v,positive=False):
    if type(v) not in (int,float) or not isfinite(v) or (positive and v<=0):
        raise ValueError('Finite '+('positive ' if positive else '')+'source dimension required')
    return float(v)


def _unique(rows,key):
    result={r[key]:r for r in rows}
    if len(result)!=len(rows):raise ValueError('Duplicate source '+key)
    return result


def _authenticate(body,proposal,root):
    model.sealed(body);model.validate_proposal(proposal)
    review.contract.identities(proposal['identities'])
    if body.get('schema')!='osr-vehicle-installation/1' or identity(body['physical_definition'])!=body['candidate_id']:
        raise ValueError('Sealed installed physical body required')
    binding=proposal['identities']
    if (binding['body_candidate_id']!=body['candidate_id'] or binding['engineering_revision']!=body['evaluation_id']
            or binding['source_body_bundle_id']!=body['parent_bundle_id']):
        raise ValueError('Mixed body/proposal candidate or revision')
    for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release','movement_authority','selected_reference_changed'):
        if body.get(k) is not False:raise ValueError('Explicit research body disposition required')
    source={}
    for owner in (body,proposal):
        for name,want in owner['source_sha256'].items():
            if name in source and source[name]!=want:raise ValueError('Mixed source epochs')
            path=review.ordinary(root,name,maximum=64*1024**2)
            if digest(path)!=want:raise ValueError('Body/proposal source changed: '+name)
            source[name]=want
    parts=_unique(body['parts'],'id');items=_unique(proposal['items'],'id');patterns=_unique(body['patterns'],'id')
    physical=_unique(body['physical_definition']['occurrence_patterns'],'id')
    occurrences=_unique(proposal['occurrence_patterns'],'id');materials=_unique(body['materials'],'id')
    if 'materials' in proposal and _unique(proposal['materials'],'id')!=materials:
        raise ValueError('Proposal material definitions differ from source body')
    if set(parts)!=set(items) or set(patterns)!=set(physical) or set(patterns)!=set(occurrences):
        raise ValueError('Complete source part/pattern sets must agree')
    groups=defaultdict(list)
    for pid,p in patterns.items():
        if any(p.get(k)!=v for k,v in physical[pid].items()):raise ValueError('Pattern differs from sealed physical definition')
        q=occurrences[pid]
        if p['part_id'] not in parts or q['part_id']!=p['part_id'] or q['count_per_train']!=p['count'] or q['assembly_occurrence_id']!=p['assembly_occurrence_id']:
            raise ValueError('Mixed counted occurrence pattern')
        if type(p['count']) is not int or p['count']<=0:raise ValueError('Positive integer pattern count required')
        if p['material_id']!=parts[p['part_id']]['material_id']:raise ValueError('Pattern material differs')
        groups[p['part_id']].append(p)
    for pid,p in parts.items():
        if p['material_id'] not in materials:raise ValueError('Unknown source material')
        for key in ('component_definition_id','name','assembly_id','material_id','quantity_per_train','unit','stock','manufacturing'):
            if p[key]!=items[pid][key]:raise ValueError('Proposal part differs from source body: '+pid+'/'+key)
        if sum(x['count'] for x in groups[pid])!=p['quantity_per_train']:raise ValueError('Pattern quantity differs from source part')
    return parts,items,groups,materials,source


def _profile(points):
    if not isinstance(points,list) or not 3<=len(points)<=64:raise ValueError('Bounded explicit polygon profile required')
    p=[[_number(v) for v in xy] for xy in points if isinstance(xy,list) and len(xy)==2]
    if len(p)!=len(points):raise ValueError('Two-coordinate source profile required')
    if p[0]==p[-1]:p=p[:-1]
    if len(set(map(tuple,p)))!=len(p):raise ValueError('Repeated source profile vertex')
    area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))/2
    if abs(area)<1e-14:raise ValueError('Nonzero source profile area required')
    def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    n=len(p)
    for i in range(n):
        for j in range(i+1,n):
            if j in (i,(i+1)%n) or i==(j+1)%n:continue
            a,b,c,d=p[i],p[(i+1)%n],p[j],p[(j+1)%n]
            if orient(a,b,c)*orient(a,b,d)<=0 and orient(c,d,a)*orient(c,d,b)<=0:
                if max(min(a[0],b[0]),min(c[0],d[0]))<=min(max(a[0],b[0]),max(c[0],d[0])) and max(min(a[1],b[1]),min(c[1],d[1]))<=min(max(a[1],b[1]),max(c[1],d[1])):
                    raise ValueError('Self-intersecting source profile')
    return p


def _geometry(g):
    """Cross-sections come from source_stock, never a substituted size box."""
    stock=deepcopy(g.get('source_stock'));profile=None;dims={};holds=[]
    if stock is None:
        size=g.get('size_m')
        if not isinstance(size,list) or len(size)!=3:raise ValueError('Explicit bounded installation zone required')
        L,W,H=[_number(x,True) for x in size];kind='envelope';scope='bounded-installation-envelope'
        holds.append('No source stock/finished equipment geometry: bounded installation envelope only')
    else:
        kind=stock.get('kind');scope='gross-source-stock'
        if kind in ('box','envelope'):
            if not isinstance(stock.get('size_m'),list) or len(stock['size_m'])!=3:raise ValueError('Three source stock dimensions required')
            L,W,H=[_number(x,True) for x in stock['size_m']]
            if kind=='envelope':scope='bounded-installation-envelope'
        elif kind in ('rhs','u_channel'):
            L,W,H=[_number(stock[k],True) for k in ('length_m','width_m','depth_m')];t=_number(stock['wall_m'],True)
            if 2*t>=min(W,H):raise ValueError('Wall consumes source section')
            dims['wall_m']=t
        elif kind in ('annulus','cylinder'):
            L=_number(stock['length_m'],True);ro=_number(stock.get('radius_m',stock.get('outer_radius_m')),True);W=H=2*ro
            dims['outer_diameter_m']=W
            if kind=='annulus':
                ri=_number(stock['inner_radius_m'],True)
                if ri>=ro:raise ValueError('Annulus bore consumes source section')
                dims['inner_diameter_m']=2*ri
        elif kind in ('polygon-prism','polygon_prism','xz-profile-prism'):
            profile=_profile(stock['points_xz_m']);W=_number(stock.get('thickness_m',stock.get('width_m')),True)
            L=max(p[0] for p in profile)-min(p[0] for p in profile);H=max(p[1] for p in profile)-min(p[1] for p in profile);scope='source-polygon-prism'
        else:raise ValueError('Unsupported source stock geometry: '+str(kind))
        if kind=='envelope':holds.append('Supplier internals, wall thicknesses, holes and fits are unknown; envelope is not a fabrication drawing')
    if g.get('finished_profile_xz_m') is not None:
        if kind!='box':raise ValueError('Proposed cut profile requires its explicit rectangular source blank')
        profile=_profile(g['finished_profile_xz_m'])
        if any(abs(x)>L/2+1e-10 or abs(z)>H/2+1e-10 for x,z in profile):raise ValueError('Cut profile exceeds source blank')
        scope='proposed-cut-profile-from-gross-stock';holds.append('Source-proposed cut profile is not verified finished geometry; gross-stock accounting retained')
    dims.update(length_m=L,width_m=W,depth_m=H)
    if profile:
        for i,(x,z) in enumerate(profile):dims['profile_vertex_'+str(i)+'_x_m']=x;dims['profile_vertex_'+str(i)+'_z_m']=z
    if scope!='bounded-installation-envelope' and g.get('exact_stock') is not True:raise ValueError('Stock geometry is not declared exact')
    holds.append('Finished holes, joints, mating fits, production datums and material/process qualification remain outside this stock drawing')
    return dict(kind=kind,scope=scope,source_stock=stock,profile_xz_m=profile,dimensions_m=dims,holds=holds,
        fabrication_geometry_supported=scope!='bounded-installation-envelope',finished_geometry_verified=g.get('finished_geometry_verified') is True)


def describe(body,proposal,selected_part_ids,*,source_root=ROOT):
    """Authenticate source and expose stable geometry IDs before declarations."""
    parts,items,groups,materials,source=_authenticate(body,proposal,Path(source_root))
    if not isinstance(selected_part_ids,(list,tuple)) or not 1<=len(selected_part_ids)<=MAX_TYPES or len(set(selected_part_ids))!=len(selected_part_ids):
        raise ValueError('Select one to twelve distinct representative types')
    if not set(selected_part_ids)<=set(parts):raise ValueError('Unknown selected part')
    rows=[]
    for pid in selected_part_ids:
        variants={}
        for p in groups[pid]:
            signature={k:p['geometry'].get(k) for k in ('source_stock','finished_profile_xz_m','exact_stock','definition_basis','finished_geometry_verified')}
            if signature['source_stock'] is None:signature['envelope_size_m']=p['geometry'].get('size_m')
            vid=identity(signature)
            if vid not in variants:
                try:shape=_geometry(p['geometry']);error=None
                except (ValueError,KeyError,TypeError) as exc:shape=None;error=str(exc)
                variants[vid]=dict(variant_id=vid,source_geometry=deepcopy(p['geometry']),shape=shape,geometry_hold=error,pattern_ids=[],count_per_train=0)
            variants[vid]['pattern_ids'].append(p['id']);variants[vid]['count_per_train']+=p['count']
        rows.append(dict(part=deepcopy(items[pid]),material=deepcopy(materials[parts[pid]['material_id']]),variants=sorted(variants.values(),key=lambda v:v['variant_id'])))
    return dict(schema=SCHEMA+'/scope',identities=deepcopy(proposal['identities']),proposal_id=proposal['proposal_id'],
        body_evaluation_id=body['evaluation_id'],source_sha256=source,selected=rows)


def _el(parent,name,**attrs):return ET.SubElement(parent,'{'+NS+'}'+name,{k.replace('_','-'):str(v) for k,v in attrs.items()})
def _text(parent,x,y,text,cls='label',**attrs):
    e=_el(parent,'text',x=x,y=y,**{'class':cls},**attrs);e.text=str(text);return e

def _label(value):return format(value*1000,'.6f').rstrip('0').rstrip('.')+' mm'


def _svg(row,variant,revision,limits):
    shape=variant['shape'];d=shape['dimensions_m'];L,W,H=[d[k] for k in ('length_m','width_m','depth_m')]
    root=ET.Element('{'+NS+'}svg',dict(width='420mm',height='297mm',viewBox='0 0 1400 990',role='img'))
    title=_el(root,'title');title.text=row['part']['name']+' — '+shape['scope']
    meta=_el(root,'metadata');meta.text=encoded(dict(source_part_id=row['part']['id'],component_definition_id=row['part']['component_definition_id'],source_part_sha256=identity(row['part']),variant=variant,revision=revision,dimensions_source_units='m',drawing_dimension_units='mm',identities=row['part']['identities'])).decode()
    style=_el(root,'style');style.text='''text{font-family:DejaVu Sans,Arial,sans-serif;fill:#173141}.title{font-size:25px;font-weight:700}.label{font-size:16px}.small{font-size:12px}.mono{font-family:DejaVu Sans Mono,monospace;font-size:10px}.warning{font-size:16px;fill:#9a5126;font-weight:600}.outline{fill:#edf3f5;stroke:#173141;stroke-width:2}.hidden{fill:none;stroke:#678796;stroke-width:1.3;stroke-dasharray:8 5}.centre{stroke:#648595;stroke-width:1;stroke-dasharray:12 4 2 4}.dim{stroke:#36596c;stroke-width:1.1;fill:none}.frame{stroke:#b2c3cb;fill:none;stroke-width:1}.profile{fill:url(#hatch);stroke:#173141;stroke-width:2}'''
    defs=_el(root,'defs');pattern=_el(defs,'pattern',id='hatch',width=9,height=9,patternUnits='userSpaceOnUse',patternTransform='rotate(45)');_el(pattern,'line',x1=0,y1=0,x2=0,y2=9,stroke='#bed0d8',stroke_width=2)
    arrow=_el(defs,'marker',id='arrow',viewBox='0 0 10 10',refX=5,refY=5,markerWidth=7,markerHeight=7,orient='auto-start-reverse');_el(arrow,'path',d='M 0 0 L 10 5 L 0 10 Z',fill='#36596c')
    _el(root,'rect',x=0,y=0,width=1400,height=990,fill='white')
    _el(root,'rect',x=18,y=18,width=1364,height=954,**{'class':'frame'});_el(root,'rect',x=18,y=18,width=1364,height=100,fill='#edf3f5')
    for i,line in enumerate(textwrap.wrap(row['part']['name'],72)[:2]):_text(root,40,52+i*29,line,'title')
    _text(root,40,105,shape['scope'].replace('-',' ').upper(),'warning');_text(root,1355,50,'CONTROLLED RESEARCH DRAFT','label',text_anchor='end');_text(root,1355,80,'NO MANUFACTURING / OPERATING RELEASE','small',text_anchor='end')
    def dimension(x1,y1,x2,y2,text,vertical=False):
        _el(root,'line',x1=x1,y1=y1,x2=x2,y2=y2,**{'class':'dim','marker-start':'url(#arrow)','marker-end':'url(#arrow)'})
        _text(root,(x1+x2)/2+(14 if vertical else 0),(y1+y2)/2+(-8 if not vertical else 0),text,'small',text_anchor='start' if vertical else 'middle')
    def rectview(name,x,y,w,h,a,b,profile=None):
        _text(root,x,y-22,name,'label');_el(root,'rect',x=x-10,y=y-9,width=w+20,height=h+59,**{'class':'frame'})
        scale=min((w-95)/a,(h-65)/b);sx=(w-a*scale)/2+x;sy=(h-b*scale)/2+y
        _el(root,'rect',x=sx,y=sy,width=a*scale,height=b*scale,**{'class':'outline' if shape['scope']!='bounded-installation-envelope' else 'hidden'})
        if profile:
            xmin=-L/2 if shape['scope']=='proposed-cut-profile-from-gross-stock' else min(v[0] for v in profile)
            zmax=H/2 if shape['scope']=='proposed-cut-profile-from-gross-stock' else max(v[1] for v in profile)
            pts=' '.join(str(sx+(px-xmin)*scale)+','+str(sy+(zmax-pz)*scale) for px,pz in profile)
            _el(root,'polygon',points=pts,**{'class':'profile'})
        if shape['kind'] in ('rhs','annulus','cylinder'):
            _el(root,'line',x1=sx-12,y1=sy+b*scale/2,x2=sx+a*scale+12,y2=sy+b*scale/2,**{'class':'centre'})
            inside=d.get('inner_diameter_m',b-2*d.get('wall_m',b/2))
            if inside>0:
                for sign in (-1,1):_el(root,'line',x1=sx,y1=sy+b*scale/2+sign*inside*scale/2,x2=sx+a*scale,y2=sy+b*scale/2+sign*inside*scale/2,**{'class':'hidden'})
        dimension(sx,sy+b*scale+24,sx+a*scale,sy+b*scale+24,_label(a));dimension(sx+a*scale+23,sy,sx+a*scale+23,sy+b*scale,_label(b),True)
        _text(root,x+3,y+h+40,'Independent view scale; dimensions govern. Local stock axes.','small')
    rectview('FRONT  X–Z',45,170,820,235,L,H,shape['profile_xz_m'])
    rectview('PLAN  X–Y',45,500,820,235,L,W)
    x,y,w,h=955,185,365,400;_text(root,x,y-37,'END '+('PROJECTION' if shape['profile_xz_m'] else 'SECTION')+'  Y–Z','label');_el(root,'rect',x=x-15,y=y-20,width=w+35,height=h+55,**{'class':'frame'});s=min((w-80)/W,(h-75)/H);sx=x+(w-W*s)/2;sy=y+(h-H*s)/2
    def rpath(x,y,a,b):return f'M {x} {y} h {a} v {b} h {-a} Z '
    if shape['kind'] in ('annulus','cylinder'):
        _el(root,'circle',cx=sx+W*s/2,cy=sy+H*s/2,r=W*s/2,**{'class':'profile'})
        if 'inner_diameter_m' in d:_el(root,'circle',cx=sx+W*s/2,cy=sy+H*s/2,r=d['inner_diameter_m']*s/2,fill='white',stroke='#173141',stroke_width=2)
        _el(root,'line',x1=sx-12,y1=sy+H*s/2,x2=sx+W*s+12,y2=sy+H*s/2,**{'class':'centre'})
        _el(root,'line',x1=sx+W*s/2,y1=sy-12,x2=sx+W*s/2,y2=sy+H*s+12,**{'class':'centre'})
    elif shape['kind']=='rhs':
        t=d['wall_m']*s;_el(root,'path',d=rpath(sx,sy,W*s,H*s)+rpath(sx+t,sy+t,W*s-2*t,H*s-2*t),fill_rule='evenodd',**{'class':'profile'})
    elif shape['kind']=='u_channel':
        t=d['wall_m'];pts=[(0,0),(W,0),(W,t),(t,t),(t,H-t),(W,H-t),(W,H),(0,H)];_el(root,'polygon',points=' '.join(f'{sx+a*s},{sy+b*s}' for a,b in pts),**{'class':'profile'})
    else:_el(root,'rect',x=sx,y=sy,width=W*s,height=H*s,**{'class':'hidden' if shape['scope']=='bounded-installation-envelope' else 'profile'})
    dimension(sx,sy+H*s+24,sx+W*s,sy+H*s+24,_label(W));dimension(sx+W*s+23,sy,sx+W*s+23,sy+H*s,_label(H),True)
    for i,k in enumerate(('wall_m','outer_diameter_m','inner_diameter_m')):
        if k in d:_text(root,950,650+25*i,k.replace('_m','').replace('_',' ').upper()+': '+_label(d[k]),'label')
    if shape['profile_xz_m']:
        _text(root,950,640,'PROFILE VERTICES  •  local X, Z (mm)','small')
        for i,(x,z) in enumerate(shape['profile_xz_m'][:8]):
            _text(root,950,659+15*i,f'P{i+1}: {_label(x)} , {_label(z)}','small')
        if len(shape['profile_xz_m'])>8:_text(root,950,794,'Full profile table held; see geometry.json.','small')
    else:_text(root,950,750,'No holes or supplier internals inferred.','small')
    _el(root,'line',x1=35,y1=805,x2=1365,y2=805,**{'class':'frame'})
    notes=['DIMENSIONS: millimetres. Source geometry: metres. Orthographic projections; view scales independent.',
        'Material: '+row['material'].get('specification',row['material']['id']),
        'Source patterns: '+str(len(variant['pattern_ids']))+' / counted quantity per train: '+str(variant['count_per_train']),
        'Nominal stock only. Inspection limits/process times missing: controlled document scope held.' if not limits else 'Declared research limits: '+str(len(limits))+' source dimensions; see declarations.json. No released tolerances.']
    for i,line in enumerate(notes):_text(root,40,827+i*18,textwrap.shorten(line,165,placeholder=' …'),'small')
    _el(root,'line',x1=35,y1=902,x2=1365,y2=902,**{'class':'frame'})
    _text(root,40,922,'PART: '+row['part']['id']+'   REV: '+revision,'small');_text(root,40,944,'BODY '+row['part']['identities']['body_candidate_id'],'mono');_text(root,40,961,'ENGINEERING '+row['part']['identities']['engineering_revision'],'mono')
    _text(root,1010,924,'SHEET '+variant['variant_id'][:14],'small');_text(root,1010,946,'A3 • source stock / research only','small')
    return ET.tostring(root,encoding='utf-8',xml_declaration=True)


def _declared(row,variant,part_declaration):
    """No tolerance, fit, supplier feature or process time default is invented."""
    if not isinstance(part_declaration,dict):return None,['No declared inspection limits and process times']
    revision=part_declaration.get('revision');review.contract.text(revision,'research revision',100)
    research=part_declaration.get('research_holds')
    if not isinstance(research,list) or any(not isinstance(s,str) or not s.strip() for s in research):raise ValueError('Explicit research holds required')
    declaration=part_declaration.get('variants',{}).get(variant['variant_id'])
    if declaration is None:return None,['Missing declarations for geometry variant '+variant['variant_id']]
    if not isinstance(declaration,dict) or set(declaration)!={'characteristics','operations'}:
        raise ValueError('Explicit variant inspection and route declarations required')
    chars=[];refs={};dims=variant['shape']['dimensions_m'];covered=set();prefix='v'+variant['variant_id'][:12]+'-'
    for item in declaration.get('characteristics',[]):
        data=deepcopy(item);dimension=data.pop('dimension');unit=data.get('unit')
        if dimension not in dims or unit not in ('m','mm'):raise ValueError('Inspection must bind a source dimension in explicit m/mm')
        nominal=dims[dimension]*(1000 if unit=='mm' else 1)
        for k in ('minimum','maximum'):
            if data[k] is not None:_number(data[k])
        if ((data['minimum'] is None and data['maximum'] is None) or (data['minimum'] is not None and data['minimum']>nominal) or (data['maximum'] is not None and data['maximum']<nominal)):
            raise ValueError('Declared research limits exclude the source nominal dimension')
        refs[data['id']]=prefix+data['id'];data['id']=refs[data['id']];chars.append(data);covered.add(dimension)
    if covered!=set(dims):return None,['Inspection limits do not cover all source dimensions: '+', '.join(sorted(set(dims)-covered))]
    operations=[]
    for item in declaration.get('operations',[]):
        data=deepcopy(item);index=data.pop('source_operation_index')
        if type(index) is not int or not 0<=index<len(row['part']['manufacturing']):raise ValueError('Route must reference an actual source manufacturing operation')
        if data['operation']!=row['part']['manufacturing'][index]:raise ValueError('Route operation differs from its source text')
        if any(i not in refs for i in data['inspection_ids']):raise ValueError('Dangling routing inspection reference')
        data['inspection_ids']=[refs[i] for i in data['inspection_ids']];operations.append(data)
    if not operations:return None,['No declared source-referenced process route']
    return dict(revision=revision,research_holds=research,characteristics=chars,operations=operations),[]


def export(body,proposal,output,selected_part_ids,declared_tolerances_and_process_times,*,source_root=ROOT):
    """Write real SVGs and controlled research docs for at most twelve types.

    Declarations: {part_id:{revision,research_holds,variants:{variant_id:{
      characteristics:[{dimension:<describe dimension name>,...protocol fields}],
      operations:[{source_operation_index:<part.manufacturing index>,...protocol fields}]
    }}}}. Every variant and source dimension requires explicit declarations for
    review-index coverage. Unknown finished details always remain research holds.
    """
    scope=describe(body,proposal,selected_part_ids,source_root=source_root)
    model.guard_draft(declared_tolerances_and_process_times)
    if not isinstance(declared_tolerances_and_process_times,dict) or not set(declared_tolerances_and_process_times)<=set(selected_part_ids):raise ValueError('Declarations must belong to selected source parts')
    out=Path(output).absolute()
    if out.exists() or any(p.is_symlink() for p in (out,*out.parents)):raise ValueError('Fresh ordinary output directory required')
    out.mkdir(parents=True);components=[];coverage=[];conversions={}
    def write(name,raw):
        if sum(p.stat().st_size for p in out.rglob('*') if p.is_file())+len(raw)>MAX_BYTES:raise ValueError('Controlled drawing output budget exceeded')
        path=out/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        return dict(path=name,sha256=digest(path),bytes=len(raw),media_type='image/svg+xml' if name.endswith('.svg') else 'application/json')
    write('declarations.json',encoded(declared_tolerances_and_process_times))
    for row in scope['selected']:
        pid=row['part']['id'];part_decl=declared_tolerances_and_process_times.get(pid);folder='parts/'+identity(pid)[:16];payloads=[];chars=[];operations=[];holds=[];variant_rows=[];revisions=set();complete=True
        if part_decl is not None and not isinstance(part_decl,dict):raise ValueError('Structured part declarations required')
        if part_decl is not None and set(part_decl)!={'revision','research_holds','variants'}:
            raise ValueError('Only explicit revision, holds and variant declarations are supported')
        if part_decl is not None and (not isinstance(part_decl.get('variants'),dict) or set(part_decl['variants'])-set(v['variant_id'] for v in row['variants'])):
            raise ValueError('Unknown declared geometry variant')
        if len(row['variants'])>MAX_VARIANTS:complete=False;holds.append('More than twelve distinct geometry variants; split into reviewed document scope')
        for variant in row['variants']:
            record=dict(variant_id=variant['variant_id'],pattern_ids=variant['pattern_ids'],count_per_train=variant['count_per_train'],drawn=False,controlled_dimensions_complete=False,holds=[])
            if variant['shape'] is None:record['holds'].append(variant['geometry_hold']);complete=False
            elif len(row['variants'])>MAX_VARIANTS:record['holds'].append('Variant count exceeds this document protocol');complete=False
            else:
                declared,missing=_declared(row,variant,part_decl);record['holds'].extend(missing);record['holds'].extend(variant['shape']['holds']);revision=declared['revision'] if declared else (part_decl or {}).get('revision','RESEARCH-UNSPECIFIED')
                drawing=write(folder+'/'+variant['variant_id'][:16]+'.svg',_svg(row,variant,revision,declared['characteristics'] if declared else []));payloads.append(drawing);record.update(drawn=True,drawing=drawing,controlled_dimensions_complete=declared is not None,geometry_scope=variant['shape']['scope'])
                if declared:
                    revisions.add(declared['revision']);chars.extend(declared['characteristics']);holds.extend(declared['research_holds'])
                    for op in declared['operations']:operations.append(dict(op,sequence=len(operations)+1))
                if declared is None or not variant['shape']['fabrication_geometry_supported']:complete=False
                if len(variant['shape']['profile_xz_m'] or [])>8:
                    complete=False;record['holds'].append('More than eight profile vertices require a separate dimensioned detail sheet')
            holds.extend(record['holds']);variant_rows.append(record)
        if len(chars)>200 or len(operations)>200:
            complete=False;holds.append('Inspection/routing rows exceed the controlled document protocol; split reviewed scope')
        if len(revisions)>1:raise ValueError('Part variants must share one controlled document revision')
        metadata=dict(schema=SCHEMA+'/geometry-provenance',identities=proposal['identities'],part_id=pid,component_definition_id=row['part']['component_definition_id'],source_part_sha256=identity(row['part']),material=row['material'],variants=row['variants'],coverage=variant_rows,review_eligible=complete,finished_part_qualification=False,**FLAGS)
        write(folder+'/geometry.json',encoded(metadata))
        if complete:
            common=dict(schema='osr-controlled-research-document/1',identities=deepcopy(proposal['identities']),part_id=pid,component_definition_id=row['part']['component_definition_id'],source_part_sha256=identity(row['part']),revision=next(iter(revisions)),maturity='controlled-research-draft',research_holds=list(dict.fromkeys(holds)),**FLAGS)
            documents={'drawing':dict(common,document_type='drawing',payloads=payloads)}
            for kind,field,values in [('inspection','characteristics',chars),('routing','operations',operations)]:
                payload=write(folder+'/'+kind+'.json',encoded(dict(schema='osr-controlled-research-'+('inspection' if kind=='inspection' else 'route')+'/1',identities=proposal['identities'],part_id=pid,**{field:values})))
                documents[kind]=dict(common,document_type=kind,payloads=[payload],**{field:values})
            mapping={'part_id':pid}
            for kind,document in documents.items():
                review.contract.validate_document(document,row['part'],proposal['identities']);name=folder+'/'+kind+'-metadata.json';write(name,encoded(document));mapping[kind]=name
            components.append(mapping);conversions[pid]=dict(valuation_mode='source-priced-workpiece',source_part_sha256=identity(row['part']),stock_inputs=[],direct_process_allowance_usd=None)
        coverage.append(dict(part_id=pid,source_pattern_ids=sorted(p for v in row['variants'] for p in v['pattern_ids']),variants=variant_rows,controlled_research_documents_complete=complete,finished_fabrication_drawing_complete=False,finished_geometry_and_fit_status='held',holds=list(dict.fromkeys(holds))))
    index=dict(schema='osr-controlled-research-documents/1',identities=deepcopy(proposal['identities']),components=components);write('documents.json',encoded(index));write('conversions.json',encoded(conversions))
    source=dict(scope['source_sha256'])
    for name,path in ((PRODUCER,Path(__file__)),(review.CONTRACT,review.ROOT/review.CONTRACT),
                      ('engineering/pilot_delivery/review.py',Path(review.__file__)),('engineering/pilot_delivery/model.py',Path(model.__file__))):
        actual=digest(path)
        if name in source and source[name]!=actual:raise ValueError('Mixed drawing producer/source epoch')
        source[name]=actual
    manifest=dict(schema=SCHEMA,identities=deepcopy(proposal['identities']),proposal_id=proposal['proposal_id'],body_evaluation_id=body['evaluation_id'],source_sha256=source,
        coverage=dict(source_part_ids=sorted(p['id'] for p in proposal['items']),selected_part_ids=list(selected_part_ids),documented_part_ids=sorted(p['part_id'] for p in components),unselected_part_ids=sorted(set(p['id'] for p in proposal['items'])-set(selected_part_ids)),parts=coverage,all_selected_stock_documents_complete=all(p['controlled_research_documents_complete'] for p in coverage),whole_vehicle_finished_drawing_coverage_complete=False),
        declarations_sha256=identity(declared_tolerances_and_process_times),manufacturing_readiness='held',cost_scope='Source direct part/process price retained once; routing times are non-additive declared planning inputs',
        files_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},**FLAGS)
    manifest['manifest_id']=identity(manifest);write('manifest.json',encoded(manifest));return manifest
