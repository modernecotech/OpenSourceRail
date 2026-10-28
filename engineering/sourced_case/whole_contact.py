"""Conditional 3D frame/layered-sandwich body with counted finite interfaces.

Geometry-connected is not a qualified joint. This layer never changes frozen
methods or inherits a body result across its proposed physical revisions.
"""
from copy import deepcopy
from pathlib import Path
from math import ceil,fsum,sqrt
import io,json,os,resource,subprocess,sys,tarfile,time
import numpy as np
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import splu
from engineering.station_rail import ROOT
from engineering.station_rail.common import identity,encoded,digest
from engineering.component_registry import make_part,make_occurrence,make_registry,summary
from engineering.component_registry.materials import catalogue
from engineering.reference_cell.vehicles import _mass_properties
from engineering.railway_progress.structures import _basis,_skew,frame_stiffness
from . import layered_structure as panel
FLAGS=panel.FLAGS
PRODUCER='engineering/sourced_case/whole_contact.py'
FROZEN='engineering/railway_progress/structures.py'
G=9.80665


def _selected(row):
    if row['part']['geometry']['kind']!='box' or not any(f in row['part']['functions'] for f in ('primary-body','bogie-interfaces')):return False
    name=row['occurrence']['occurrence_id'].split('/')[1]
    excluded=('floor-face','floor-core','roof-face','roof-core','bond','adhesive','rib-cap','service-panel','captive','retainer','-shaft','-head','-nut','-washer')
    return not any(x in name for x in excluded)


def _geometry(vehicle):
    rows,panels=panel.inventory(vehicle);groups=[]
    for row in rows:
        if _selected(row):groups.append(dict(source=row['occurrence']['occurrence_id'],lower=row['lower'],upper=row['upper'],row=row,kind='frame'))
    for p in panels:
        centre=np.asarray(p['centre_m']);d=np.array([p['length_m'],p['width_m'],p['core_thickness_m']+2*max(f['thickness_m'] for f in p['faces'])+.0024])
        # Actual skin extrema, not an expanded contact tolerance.
        faces=[r for r in rows if r['occurrence']['occurrence_id'] in p['actual_source_occurrences'] and r['occurrence']['occurrence_id'].split('/')[1] in ('floor-face','roof-face')]
        lower=centre-d/2;upper=centre+d/2;lower[2]=min(r['lower'][2] for r in faces);upper[2]=max(r['upper'][2] for r in faces)
        groups.append(dict(source=p['panel_id'],lower=lower,upper=upper,panel=p,kind='sandwich'))
    return rows,panels,groups


def _intersection(a,b):
    lo=np.maximum(a['lower'],b['lower']);hi=np.minimum(a['upper'],b['upper']);d=hi-lo
    if min(d)<-1e-9:return None
    axis=int(np.argmin(d));other=[i for i in range(3) if i!=axis]
    if min(d[other])<=1e-7:return None
    return dict(lower=lo,upper=hi,axis=axis,other=other,area=float(np.prod(d[other])))


def _components(groups,extra=()):
    graph=[set() for _ in groups]
    for i,a in enumerate(groups):
        for j,b in enumerate(groups[:i]):
            if _intersection(a,b) is not None:graph[i].add(j);graph[j].add(i)
    lookup={g['source']:i for i,g in enumerate(groups)}
    for a,b in extra:
        if a in lookup and b in lookup:graph[lookup[a]].add(lookup[b]);graph[lookup[b]].add(lookup[a])
    todo=set(range(len(groups)));out=[]
    while todo:
        front=[todo.pop()];component=set(front)
        while front:
            n=front.pop()
            for m in graph[n]&todo:todo.remove(m);component.add(m);front.append(m)
        out.append(sorted(component))
    return out


def sources(vehicle,root=ROOT):
    out=panel.sources(vehicle,root)
    for path in (PRODUCER,FROZEN,'engineering/railway_progress/__init__.py','engineering/sourced_case/__init__.py'):out[path]=digest(Path(root)/path)
    if out[PRODUCER]!=digest(__file__):raise ValueError('Executing full-body source differs')
    return dict(sorted(out.items()))


def revision(vehicle,root=ROOT):
    """Count minimal finite metal splice/angle routes connecting actual gaps.

    Nearest disconnected physical groups receive rectangular machined angle
    legs, individual end bonds and counted bolt/head/nut/washer retention.
    Actual holes, taper, weld/cure, local bearing and fail-safe proof remain open.
    Bridges are geometry and mass, never a contact tolerance or infinite joint.
    """
    rows,panels,groups=_geometry(vehicle)
    # Counted support stacks connect their exact rib to their cassette.
    extra=[(p['panel_id'],q['source_occurrence_id']) for p in panels for q in p['bearing_patches'] if q['connection_defined']]
    initial=_components(groups,extra);plans=[]
    # Repeated load paths, not just a graph-minimum wall attached at one end.
    mandatory=[]
    uprights=[g for g in groups if '/ring-upright/' in g['source']]
    for upright in uprights:
        x=float((upright['lower'][0]+upright['upper'][0])/2)
        for token in ('/transverse-floor-member/','/roof-transverse-rib/'):
            candidates=[g for g in groups if token in g['source'] and abs(float((g['lower'][0]+g['upper'][0])/2)-x)<1e-7]
            if len(candidates)!=1:raise ValueError('Each ring upright needs actual matching floor and roof transverse members')
            target=candidates[0];gap=np.maximum(np.maximum(upright['lower']-target['upper'],target['lower']-upright['upper']),0.)
            plans.append((upright,target,float(np.linalg.norm(gap))));mandatory.append((upright['source'],target['source']))
    working=[set(c) for c in _components(groups,extra+mandatory)]
    while len(working)>1:
        best=None
        for ca in range(len(working)):
            for cb in range(ca):
                for i in working[ca]:
                    for j in working[cb]:
                        a,b=groups[i],groups[j];gap=np.maximum(np.maximum(a['lower']-b['upper'],b['lower']-a['upper']),0.);distance=float(np.linalg.norm(gap))
                        if best is None or distance<best[0]:best=(distance,ca,cb,i,j)
        distance,ca,cb,i,j=best
        if distance>.20:raise ValueError('Disconnected structural groups require a new architecture, nearest gap exceeds200mm')
        a,b=groups[i],groups[j];plans.append((a,b,distance));working[cb]|=working[ca];working.pop(ca)
    parts={p['physical_definition_id']:deepcopy(p) for p in vehicle['registry']['parts']};added=[];logs=[]
    mats={m['grade_id']:m for m in catalogue()['materials']}
    def add(name,dims,xyz,grade='AL-6082-T6-EXTRUSION',kind='box',axis=2):
        material=mats[grade];rho=material['density_kg_m3'];V=float(np.prod(dims)) if kind=='box' else np.pi*dims['radius']**2*dims['length']
        p=make_part('OSR-'+vehicle['vehicle_id']+'-'+name.upper(),'A',['primary-body'],dict(kind=kind,dimensions_m=dims,net_volume_m3=V),material['material_id'],
            dict(calculated_kg=V*rho['nominal'],lower_bound_kg=V*rho['lower'],upper_bound_kg=V*rho['upper'],evidence_state='calculated'),
            dict(method='machine-fit-drill-bond-bolt-inspect',process='prototype-angle-and-retention',cycle_hours=None,tooling_qualified=False),
            assembly=dict(attachment='finite footprint splice/angle; counted retention; net hole/counterbore details pending',strength_qualified=False,
                removal='Support connected stock, isolate and remove counted bolts, cut sacrificial bond, inspect substrates and replace'),
            evidence=dict(state='design-hypothesis',physical_test_ids=[],source=PRODUCER))
        parts[p['physical_definition_id']]=p;T=np.eye(4);T[:3,3]=xyz
        if kind=='cylinder' and axis!=2:
            R=np.eye(3);R[:,2]=np.eye(3)[:,axis];R[:,axis]=-np.eye(3)[:,2];T[:3,:3]=R
        added.append((name,p,T))
    for n,(a,b,distance) in enumerate(plans):
        da=a['upper']-a['lower'];db=b['upper']-b['lower'];width=np.minimum(.08,np.maximum(.024,np.minimum(da,db)*.8))
        pa=[];pb=[];axes=[]
        for k in range(3):
            if b['lower'][k]>a['upper'][k]+1e-9:pa.append(float(a['upper'][k]));pb.append(float(b['lower'][k]));axes.append(k)
            elif a['lower'][k]>b['upper'][k]+1e-9:pa.append(float(a['lower'][k]));pb.append(float(b['upper'][k]));axes.append(k)
            else:q=float((max(a['lower'][k],b['lower'][k])+min(a['upper'][k],b['upper'][k]))/2);pa.append(q);pb.append(q)
        if not axes:
            # Zero-area edge contact still needs a finite lap beside the edge.
            axes=[int(np.argmin(np.maximum(np.minimum(a['upper'],b['upper'])-np.maximum(a['lower'],b['lower']),0.)))];k=axes[0];pa[k]-=.01;pb[k]+=.01
        # Bring the two end footprints inside their actual stock faces.
        first,last=axes[0],axes[-1]
        for k in range(3):
            if k!=first:pa[k]=float(np.clip(pa[k],a['lower'][k]+width[k]/2,a['upper'][k]-width[k]/2))
            if k!=last:pb[k]=float(np.clip(pb[k],b['lower'][k]+width[k]/2,b['upper'][k]-width[k]/2))
        current=np.array(pa);target=np.array(pb);legnames=[]
        route=axes+[k for k in range(3) if k not in axes and abs(target[k]-current[k])>1e-9]
        for z,k in enumerate(route):
            end=current.copy();end[k]=target[k];delta=end[k]-current[k]
            if abs(delta)<1e-8:continue
            dims=width.copy();lo=min(current[k],end[k]);hi=max(current[k],end[k])
            # Trim the departing leg to the arriving leg's side plane; no duplicate elbow solid volume.
            if z<len(route)-1:hi-=width[k]/2 if delta>0 else 0.;lo+=width[k]/2 if delta<0 else 0.
            if hi-lo<=1e-7:continue
            centre=(current+end)/2;centre[k]=(lo+hi)/2;dims[k]=hi-lo;name='body-splice-'+str(n)+'-leg-'+str(z)
            add(name,dims.tolist(),centre.tolist());legnames.append(name);current=end
        # End plates intentionally overlap parent stock in envelope until matching pockets/bores are detailed.
        # Their installed material is still counted, while overlapping CAD never means net manufacturing acceptance.
        for side,(q,k) in enumerate(((pa,first),(pb,last))):
            d=width.copy();d[k]=.008;name='body-splice-'+str(n)+'-end-plate-'+str(side);add(name,d.tolist(),q)
            # Bolt shaft, head, nut, two washers: every separate item has geometry/mass.
            for j in (-1,1):
                xyz=np.array(q);other=[i for i in range(3) if i!=k][0];xyz[other]+=j*width[other]/4
                add('body-splice-'+str(n)+'-bolt-'+str(side)+'-'+str(j),dict(length=.050,radius=.004),xyz.tolist(),'STEEL-FASTENER-HYPOTHESIS','cylinder',k)
                for item,offset,thick,radius in (('head',.027,.006,.007),('nut',-.027,.007,.007),('washer-a',.023,.0015,.009),('washer-b',-.023,.0015,.009)):
                    pos=xyz.copy();pos[k]+=offset
                    add('body-splice-'+str(n)+'-'+item+'-'+str(side)+'-'+str(j),dict(length=thick,radius=radius),pos.tolist(),'STEEL-FASTENER-HYPOTHESIS','cylinder',k)
        logs.append(dict(source_pair=[a['source'],b['source']],gap_distance_m=distance,endpoints_m=[pa,pb],leg_names=legnames,
            end_footprints_m=[width.tolist(),width.tolist()],end_plate_thickness_m=.008,bolt_diameter_m=.008,bolts_per_end=2,
            net_holes_and_pockets_defined=False,qualified_joint=False))
    occ=deepcopy(vehicle['registry']['occurrences'])
    for car in range(1,7):
        for name,p,T in added:
            moved=T.copy();moved[0,3]+=17.5*(car-1);occ.append(make_occurrence('car-'+str(car)+'/'+name,p,parent_id='car-'+str(car)+'/primary-body',transform=moved.tolist(),scope='vehicle/primary-body'))
    reg=make_registry(vehicle['label']+'; finite whole-body splice revision',list(parts.values()),occ,vehicle['functional_requirements'],
        parent_candidate_id=vehicle['candidate_id'],assemblies=vehicle['registry']['assemblies'])
    result=deepcopy(vehicle);result.pop('evaluation_id');result.update(candidate_id=reg['candidate_id'],registry=reg,summary=summary(reg),label=vehicle['label']+'; finite whole-body splice revision')
    pmap={p['physical_definition_id']:p for p in reg['parts']};massrows=[]
    for o in reg['occurrences']:
        T=np.array(o['transform']);axis='x' if abs(T[0,2])>.9 else 'y' if abs(T[1,2])>.9 else 'z'
        massrows.append(dict(part=pmap[o['part_definition_id']],xyz=T[:3,3].tolist(),axis=axis,car=o['occurrence_id'].split('/')[0]))
    local=[r for r in massrows if r['car']=='car-1'];result['per_car_mass_properties']=_mass_properties(local);result['train_mass_properties']=_mass_properties(massrows)
    result['per_car_occurrences']=len(local);result['per_car_part_definitions']=len(parts);result['per_car_functional_occurrences']={f:sum(f in r['part']['functions'] for r in local) for f in result['functional_requirements']}
    result['whole_body_revision_ancestry']=dict(parent_candidate_id=vehicle['candidate_id'],parent_vehicle_evaluation_id=vehicle['evaluation_id'],initial_components=len(initial),
        counted_splice_plans=logs,mandatory_repeated_ring_paths=len(mandatory),bracket_stock_minimum_cross_dimension_m=.024,added_occurrences_per_car=len(added),mass_upper_delta_per_car_kg=result['per_car_mass_properties']['mass_upper_bound_kg']-vehicle['per_car_mass_properties']['mass_upper_bound_kg'])
    result['manufacturing_plan']=[dict(part_definition_id=p['physical_definition_id'],part_revision_id=p['revision_id'],part_id=p['part_id'],process=p['manufacturing'],
        required_inspections=['dimensions','material-lot','hole-and-fitup','joint-or-retention','damage'],approved_work_instruction=None,qualified_tooling=None) for p in reg['parts']]
    for n,log in enumerate(logs):
        ends=np.asarray(log['endpoints_m']);extent=np.maximum(np.ptp(ends,axis=0)+.08,.08);centre=ends.mean(axis=0);travel=np.array([0.,.3 if centre[1]>=0 else -.3,0.]);T=np.eye(4);T[:3,3]=centre;end=T.copy();end[:3,3]+=travel
        result['assembly_access'].append(dict(id='body-splice-removal-'+str(n),function='primary-body',envelope_dimensions_m=extent.tolist(),
            start_transform=T.tolist(),end_transform=end.tolist(),motion=dict(kind='linear-translation',sample_count=9,translation_m=travel.tolist()),
            swept_AABB_m=dict(min=(np.minimum(centre,centre+travel)-extent/2).tolist(),max=(np.maximum(centre,centre+travel)+extent/2).tolist()),
            tool_access_radius_m=.10,required_tools=['rated-body-support','torque-tool','controlled-bond-cutting-tool'],lifting_device='rated-splice-cradle',
            sequence=['isolate-and-protect','support-connected-body-stock','remove-counted-retention','release-sacrificial-bonds','translate-through-swept-envelope','inspect-and-replace'],
            flexible_service_reserve_m=None,clearance_and_lifting_verified=False,interference_resolution='Body/frame and equipment swept-envelope check and qualified replacement procedure required'))
    result['source_sha256']=sources(vehicle,root);result['evaluation_id']=identity(result);panel._vehicle(result);return result


def request(vehicle,*,mesh_m=1.2,maximum_seconds=240,memory_bytes=3*1024**3,root=ROOT):
    panel._vehicle(vehicle)
    if type(mesh_m) not in (int,float) or not .6<=mesh_m<=1.5:raise ValueError('Bounded whole-body base mesh .6..1.5m required')
    if type(maximum_seconds) is not int or not 1<=maximum_seconds<=240 or type(memory_bytes) is not int or not 1024**3<=memory_bytes<=3*1024**3:raise ValueError('At most240s/3GiB required')
    r=dict(schema='osr-whole-layered-request/1',vehicle=deepcopy(vehicle),candidate_id=vehicle['candidate_id'],vehicle_evaluation_id=vehicle['evaluation_id'],
        mesh_m=[float(mesh_m),float(mesh_m)/2],material_hypotheses=dict(GFRP_E_Pa=20e9,GFRP_G_Pa=4e9,AL_E_Pa=70e9,AL_G_Pa=26e9,
        core_G_Pa=16e6,adhesive_G_Pa_hypothesis=.4e9,adhesive_E_Pa_hypothesis=1e9,frame_contact_strength_allowable_Pa=None),maximum_seconds=maximum_seconds,memory_bytes=memory_bytes,
        source_sha256=sources(vehicle,root),**FLAGS);r['request_id']=identity(r);return r


def _validate(r,root):
    if r!=request(r['vehicle'],mesh_m=r['mesh_m'][0],maximum_seconds=r['maximum_seconds'],memory_bytes=r['memory_bytes'],root=root):raise ValueError('Exact whole-body request required')


def _element_k(e,nodes):
    L,R=_basis(nodes[e['a']],nodes[e['b']],e['local_y']);T=np.zeros((12,12))
    for j in range(4):T[j*3:j*3+3,j*3:j*3+3]=R
    k=frame_stiffness(L,e['EA'],e['EIy'],e['EIz'],e['GJ'],1.,1.)
    if e.get('Sy') is not None:
        # Local z translation / local y rotation has opposite slope sign.
        idx=[2,4,8,10];Q=np.diag([1.,-1.,1.,-1.]);k[np.ix_(idx,idx)]=Q@panel.timoshenko_stiffness(L,e['EIy'],e['Sy'])@Q
    return T.T@k@T,k,T


def mechanical_joint_rank(links):
    """Six relative rigid freedoms from finite physical quadrature patches.

    Rotation columns are normalized with the actual patch extent. Rank is a
    conditional kinematic check, never a joint-strength or material approval.
    """
    groups={}
    for link in links:groups.setdefault(tuple(sorted(link['source_pair'])),[]).append(link)
    output=[]
    for pair,rows in sorted(groups.items()):
        points=np.asarray([r['point'] for r in rows]);origin=points.mean(axis=0);length=max(1e-9,float(np.linalg.norm(np.ptp(points,axis=0))));K=np.zeros((6,6))
        for row in rows:
            B=np.c_[np.eye(3),-_skew(np.asarray(row['point'])-origin)/length]
            K+=B.T@np.diag(row['stiffness_N_m'])@B
        ev=np.linalg.eigvalsh(K);largest=max(1e-300,float(ev[-1]));rank=int(np.count_nonzero(ev>largest*1e-12))
        output.append(dict(source_pair=list(pair),rank=rank,relative_eigenvalue=float(ev[0]/largest),normalization_length_m=length,
            quadrature_points=len(rows),strength_qualified=False))
    return output


def build(vehicle,mesh_m):
    rows,panels,groups=_geometry(vehicle);nodes=[];elements=[];links=[]
    def node(x):nodes.append(np.asarray(x).tolist());return len(nodes)-1
    for group in groups:
        group['nodes']=[];group['element_start']=len(elements)
        if group['kind']=='frame':
            row=group['row'];d=row['dimensions'];R=row['rotation'];c=row['position'];axis=int(np.argmax(d));other=[i for i in range(3) if i!=axis]
            L=float(d[axis]);n=max(2,int(ceil(L/mesh_m)));n+=n%2;ids=[]
            for x in np.linspace(-L/2,L/2,n+1):ids.append(node(c+R[:,axis]*x))
            width,depth=float(d[other[0]]),float(d[other[1]]);E=70e9 if row['grade'].startswith('AL-') else 20e9;Gs=26e9 if row['grade'].startswith('AL-') else 4e9
            A=width*depth;Iy=width*depth**3/12;Iz=depth*width**3/12;aa=max(width,depth);bb=min(width,depth);J=aa*bb**3*(1/3-.21*bb/aa*(1-bb**4/(12*aa**4)))
            for a,b in zip(ids[:-1],ids[1:]):elements.append(dict(a=a,b=b,EA=E*A,EIy=E*Iy,EIz=E*Iz,GJ=Gs*J,local_y=R[:,other[0]].tolist(),
                source=group['source'],scope='actual-stock-frame',area_m2=A,depth_m=depth,EI_stress_E_Pa=E))
            group['nodes']=ids
        else:
            p=group['panel'];nx=max(2,int(ceil(p['length_m']/mesh_m)));ny=max(2,int(ceil(p['width_m']/mesh_m)));grid={};z=p['section']['neutral_axis_m']
            for i in range(nx+1):
                for j in range(ny+1):grid[i,j]=node([p['origin_x_m']+p['length_m']*i/nx,-p['width_m']/2+p['width_m']*j/ny,z])
            for direction in (0,1):
                na,nb=(nx,ny) if direction==0 else (ny,nx);spanwidth=p['width_m'] if direction==0 else p['length_m']
                for i in range(na):
                    for j in range(nb+1):
                        width=spanwidth/nb*(.5 if j in (0,nb) else 1.);scale=width/p['width_m'];section=p['section'];tf=sum(f['thickness_m'] for f in p['faces']);h=section['face_centre_separation_m']
                        a,b=(grid[i,j],grid[i+1,j]) if direction==0 else (grid[j,i],grid[j,i+1]);E=fsum(f['E_Pa']*f['thickness_m'] for f in p['faces'])/tf;Gs=26e9 if p['faces'][0]['basis'].startswith('hulamin') else 4e9
                        elements.append(dict(a=a,b=b,EA=section['EA_N']*scale,EIy=section['EI_Nm2']*scale,EIz=E*tf*width**3/12,
                            GJ=Gs*width*tf*h*h/2,Sy=section['core_shear_stiffness_N']*scale,local_y=[0.,1.,0.] if direction==0 else [1.,0.,0.],
                            source=group['source'],scope='layered-orthogonal-sandwich-grillage',area_m2=width*tf,depth_m=h,EI_stress_E_Pa=E))
            group['nodes']=list(grid.values());group['grid']=dict(nx=nx,ny=ny,indices={str(i)+','+str(j):n for (i,j),n in grid.items()})
        group['element_indices']=list(range(group['element_start'],len(elements)))
    xyz=np.asarray(nodes)
    # Every numerical cassette grid must match the actual registered component.
    for g in groups:
        if g['kind']!='sandwich':continue
        actual=next(r for r in rows if r['occurrence']['occurrence_id']==g['source'])
        points=xyz[g['nodes']]
        if not np.allclose(np.ptp(points,axis=0)[:2],actual['dimensions'][:2],rtol=0.,atol=1e-10):raise ValueError('Numerical cassette dimensions differ from actual stock')
        if not np.allclose((points.min(0)+points.max(0))[:2]/2,actual['position'][:2],rtol=0.,atol=1e-10):raise ValueError('Numerical cassette pose differs from actual stock')
    def connect(a,b,point,axis,area,lengths=None,stiffness=None):
        ia=min(a['nodes'],key=lambda n:np.linalg.norm(xyz[n]-point));ib=min(b['nodes'],key=lambda n:np.linalg.norm(xyz[n]-point))
        da=a['upper']-a['lower'];db=b['upper']-b['lower'];travel=max(.0006,float(da[axis]+db[axis])/2)
        if stiffness is None:
            # Finite local compliance based on actual footprint/stock thickness;
            # a conditional contact law, not a manufactured weld/bond certificate.
            Ea=70e9 if a.get('row',{}).get('grade','').startswith('AL-') else 20e9
            Eb=70e9 if b.get('row',{}).get('grade','').startswith('AL-') else 20e9
            Ga=26e9 if a.get('row',{}).get('grade','').startswith('AL-') else 4e9
            Gb=26e9 if b.get('row',{}).get('grade','').startswith('AL-') else 4e9
            ks=np.full(3,min(Ga,Gb)*area/travel);ks[axis]=min(Ea,Eb)*area/travel
        else:ks=np.asarray(stiffness)
        da,Na=contact_mapping(a,point,nodes,elements);db,Nb=contact_mapping(b,point,nodes,elements)
        ids=sorted(set(da+db));B=np.zeros((3,len(ids)));where={d:i for i,d in enumerate(ids)}
        for j,d in enumerate(da):B[:,where[d]]+=Na[:,j]
        for j,d in enumerate(db):B[:,where[d]]-=Nb[:,j]
        links.append(dict(a=ia,b=ib,dofs=ids,interpolation_B=B.tolist(),point=np.asarray(point).tolist(),stiffness_N_m=ks.tolist(),source_pair=[a['source'],b['source']],
            footprint_area_m2=area,contact_normal_axis=axis,qualified_joint=False))
    for i,a in enumerate(groups):
        for b in groups[:i]:
            overlap=_intersection(a,b)
            if overlap is None:continue
            for q,area in contact_quadrature(a,b,overlap['lower'],overlap['upper'],overlap['axis'],xyz):
                connect(a,b,q,overlap['axis'],area)
    lookup={g['source']:g for g in groups}
    for p in panels:
        for patch in p['bearing_patches']:
            if not patch['connection_defined']:continue
            a,b=lookup[p['panel_id']],lookup[patch['source_occurrence_id']];centre=np.array([p['origin_x_m']+(patch['a_m']+patch['b_m'])/2,0.,float(b['upper'][2])]);dx=patch['b_m']-patch['a_m'];dy=patch['width_m']
            low=centre-np.array([dx/2,dy/2,0.]);high=centre+np.array([dx/2,dy/2,0.])
            compliance=p['core_thickness_m']/(p['core_G_Pa']*patch['area_m2'])
            for oid in patch['counted_support_stack']:
                row=next(r for r in rows if r['occurrence']['occurrence_id']==oid);Gs=26e9 if row['grade'].startswith('AL-') else .4e9
                compliance+=float(row['dimensions'][2])/(Gs*patch['area_m2'])
            for q,area in contact_quadrature(a,b,low,high,2,xyz):
                fraction=area/patch['area_m2'];kn=patch['kn_N_m']*fraction;kt=1/compliance*fraction
                connect(a,b,q,2,area,stiffness=[kt,kt,kn])
    joint_rank=mechanical_joint_rank(links)
    components=_components(groups,[l['source_pair'] for l in links]);supports=[]
    for point in vehicle['interfaces']['body_secondary_hardpoint_positions_m']:
        choices=[g for g in groups if '/body-bogie-hardpoint/' in g['source']];indices=[n for g in choices for n in g['nodes']]
        supports.append(min(indices,key=lambda n:np.linalg.norm(xyz[n]-point)))
    fixed=sorted(set([6*n+2 for n in supports]+[6*supports[0],6*supports[0]+1,6*supports[2]+1]))
    # Keep only actual node/element/group data, avoiding NumPy objects in receipts.
    public=[]
    for g in groups:public.append(dict(source=g['source'],lower=g['lower'].tolist(),upper=g['upper'].tolist(),kind=g['kind'],nodes=g['nodes'],grid=g.get('grid'),element_indices=g['element_indices']))
    return dict(nodes=nodes,elements=elements,links=links,groups=public,fixed_dofs=fixed,support_nodes=supports,
        components=[[groups[i]['source'] for i in c] for c in components],joint_mechanical_rank=joint_rank,mesh_m=mesh_m),rows,panels


def assemble(model):
    rows=[];cols=[];values=[]
    def add(ids,K):
        # Exact-zero sparsity only; array chunks avoid Python-object triplet
        # memory growth under the explicit3GiB native-worker budget.
        ii,jj=np.nonzero(K);indices=np.asarray(ids,dtype=np.int32);rows.append(indices[ii]);cols.append(indices[jj]);values.append(K[ii,jj])
    for e in model['elements']:
        ids=[6*e['a']+i for i in range(6)]+[6*e['b']+i for i in range(6)];add(ids,_element_k(e,model['nodes'])[0])
    for link in model['links']:
        B=np.asarray(link['interpolation_B']);K=B.T@np.diag(link['stiffness_N_m'])@B
        add(link['dofs'],K)
    return coo_matrix((np.concatenate(values),(np.concatenate(rows),np.concatenate(cols))),shape=(6*len(model['nodes']),)*2).tocsc()


def loads(vehicle,model,rows,panels):
    xyz=np.asarray(model['nodes']);groups={g['source']:g for g in model['groups']};size=len(xyz)*6;bindings=[];base=np.zeros(size)
    def apply(F,position,force):
        position=np.asarray(position);roof=position[2]>3.4
        candidates=[p for p in panels if p['kind']==('roof' if roof else 'floor')];p=min(candidates,key=lambda p:max(p['origin_x_m']-position[0],0.,position[0]-p['origin_x_m']-p['length_m']))
        g=groups[p['panel_id']];grid=g['grid'];nx,ny=grid['nx'],grid['ny'];u=np.clip((position[0]-p['origin_x_m'])/p['length_m']*nx,0.,nx);v=np.clip((position[1]+p['width_m']/2)/p['width_m']*ny,0.,ny)
        i=min(nx-1,int(u));j=min(ny-1,int(v));u-=i;v-=j
        for di,dj,w in ((0,0,(1-u)*(1-v)),(1,0,u*(1-v)),(0,1,(1-u)*v),(1,1,u*v)):
            n=grid['indices'][str(i+di)+','+str(j+dj)];f=np.asarray(force)*w;F[6*n:6*n+3]+=f;F[6*n+3:6*n+6]+=np.cross(position-xyz[n],f)
    upper=0.;direct=0.
    panel_sources={oid:p['panel_id'] for p in panels for oid in p['actual_source_occurrences']}
    for row in rows:
        mass=row['part']['mass']['upper_bound_kg'];upper+=mass;oid=row['occurrence']['occurrence_id']
        if 'running-gear' in row['part']['functions']:direct+=mass;continue
        group=groups.get(panel_sources.get(oid,oid))
        if group is not None:
            ids=group['nodes'];grid=group['grid']
            if grid:
                weights=[(.5 if i in (0,grid['nx']) else 1.)*(.5 if j in (0,grid['ny']) else 1.) for i in range(grid['nx']+1) for j in range(grid['ny']+1)]
            else:weights=[.5]+[1.]*(len(ids)-2)+[.5]
            total=sum(weights)
            for n,w in zip(ids,weights):base[6*n+2]-=mass*G*w/total
        elif row['part']['geometry']['kind']=='envelope':
            d=row['dimensions']
            for dx,dy in ((-1,-1),(-1,1),(1,-1),(1,1)):
                apply(base,row['position']+np.array([dx*d[0]/(2*sqrt(3)),dy*d[1]/(2*sqrt(3)),0.]),[0.,0.,-mass*G/4])
        else:apply(base,row['position'],[0.,0.,-mass*G])
        bindings.append(dict(occurrence_id=oid,mass_upper_kg=mass,position_m=row['position'].tolist(),internal_CG_known=row['part']['geometry']['kind']!='envelope'))
    normal=base.copy();crowd=base.copy();seats=[r['position'] for r in rows if panel._is(r,'seat-pan')]
    for r in rows:
        if panel._is(r,'two-place-wall-bench'):seats.extend([r['position']+[-.24,0.,0.],r['position']+[.24,0.,0.]])
    seats.extend(np.array(w['center_m']) for w in vehicle['interfaces']['wheelchair_spaces_per_car'])
    if len(seats)!=46:raise ValueError('Actual44seat+2WC loads required')
    for position in seats:apply(normal,position,[0.,0.,-75*G])
    for x in np.linspace(.5,16.5,16):
        for y in np.linspace(-1.15,1.15,10):apply(crowd,[x,y,1.65],[0.,0.,-75*G])
    out=[('empty-upper',base),('normal-upper',normal),('crowd160-upper',crowd)]
    for name,token,axis,accel in (('brake-normal',None,0,.6),('door-lateral','door-',1,.6),('HVAC-lateral','HVAC-',1,.6),('solar-lateral','solar-',1,.6)):
        F=normal.copy()
        for row in rows:
            if 'running-gear' in row['part']['functions']:continue
            if token is None or token.lower() in row['occurrence']['occurrence_id'].lower():
                f=np.zeros(3);f[axis]=row['part']['mass']['upper_bound_kg']*accel;apply(F,row['position'],f)
        out.append((name,F))
    for name,token,force in (('fin-launch-demand','passive-aluminium-fin',6*(upper+3450)*.4),('coupler-trailing-demand','coupler-drawgear',5*(upper+3450)*.6)):
        F=normal.copy();targets=[r for r in rows if token in r['occurrence']['occurrence_id']]
        if not targets:raise ValueError('Actual fin/coupler interface required')
        for r in targets:apply(F,r['position'],[force/len(targets),0.,0.])
        out.append((name,F))
    return out,dict(total_upper_mass_kg=upper,direct_running_gear_upper_mass_kg=direct,supported_upper_mass_kg=upper-direct,
        upper_mass_bindings=bindings,pax_normal=46,pax_crowd=160,load_transfer='Finite floor/roof panel area bilinear weights with exact point-offset moments; actual equipment support details remain conditional')


def solve(model,cases):
    if len(model['components'])!=1:return dict(execution='definition-mechanism',reason='Disconnected actual geometry/interface graph',components=model['components'])
    if any(j['rank']<6 for j in model['joint_mechanical_rank']):return dict(execution='finite-joint-mechanism',reason='Finite footprint fails six relative rigid freedoms',joints=[j for j in model['joint_mechanical_rank'] if j['rank']<6])
    K=assemble(model);fixed=np.array(model['fixed_dofs']);free=np.setdiff1d(np.arange(K.shape[0]),fixed);diagonal=K.diagonal()[free]
    # Drop truly inactive zero rows only, never mass-loaded orphan freedoms.
    inactive=free[diagonal<=1e-20]
    if any(np.any(abs(F[inactive])>1e-10) for _,F in cases):return dict(execution='loaded-orphan-dofs',dofs=inactive.tolist())
    free=free[diagonal>1e-20];scale=1/np.sqrt(K.diagonal()[free]);D=diags(scale)
    try:factor=splu((D@K[free][:,free]@D).tocsc())
    except RuntimeError as error:return dict(execution='numerical-mechanism',reason=str(error))
    pivot=abs(factor.U.diagonal());ratio=float(pivot.min()/pivot.max())
    if ratio<1e-14:return dict(execution='numerical-mechanism',reason='Normalized nearzero factor pivot',pivot_ratio=ratio)
    results=[];xyz=np.asarray(model['nodes'])
    for name,F in cases:
        u=np.zeros(K.shape[0]);u[free]=scale*factor.solve(scale*F[free]);reaction=K@u-F;res=float(np.linalg.norm(reaction[free])/max(1.,np.linalg.norm(F)));energy=float(u@(K@u)/2);work=float(u@F/2);R=np.zeros_like(u);R[fixed]=reaction[fixed];total=(F+R).reshape(-1,6)
        witnesses={}
        for e in model['elements']:
            ids=[6*e['a']+i for i in range(6)]+[6*e['b']+i for i in range(6)];_,k,T=_element_k(e,model['nodes']);f=k@T@u[ids]
            stress=abs(f[0])/e['area_m2']+max(abs(f[4]),abs(f[10]))*e['EI_stress_E_Pa']*e['depth_m']/2/e['EIy']
            row=dict(source_occurrence_id=e['source'],normal_stress_proxy_Pa=float(stress),end_forces_N_Nm=f.tolist(),approved_margin=None)
            if e['source'] not in witnesses or witnesses[e['source']]['normal_stress_proxy_Pa']<stress:witnesses[e['source']]=row
        joint_witnesses={}
        for link in model['links']:
            a,b=link['a'],link['b'];point=np.asarray(link['point']);delta=np.asarray(link['interpolation_B'])@u[link['dofs']];force=np.asarray(link['stiffness_N_m'])*delta
            key='|'.join(link['source_pair']);stress=float(np.linalg.norm(force)/link['footprint_area_m2'])
            witness=dict(source_pair=link['source_pair'],point_m=link['point'],force_N=force.tolist(),relative_displacement_m=delta.tolist(),footprint_area_m2=link['footprint_area_m2'],
                traction_proxy_Pa=stress,strain_energy_J=float(np.dot(force,delta)/2),approved_joint_margin=None)
            if key not in joint_witnesses or joint_witnesses[key]['traction_proxy_Pa']<stress:joint_witnesses[key]=witness
        q=u.reshape(-1,6);results.append(dict(name=name,displacements_m_rad=q.tolist(),maximum_translation_m=float(np.linalg.norm(q[:,:3],axis=1).max()),
            maximum_rotation_rad=float(np.linalg.norm(q[:,3:],axis=1).max()),free_relative_residual=res,relative_energy_residual=abs(energy-work)/max(1.,abs(energy)),
            strain_energy_J=energy,external_work_J=work,force_balance_residual_N=total[:,:3].sum(axis=0).tolist(),
            moment_balance_residual_Nm=(total[:,3:]+np.cross(xyz,total[:,:3])).sum(axis=0).tolist(),
            support_reactions=[dict(dof=int(i),reaction=float(reaction[i])) for i in fixed],stress_witnesses=list(witnesses.values()),joint_witnesses=list(joint_witnesses.values()),
            numerical_valid=bool(res<1e-6 and abs(energy-work)/max(1.,abs(energy))<1e-6),
            linear_kinematic_domain_suspect=bool(np.linalg.norm(q[:,3:],axis=1).max()>.1 or np.linalg.norm(q[:,:3],axis=1).max()>.17),
            approved_strength_margin=None,approved_clearance_limit_m=None))
    return dict(execution='completed',pivot_ratio=ratio,inactive_unloaded_dofs=inactive.tolist(),cases=results)


def evaluate(vehicle,*,root=ROOT,**options):
    r=request(vehicle,root=root,**options);out=[]
    for mesh in r['mesh_m']:
        model,rows,panels=build(vehicle,mesh);cases,mass=loads(vehicle,model,rows,panels);out.append(dict(model=model,mass=mass,response=solve(model,cases)))
    value=dict(schema='osr-whole-layered-evaluation/1',candidate_id=vehicle['candidate_id'],vehicle_evaluation_id=vehicle['evaluation_id'],request_id=r['request_id'],
        execution='completed' if all(x['response']['execution']=='completed' for x in out) else 'definition-or-numerical-hold',results=out,source_sha256=r['source_sha256'],
        method_benchmark=panel.benchmarks(),continuous_I_section_benchmark=continuous_I_section_benchmark(),material_hypotheses=r['material_hypotheses'],whole_body_conditional_model_executed=all(x['response']['execution']=='completed' for x in out),
        numerical_cases_valid=sum(c.get('numerical_valid',False) for x in out for c in x['response'].get('cases',[])),
        kinematic_cases_in_domain=sum(not c.get('linear_kinematic_domain_suspect',True) for x in out for c in x['response'].get('cases',[])),
        physical_strength_allowables=None,physical_joint_allowables=None,actual_laminate_schedule=None,
        limitations=['Conditional 3D frame/layered orthogonal grillage, not full continuum shell/ply or nonlinear buckling/crash/fatigue/fire proof',
            'Finite actual overlap patches use explicit local material-compliance contact hypotheses; manufactured joint/cure/bolted bearing allowables remain open',
            'Purchased equipment internal CG, mounting internals, spacers/angles net bores and local peel/bearing remain unqualified',
            'No functional clearance limit is invented; large response is a model/domain/refinement finding, not automatic body rejection'],**FLAGS)
    if value['execution']=='completed':value['refinement']=[dict(case=a['name'],coarse_max_translation_m=a['maximum_translation_m'],fine_max_translation_m=b['maximum_translation_m'],
        relative_change=abs(a['maximum_translation_m']-b['maximum_translation_m'])/max(1e-20,b['maximum_translation_m'])) for a,b in zip(out[0]['response']['cases'],out[1]['response']['cases'])]
    else:value['refinement']=None
    value['evaluation_id']=identity(value);return value


def run(r,output,*,root=ROOT):
    _validate(r,root);folder=Path(output).resolve()
    if folder.exists():raise ValueError('Fresh immutable whole-body run required')
    folder.mkdir(parents=True);(folder/'input.json').write_bytes(encoded(r))
    with tarfile.open(folder/'sources.tar','w') as archive:
        for name,expected in r['source_sha256'].items():
            raw=(Path(root)/name).read_bytes()
            if digest(Path(root)/name)!=expected:raise ValueError('Source changed before numerical worker')
            item=tarfile.TarInfo(name);item.size=len(raw);item.mode=0o444;archive.addfile(item,io.BytesIO(raw))
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(r['memory_bytes'],r['memory_bytes']));resource.setrlimit(resource.RLIMIT_CPU,(r['maximum_seconds'],r['maximum_seconds']+1))
    script='from engineering.sourced_case.whole_contact import _worker;_worker('+repr(str(folder))+','+repr(str(Path(root).resolve()))+')';start=time.monotonic();code=None;reason=None;stdout=b'';stderr=b''
    try:
        result=subprocess.run([sys.executable,'-c',script],cwd=root,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1'),
            preexec_fn=limits,timeout=r['maximum_seconds'],stdout=subprocess.PIPE,stderr=subprocess.PIPE);code=result.returncode;stdout=result.stdout;stderr=result.stderr
        if code:reason='Numerical worker exit '+str(code)
    except subprocess.TimeoutExpired as error:reason='Numerical wall timeout';stdout=error.stdout or b'';stderr=error.stderr or b''
    (folder/'stdout.log').write_bytes(stdout);(folder/'stderr.log').write_bytes(stderr)
    if not (folder/'result.json').exists():(folder/'result.json').write_bytes(encoded(dict(schema='osr-whole-layered-failure/1',request_id=r['request_id'],candidate_id=r['candidate_id'],execution='failed',reason=reason or 'Missing worker output',**FLAGS)))
    report=dict(schema='osr-whole-layered-package/1',candidate_id=r['candidate_id'],request_id=r['request_id'],source_sha256=r['source_sha256'],
        returncode=code,failure=reason,elapsed_s=time.monotonic()-start,resource_limits=dict(address_space_bytes=r['memory_bytes'],wall_timeout_s=r['maximum_seconds']),
        isolation='Ordinary subprocess with RLIMIT_AS/RLIMIT_CPU and wall timeout; no filesystem/network sandbox',python_sha256=digest(sys.executable),numpy_version=np.__version__,
        files={p.name:dict(sha256=digest(p),bytes=p.stat().st_size) for p in folder.iterdir()},**FLAGS)
    report['package_id']=identity(report);(folder/'manifest.json').write_bytes(encoded(report));return report


def _worker(folder,root):
    folder=Path(folder);r=json.loads((folder/'input.json').read_text());_validate(r,root)
    value=evaluate(r['vehicle'],root=root,mesh_m=r['mesh_m'][0],maximum_seconds=r['maximum_seconds'],memory_bytes=r['memory_bytes'])
    (folder/'result.json').write_bytes(encoded(value))


def verify(output,*,root=ROOT,require_current_source=True):
    from pathlib import PurePosixPath
    from hashlib import sha256
    folder=Path(output)
    if {p.name for p in folder.iterdir()}!=panel.FILES:raise ValueError('Closed whole-body package inventory differs')
    manifest=json.loads((folder/'manifest.json').read_text())
    if manifest['package_id']!=identity({k:v for k,v in manifest.items() if k!='package_id'}):raise ValueError('Package identity differs')
    if set(manifest['files'])!=panel.FILES-{'manifest.json'}:raise ValueError('Package payload set differs')
    for name,item in manifest['files'].items():
        path=folder/name
        if path.is_symlink() or not path.is_file() or path.stat().st_size!=item['bytes'] or digest(path)!=item['sha256']:raise ValueError('Payload identity differs')
    if (folder/'sources.tar').stat().st_size>256*1024**2:raise ValueError('Source archive size limit')
    with tarfile.open(folder/'sources.tar') as archive:
        members=archive.getmembers();names=[m.name for m in members]
        if len(names)!=len(set(names)) or set(names)!=set(manifest['source_sha256']):raise ValueError('Source inventory/duplicates differ')
        total=0
        for member in members:
            if not member.isfile() or member.name.startswith('/') or '..' in PurePosixPath(member.name).parts or '\\' in member.name:raise ValueError('Unsafe source member')
            total+=member.size
            if member.size>32*1024**2 or total>256*1024**2:raise ValueError('Source size limit')
            if sha256(archive.extractfile(member).read()).hexdigest()!=manifest['source_sha256'][member.name]:raise ValueError('Archived source differs')
    r=json.loads((folder/'input.json').read_text());value=json.loads((folder/'result.json').read_text())
    if r['request_id']!=identity({k:v for k,v in r.items() if k!='request_id'}) or r['source_sha256']!=manifest['source_sha256']:raise ValueError('Request/source identity differs')
    panel._vehicle(r['vehicle'])
    if require_current_source:_validate(r,root)
    if any(r['candidate_id']!=obj['candidate_id'] or r['request_id']!=obj['request_id'] for obj in (manifest,value)):raise ValueError('Mixed candidate or request')
    if any(obj.get(k) is not False for obj in (r,value,manifest) for k in FLAGS):raise ValueError('Package grants unsupported approval')
    if value['execution']!='failed':
        if value['evaluation_id']!=identity({k:v for k,v in value.items() if k!='evaluation_id'}):raise ValueError('Evaluation identity differs')
        if value['source_sha256']!=r['source_sha256'] or value['vehicle_evaluation_id']!=r['vehicle_evaluation_id']:raise ValueError('Evaluation/source input differs')
        if not value['method_benchmark']['benchmark_pass'] or not value['continuous_I_section_benchmark']['benchmark_pass']:raise ValueError('Independent benchmark failed')
    report=dict(package_id=manifest['package_id'],candidate_id=r['candidate_id'],evaluation_id=value.get('evaluation_id'),execution=value['execution'],
        recorded_source_payload_verified=True,current_source_verified=require_current_source,current_numerical_recomputed=False,**FLAGS)
    report['verification_id']=identity(report);return report


def beam_section_shape(e,nodes,point):
    """Exact homogeneous EB/Timoshenko centre-line displacement and rotation."""
    a,b=np.asarray(nodes[e['a']]),np.asarray(nodes[e['b']]);L,R=_basis(a,b,e['local_y']);s=float(np.clip(np.dot(np.asarray(point)-a,R[0])/L,0.,1.));N=np.zeros((6,12))
    for d in (0,3):N[d,d]=1-s;N[d,d+6]=s
    for translation,rotation,sign,phi in ((1,5,1.,0.),(2,4,-1.,12*e['EIy']/(e['Sy']*L*L) if e.get('Sy') else 0.)):
        indices=[translation,rotation,translation+6,rotation+6];q=1+phi
        H=np.array([1+phi-phi*s-3*s*s+2*s**3,L*((1+phi/2)*s-(2+phi/2)*s*s+s**3),phi*s+3*s*s-2*s**3,L*(-phi*s/2+(phi/2-1)*s*s+s**3)])/q
        Ht=np.array([6*s*(s-1)/L,(1-s)*(1+phi-3*s),6*s*(1-s)/L,s*(3*s-2+phi)])/q
        S=np.diag([1.,sign,1.,sign]);N[translation,indices]=H@S;N[rotation,indices]=sign*Ht@S
    T=np.zeros((12,12));Q=np.zeros((6,6))
    for i in range(4):T[i*3:i*3+3,i*3:i*3+3]=R
    Q[:3,:3]=R.T;Q[3:,3:]=R.T;centre=a+R[0]*(s*L)
    return Q@N@T,centre


def contact_mapping(group,point,nodes,elements):
    point=np.asarray(point)
    if group['kind']=='frame':
        def distance(e):
            a,b=np.asarray(nodes[e['a']]),np.asarray(nodes[e['b']]);v=b-a;t=np.clip(np.dot(point-a,v)/np.dot(v,v),0.,1.);return np.linalg.norm(point-a-t*v)
        e=min((elements[i] for i in group['element_indices']),key=distance);N,centre=beam_section_shape(e,nodes,point)
        B=np.c_[np.eye(3),-_skew(point-centre)]@N;return [6*e['a']+i for i in range(6)]+[6*e['b']+i for i in range(6)],B
    grid=group['grid'];xyz=np.asarray(nodes);lo=xyz[group['nodes']].min(0);hi=xyz[group['nodes']].max(0);nx,ny=grid['nx'],grid['ny'];u=float(np.clip((point[0]-lo[0])/(hi[0]-lo[0])*nx,0.,nx));v=float(np.clip((point[1]-lo[1])/(hi[1]-lo[1])*ny,0.,ny));i=min(nx-1,int(u));j=min(ny-1,int(v));u-=i;v-=j;ids=[];blocks=[]
    for di,dj,w in ((0,0,(1-u)*(1-v)),(1,0,u*(1-v)),(0,1,(1-u)*v),(1,1,u*v)):
        n=grid['indices'][str(i+di)+','+str(j+dj)];ids.extend(6*n+k for k in range(6));projected=np.array([np.clip(point[0],lo[0],hi[0]),np.clip(point[1],lo[1],hi[1]),lo[2]]);blocks.append(w*np.c_[np.eye(3),-_skew(point-projected)])
    return ids,np.concatenate(blocks,axis=1)


def contact_quadrature(a,b,lower,upper,axis,nodes):
    """Integrate piecewise fields over BOTH actual surface discretizations."""
    other=[i for i in range(3) if i!=axis];cuts=[]
    for k in other:
        xs=[float(lower[k]),float(upper[k])]
        xs.extend(float(nodes[n][k]) for g in (a,b) for n in g['nodes'] if lower[k]+1e-10<nodes[n][k]<upper[k]-1e-10)
        cuts.append(sorted(set(round(x,12) for x in xs)))
    for x0,x1 in zip(cuts[0][:-1],cuts[0][1:]):
        for y0,y1 in zip(cuts[1][:-1],cuts[1][1:]):
            if min(x1-x0,y1-y0)<=1e-12:continue
            for u,v in ((-1,-1),(-1,1),(1,-1),(1,1)):
                q=(np.asarray(lower)+upper)/2;q[other[0]]=(x0+x1)/2+u*(x1-x0)/(2*sqrt(3));q[other[1]]=(y0+y1)/2+v*(y1-y0)/(2*sqrt(3))
                yield q,(x1-x0)*(y1-y0)/4


def continuous_I_section_benchmark():
    """Independent pure-bending patch test, including continuous contact slip.

    Three actual pieces, common curvature and face-centroid axial strains.
    The parallel-axis energy is an independent exact cross-section integral.
    No load-introduction/end-boundary or body approval is claimed by this test.
    """
    E=70e9;L=2.;curvature=.001;pieces=[(.008,.12,0.),(.1,.008,-.064),(.1,.008,.064)];expected=E*sum(b*t**3/12+b*t*z*z for b,t,z in pieces)*curvature**2*L/2;runs=[]
    for divisions in (4,8):
        energy=0.;maxslip=0.;allnodes=[];allelements=[];groups=[];U=[]
        for index,(b,t,z) in enumerate(pieces):
            ids=[];start=len(allelements)
            for x in np.linspace(0.,L,divisions+1):ids.append(len(allnodes));allnodes.append([x,0.,z]);U.extend([-curvature*z*x,0.,curvature*x*x/2,0.,-curvature*x,0.])
            for a,bnode in zip(ids[:-1],ids[1:]):allelements.append(dict(a=a,b=bnode,EA=E*b*t,EIy=E*b*t**3/12,EIz=E*t*b**3/12,GJ=26e9*min(b,t)**3*max(b,t)/3,local_y=[0.,1.,0.]))
            groups.append(dict(kind='frame',nodes=ids,element_indices=list(range(start,len(allelements))),lower=np.array([0.,-b/2,z-t/2]),upper=np.array([L,b/2,z+t/2])))
        U=np.asarray(U)
        for e in allelements:
            ids=[6*e['a']+i for i in range(6)]+[6*e['b']+i for i in range(6)];K,_,_=_element_k(e,allnodes);d=U[ids];energy+=float(d@K@d/2)
        quadrature_count=0
        for index,z in ((1,-.06),(2,.06)):
            lo=np.array([0.,-.004,z]);hi=np.array([L,.004,z])
            for point,area in contact_quadrature(groups[0],groups[index],lo,hi,2,np.asarray(allnodes)):
                ia,Na=contact_mapping(groups[0],point,allnodes,allelements);ib,Nb=contact_mapping(groups[index],point,allnodes,allelements);maxslip=max(maxslip,float(np.linalg.norm(Na@U[ia]-Nb@U[ib])));quadrature_count+=1
        runs.append(dict(divisions=divisions,computed_energy_J=energy,exact_energy_J=expected,relative_energy_error=abs(energy-expected)/expected,maximum_contact_slip_m=maxslip,quadrature_points=quadrature_count))
    return dict(schema='osr-continuous-I-section-bending-patch/1',runs=runs,benchmark_pass=all(r['relative_energy_error']<1e-9 and r['maximum_contact_slip_m']<1e-12 for r in runs),
        scope='Exact integrated cross-section and kinematic contact patch test; no physical joint correlation or whole-body validation')
