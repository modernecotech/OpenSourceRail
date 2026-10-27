"""Gross-stock geometry, mass properties and native CAD for grammar candidates.

Tube ends and joints are not fabricated by an illustration. The current solids
are nominal cut stock; joint mitres, fasteners and assembled overlap remain
explicit open work. No complete installed vehicle mass or clearance is claimed.
"""
from pathlib import Path
from copy import deepcopy
import json,subprocess
import numpy as np
from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded,identity,digest
PRODUCER='engineering/design_search/grammar_geometry.py'


def basis(part):
    a=np.array(part['start_m']);b=np.array(part['end_m']);w=(b-a)/np.linalg.norm(b-a)
    u=np.cross([0.,0.,1.],w)
    if np.linalg.norm(u)<1e-10:u=np.array([1.,0.,0.])
    u=u/np.linalg.norm(u);v=np.cross(w,u);return np.column_stack([u,v,w])


def bounds(part):
    if part['kind']=='box':return part['at_m'],[a+b for a,b in zip(part['at_m'],part['size_m'])]
    R=basis(part);a=np.array(part['start_m']);L=float(np.linalg.norm(np.array(part['end_m'])-a))
    vertices=np.array([a+R@np.array([x,y,z]) for x in (-part['width_m']/2,part['width_m']/2) for y in (-part['height_m']/2,part['height_m']/2) for z in (0.,L)])
    return vertices.min(axis=0).tolist(),vertices.max(axis=0).tolist()


def mass_properties(candidate):
    rows=[]
    for p in candidate['parts']:
        m=p['mass_kg']
        if p['kind']=='box':
            size=np.array(p['size_m']);cg=np.array(p['at_m'])+size/2;J=np.diag([m*(size[(i+1)%3]**2+size[(i+2)%3]**2)/12 for i in range(3)])
        else:
            a=np.array(p['start_m']);b=np.array(p['end_m']);L=float(np.linalg.norm(b-a));cg=(a+b)/2;w,h,t=p['width_m'],p['height_m'],p['wall_m'];A=w*h-(w-2*t)*(h-2*t)
            Iu=(w*h**3-(w-2*t)*(h-2*t)**3)/12;Iv=(h*w**3-(h-2*t)*(w-2*t)**3)/12
            local=np.diag([m*(L*L/12+Iu/A),m*(L*L/12+Iv/A),m*(Iu+Iv)/A]);R=basis(p);J=R@local@R.T
        rows.append((m,cg,J))
    total=sum(m for m,c,j in rows);cg=sum(m*c for m,c,j in rows)/total
    tensor=sum(j+m*(np.dot(c-cg,c-cg)*np.eye(3)-np.outer(c-cg,c-cg)) for m,c,j in rows)
    return dict(candidate_id=candidate['candidate_id'],known_gross_stock_mass_kg=total,known_gross_stock_CG_m=cg.tolist(),known_gross_stock_inertia_kg_m2=tensor.tolist(),
        scope='Nominal cut-stock aggregate only, before unknown joint cuts/hardware and unlocated equipment; complete installed mass, CG and inertia remain unknown',
        complete_installed_mass_kg=None,complete_installed_CG_m=None,complete_installed_inertia_kg_m2=None)


def interface_projection(candidate):
    components=deepcopy(candidate['components']);parts={p['id']:p for p in candidate['parts']}
    for c in components:
        if c['occurrence_id'] in parts:
            lo,hi=bounds(parts[c['occurrence_id']]);c['envelope']=dict(frame_id='vehicle',unit='m',min_m=lo,max_m=hi,kind='occupied',data_validity=dict(validity='supported',source_id='grammar'))
    keepouts=[];W=candidate['parameters']['width_m']
    for p in candidate['physical']['apertures']:
        x0,x1,z0,z1=p['xz_m'];y=p['side']*W/2
        keepouts.append(dict(id=p['id'],frame_id='vehicle',unit='m',min_m=[x0,y-.04,z0],max_m=[x1,y+.04,z1],data_validity=dict(validity='supported',source_id='grammar')))
    return dict(schema='osr-interface-graph/1',candidate_id=candidate['candidate_id'],requirement_revision=candidate['requirement_revision'],
        components=components,connections=deepcopy(candidate['connections']),required_functions=candidate['required_functions'],assembly=candidate['assembly'],keepouts=keepouts,
        frames={'vehicle':dict(unit='m',origin_m=[0,0,0],axes='x longitudinal/y left/z up')},
        sources={'grammar':dict(kind='geometry-definition',sha256=candidate['sources']['engineering/design_search/design_grammar.py'],locator='Candidate physical graph and generated stock',candidate_id=candidate['candidate_id'])})


SCRIPT=r'''
import FreeCAD as A,Part,Import,json,pathlib
out=pathlib.Path(__file__).parent;data=json.loads((out/'input.json').read_text());doc=A.newDocument('OSR_Generative_Stock');objects=[];rows=[]
for i,p in enumerate(data['parts']):
    if p['kind']=='box':shape=Part.makeBox(*[x*1000 for x in p['size_m']],A.Vector(*[x*1000 for x in p['at_m']]))
    elif p['kind']=='oriented-RHS':
        w,h,t,L=[p[k]*1000 for k in ('width_m','height_m','wall_m','length_m')]
        shape=Part.makeBox(w,h,L,A.Vector(-w/2,-h/2,0)).cut(Part.makeBox(w-2*t,h-2*t,L,A.Vector(-w/2+t,-h/2+t,0)))
        m=A.Matrix()
        for r in range(3):
            for c in range(3):setattr(m,'A'+str(r+1)+str(c+1),p['basis'][r][c])
        shape.transformShape(m);shape.translate(A.Vector(*[x*1000 for x in p['start_m']]))
    else:raise ValueError('Unsupported actual primitive')
    v=shape.Volume/1e9
    if not shape.isValid() or abs(v-p['volume_m3'])>max(1e-10,1e-7*p['volume_m3']):raise ValueError('Native gross stock differs:'+p['id'])
    obj=doc.addObject('PartDesign::Feature','Stock_'+str(i));obj.Label=p['id'];obj.Shape=shape
    for k,value in [('CandidateID',data['candidate_id']),('OccurrenceID',p['id']),('Scope','Gross stock; complete installed assembly unqualified')]:obj.addProperty('App::PropertyString',k);setattr(obj,k,value)
    objects.append(obj);rows.append(dict(id=p['id'],volume_m3=v))
doc.recompute();doc.saveAs(str(out/'structure.FCStd'));Import.export(objects,str(out/'structure.step'));A.closeDocument(doc.Name)
doc=A.openDocument(str(out/'structure.FCStd'));actual=[o for o in doc.Objects if hasattr(o,'Shape')];reopened=sum(o.Shape.Volume for o in actual)/1e9
if len(actual)!=len(rows):raise ValueError('Reopened occurrences differ')
A.closeDocument(doc.Name);step=Part.Shape();step.read(str(out/'structure.step'));expected=sum(r['volume_m3'] for r in rows)
if abs(reopened-expected)>max(1e-9,expected*1e-7) or abs(step.Volume/1e9-expected)>max(1e-9,expected*1e-7):raise ValueError('Reopened CAD/STEP stock differs')
(out/'result.json').write_text(json.dumps(dict(candidate_id=data['candidate_id'],occurrences=rows,gross_stock_volume_m3=expected,reopened_volume_m3=reopened,STEP_volume_m3=step.Volume/1e9,FreeCAD_version=list(A.Version()),physical_accepted=False),sort_keys=True)+'\n')
'''


def export(candidate,output):
    output=Path(output).resolve()
    if output.exists():raise ValueError('Fresh native geometry directory required')
    output.mkdir(parents=True);parts=deepcopy(candidate['parts'])
    for p in parts:
        if p['kind']=='oriented-RHS':p.update(length_m=float(np.linalg.norm(np.array(p['end_m'])-p['start_m'])),basis=basis(p).tolist())
    (output/'input.json').write_bytes(encoded(dict(candidate_id=candidate['candidate_id'],parts=parts)));(output/'worker.py').write_text(SCRIPT)
    proc=subprocess.run(['flatpak','run','--filesystem='+str(output),'--command=FreeCADCmd','org.freecad.FreeCAD',str(output/'worker.py')],cwd=output,capture_output=True,timeout=180)
    (output/'stdout.log').write_bytes(proc.stdout);(output/'stderr.log').write_bytes(proc.stderr)
    if proc.returncode or not(output/'result.json').is_file():raise ValueError('Native geometry export failed; retain logs')
    result=json.loads((output/'result.json').read_bytes())
    if result['candidate_id']!=candidate['candidate_id']:raise ValueError('Native geometry used a different candidate')
    manifest=dict(candidate_id=candidate['candidate_id'],source_sha256={PRODUCER:digest(ROOT/PRODUCER)},
        input_id=identity(json.loads((output/'input.json').read_bytes())),files_sha256={p.name:digest(p) for p in output.iterdir() if p.is_file()})
    manifest['manifest_id']=identity(manifest);(output/'manifest.json').write_bytes(encoded(manifest))
    return result


def read_export(candidate,output):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes());r=json.loads((output/'result.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('CAD receipt identity differs')
    if m['candidate_id']!=candidate['candidate_id'] or r['candidate_id']!=candidate['candidate_id']:raise ValueError('CAD candidate differs')
    if m['source_sha256']!={PRODUCER:digest(ROOT/PRODUCER)}:raise ValueError('CAD source differs')
    if m['files_sha256']!={p.name:digest(p) for p in output.iterdir() if p.is_file() and p.name!='manifest.json'}:raise ValueError('CAD payload differs')
    data=json.loads((output/'input.json').read_bytes())
    if identity(data)!=m['input_id'] or data['candidate_id']!=candidate['candidate_id']:raise ValueError('CAD input differs')
    expected={p['id']:p['volume_m3'] for p in candidate['parts']}
    if len(r['occurrences'])!=len(expected) or any(abs(expected[p['id']]-p['volume_m3'])>max(1e-10,1e-7*expected[p['id']]) for p in r['occurrences']):raise ValueError('CAD occurrence stock differs')
    return r
