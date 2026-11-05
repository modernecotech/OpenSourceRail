"""Common SI scene contract and explicit visual-study identities."""
from hashlib import sha256
import json
from math import isfinite, pi, sqrt
from pathlib import Path

FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, movement_authority=False,
             complete_installed_mass=False, installed_mass_complete=False)
SHAPES = {'box', 'cylinder', 'tube', 'sphere', 'profile', 'pipe'}
BASES = {'source-geometry', 'derived-layout', 'proposed-envelope', 'illustrative-tooling'}


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def identity(value):
    return sha256(encoded(value)).hexdigest()


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def vector(value, positive=False):
    if not isinstance(value, (tuple,list)) or len(value) != 3:
        raise ValueError('Three SI coordinates required')
    if any(type(x) not in (int,float) or not isfinite(x) or (positive and x <= 0) for x in value):
        raise ValueError('Finite SI geometry required')
    return list(value)


def number(value, positive=True):
    if type(value) not in (int,float) or not isfinite(value) or (positive and value <= 0):
        raise ValueError('Finite positive dimension required')
    return value


def volume(entity):
    s = entity['shape']
    if s == 'box':
        a,b,c = entity['size_m']
        holes=sum(pi*(h['diameter_m']/2)**2*h.get('length_m',entity['size_m']['xyz'.index(h.get('axis','z'))]) for h in entity.get('holes',[]))
        return a*b*c-holes
    if s in ('cylinder','tube'):
        return pi*(entity['radius_m']**2-entity.get('inner_radius_m',0.)**2)*entity['length_m']
    if s == 'sphere': return 4*pi*entity['radius_m']**3/3
    if s == 'profile':
        p = entity['points_yz_m']
        area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))/2
        return area*entity['length_m']
    return None  # A routed hose/cable envelope is not a material take-off.


def bounds(entity, rendered=False):
    p = entity['at_m'][:]
    if rendered: p=[a+b for a,b in zip(p,entity.get('render_offset_m',[0,0,0]))]
    s=entity['shape']
    if s=='box': return p,[a+b for a,b in zip(p,entity['size_m'])]
    if s in ('cylinder','tube'):
        axis=entity['axis'];length=entity['length_m'];r=entity['radius_m']
        w=[r*sqrt(max(0.,1.-a*a)) for a in axis]
        end=[a+b*length for a,b in zip(p,axis)]
        return [min(a,b)-c for a,b,c in zip(p,end,w)],[max(a,b)+c for a,b,c in zip(p,end,w)]
    if s=='sphere':
        return [a-entity['radius_m'] for a in p],[a+entity['radius_m'] for a in p]
    if s=='profile':
        q=entity['points_yz_m']
        return [p[0],p[1]+min(a[0] for a in q),p[2]+min(a[1] for a in q)], [p[0]+entity['length_m'],p[1]+max(a[0] for a in q),p[2]+max(a[1] for a in q)]
    q=entity['path_m'];r=entity['radius_m']
    return [p[i]+min(a[i] for a in q)-r for i in range(3)],[p[i]+max(a[i] for a in q)+r for i in range(3)]


def validate(assembly):
    if not isinstance(assembly,dict) or not assembly.get('id') or not assembly.get('title'):
        raise ValueError('Named visual assembly required')
    for k in FLAGS:
        if k in assembly and assembly[k] is not False:raise ValueError('Visual model cannot grant '+k)
    if not 1 <= len(assembly['entities']) <= 3500: raise ValueError('Bounded assembly required')
    ids=set()
    for e in assembly['entities']:
        if not isinstance(e.get('id'),str) or not e['id'] or e['id'] in ids: raise ValueError('Unique part IDs required')
        ids.add(e['id'])
        if e['shape'] not in SHAPES or e.get('basis') not in BASES or not e.get('source'):
            raise ValueError('Explicit shape, dimension basis and source required: '+e['id'])
        e['at_m']=vector(e.get('at_m',[0,0,0]));e['render_offset_m']=vector(e.get('render_offset_m',[0,0,0]))
        if e['shape']=='box':
            e['size_m']=vector(e['size_m'],positive=True)
            for h in e.get('holes',[]):
                if h.get('axis','z') not in 'xyz':raise ValueError('Ordinary through-hole axis required')
                number(h['diameter_m'])
        if e['shape'] in ('cylinder','tube'):
            axis=vector(e.get('axis',[0,0,1]));norm=sqrt(sum(a*a for a in axis));number(norm)
            e['axis']=[a/norm for a in axis] if abs(norm-1.)>1e-12 else axis;number(e['length_m'])
        if e['shape'] in ('cylinder','tube','sphere','pipe'): number(e['radius_m'])
        if e['shape']=='tube':
            number(e['inner_radius_m'])
            if e['inner_radius_m'] >= e['radius_m']: raise ValueError('Positive tube wall required')
        if e['shape']=='profile':
            number(e['length_m']);p=e['points_yz_m']
            if len(p)<3 or any(len(a)!=2 or any(type(x) not in (int,float) or not isfinite(x) for x in a) for a in p):
                raise ValueError('Finite closed profile required')
        if e['shape']=='pipe':
            if len(e['path_m'])<2: raise ValueError('Routed envelope needs a path')
            for a in e['path_m']: vector(a)
            if any(a==b for a,b in zip(e['path_m'],e['path_m'][1:])):raise ValueError('Nonzero route segments required')
        v=volume(e)
        if v is not None: number(v)
        if 'source_volume_m3' in e and v is not None:
            expected=number(e['source_volume_m3'])
            if abs(v-expected)>max(1e-10,expected*1e-7): raise ValueError('Source geometry volume differs: '+e['id'])
        for k in FLAGS:
            if k in e and e[k] is not False: raise ValueError('Communication geometry cannot promote '+k)
    for label in assembly.get('labels',[]): vector(label['anchor_m'])
    assembly.update(FLAGS)
    assembly['schema']='osr-visual-assembly/1';assembly['units']='metres'
    assembly['presentation_offsets_are_installed_positions']=False
    assembly['visual_study_id']=identity({k:v for k,v in assembly.items() if k!='visual_study_id'})
    return assembly


def collect(root):
    from . import station,civil,fabrication
    result=[];sources={}
    for producer in (station,civil,fabrication):
        family=producer.generate(Path(root))
        for item in family.get('sources',[]):
            name=item if isinstance(item,str) else item['path']
            path=Path(name)
            if path.is_absolute() or '..' in path.parts or not (Path(root)/path).is_file():
                raise ValueError('Existing repository source required: '+name)
            actual=digest(Path(root)/path)
            if isinstance(item,dict) and actual!=item['sha256']:
                raise ValueError('Producer source changed: '+name)
            sources[name]=actual
        for a in family['assemblies']:
            a.setdefault('family',family['family'])
            a.setdefault('assumptions',[]).extend(family.get('assumptions',[]))
            a.setdefault('references',[]).extend(family.get('references',[]))
            result.append(validate(a))
    if len({a['id'] for a in result})!=len(result):raise ValueError('Unique assembly IDs required')
    for name in ('core.py','station.py','civil.py','fabrication.py'):
        p=Path(root)/'engineering/visual_models'/name
        sources[p.relative_to(root).as_posix()]=digest(p)
    return result,sources
