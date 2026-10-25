"""Recompute admission/contour/mesh checks from retained numerical artifacts."""
from hashlib import sha256
import math
from pathlib import Path
import re
import numpy as np
from engineering.vehicle_optimisation import magnets
from .formulation import STAGES,ITERATIONS,ABS_TOL,REL_TOL,COUNTS

VEHICLE_ID='de9e5f82391fe1c7aa6dd4a9321711f3972e580f1f9345933860e73367f27e4f'
COMPONENT_ID='ff677ea60334a09828e70df8e89f8a9a8726e38da171cfc0f73c5f60221d2c0e'
NUMBER=r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'


def validate_source(source):
    value=source['value']
    if source['vehicle_candidate_id']!=VEHICLE_ID or value['physical_id']!=COMPONENT_ID or value['sample_id']!='N35-H8-half-no-yoke' or value['grade_id']!='Arnold-N35UH' or value['length_x_m']!=1.:
        raise ValueError('exact retained N35UH finite coupon/candidate identities required')
    # This refinement is deliberately outside the initial legacy CATALOGUE.
    # Rebuild its exact declared tuple, including materials and counted stock.
    expected=magnets._build(('N35-H8-half-no-yoke','planar-halbach','Arnold-N35UH',dict(segments=8,magnet_volume_m3=.006)))
    if value!=expected:raise ValueError('retained refined full physical/material/stock bundle differs')
    return value


def contours(value):
    train=[p for p in value['stock_parts'] if p['group']=='train'];lo=[min(p['at_m'][k] for p in train) for k in range(3)];hi=[max(p['at_m'][k]+p['size_m'][k] for p in train) for k in range(3)]
    return [[[v-d for v in lo],[v+d for v in hi]] for d in (.0042,.0066)]


def parse_stages(text):
    stages=[];current=None
    for raw in text.splitlines():
        line=raw.strip()
        if not line.startswith(('LOAD ','CONTINUATION ','STAGE-END ')):continue
        if line.startswith('LOAD '):
            m=re.fullmatch(r'LOAD ('+NUMBER+r') INITIAL ('+NUMBER+r')',line)
            if not m or current is not None:raise ValueError('malformed or unterminated continuation stage')
            load,initial=map(float,m.groups())
            if not math.isfinite(initial) or initial<=0:raise ValueError('positive finite stage source residual required')
            if len(stages)>=STAGES or not math.isclose(load,(len(stages)+1)/STAGES,rel_tol=0,abs_tol=1e-10):raise ValueError('load stages must be exactly 0.1 through1.0 in order')
            current=dict(load_fraction=load,initial_residual=initial,iterations=[])
        else:
            label='CONTINUATION' if line.startswith('CONTINUATION ') else 'STAGE-END'
            m=re.fullmatch(label+r' ('+NUMBER+r') (\d+) ('+NUMBER+r') ('+NUMBER+r')',line)
            if not m or current is None:raise ValueError('malformed continuation residual record')
            load,index,absolute,relative=m.groups();load=float(load);index=int(index);absolute=float(absolute);relative=float(relative)
            if not math.isclose(load,current['load_fraction'],rel_tol=0,abs_tol=1e-10) or not 0<=index<=ITERATIONS or not all(math.isfinite(x) and x>=0 for x in (absolute,relative)):raise ValueError('continuation residual domain differs')
            if not math.isclose(relative,absolute/max(current['initial_residual'],1e-30),rel_tol=2e-12,abs_tol=1e-20):raise ValueError('continuation relative residual arithmetic differs')
            if label=='CONTINUATION':
                if index!=len(current['iterations'])+1:raise ValueError('continuation iteration sequence differs')
                current['iterations'].append(dict(iteration=index,absolute_residual=absolute,relative_residual=relative))
            else:
                if index!=len(current['iterations']):raise ValueError('stage-end iteration count differs')
                last=current['iterations'][-1] if current['iterations'] else dict(absolute_residual=current['initial_residual'],relative_residual=1.)
                if not math.isclose(absolute,last['absolute_residual'],rel_tol=1e-12,abs_tol=1e-25) or not math.isclose(relative,last['relative_residual'],rel_tol=1e-12,abs_tol=1e-25):raise ValueError('stage-end residual differs from iteration trace')
                current.update(iteration_count=index,absolute_residual=absolute,relative_residual=relative,converged=absolute<=ABS_TOL or relative<=REL_TOL);stages.append(current);current=None
    complete=len(stages)==STAGES and current is None
    return dict(stages=stages,unterminated_stage=current,all_stages_present=complete,full_source_converged=complete and all(s['converged'] for s in stages),final_load_fraction=stages[-1]['load_fraction'] if stages else None,absolute_tolerance=ABS_TOL,relative_tolerance=REL_TOL)


def validate_mesh(path,mesh,value,margin):
    path=Path(path)
    if path.is_symlink() or path.stat().st_size>128*1024**2:raise ValueError('bounded ordinary mesh required')
    pm=[r for r in value['regions'] if r['material']==value['grade_id']];steel=next(r for r in value['regions'] if r['group']=='guideway');groups=list(range(100,100+len(pm)))
    expected_stock=[]
    for r in [*pm,steel]:
        a,b,c,d=r['bounds_yz_m'];expected_stock.append(dict(id=r['id'],box_m=[-value['length_x_m']/2,a,c,value['length_x_m'],b-a,d-c]))
    if mesh['physical_pm']!=groups or mesh['pm_regions']!=pm or mesh['magnetic_stock']!=expected_stock:raise ValueError('mesh physical regions differ from exact source stock')
    ymin=min(r['bounds_yz_m'][0] for r in value['regions'])-margin;ymax=max(r['bounds_yz_m'][1] for r in value['regions'])+margin;zmin=min(r['bounds_yz_m'][2] for r in value['regions'])-margin;zmax=max(r['bounds_yz_m'][3] for r in value['regions'])+margin
    expected_box=[-value['length_x_m']/2-margin,ymin,zmin,value['length_x_m']+2*margin,ymax-ymin,zmax-zmin]
    if not np.allclose(mesh['outer_box_m'],expected_box,rtol=0,atol=1e-12):raise ValueError('mesh air-box source/settings differ')
    lines=path.read_text().splitlines()
    if lines[lines.index('$MeshFormat')+1]!='2.2 0 8':raise ValueError('ASCII MSH2.2 required')
    start=lines.index('$Nodes');n=int(lines[start+1]);nodes={}
    for line in lines[start+2:start+2+n]:
        key,*coordinates=line.split();coords=np.array(list(map(float,coordinates)))
        if len(coords)!=3 or not np.isfinite(coords).all() or int(key) in nodes:raise ValueError('invalid mesh node inventory')
        nodes[int(key)]=coords
    if lines[start+2+n]!='$EndNodes':raise ValueError('mesh node terminator differs')
    if len(nodes)!=n or n!=mesh['nodes']:raise ValueError('mesh node count differs')
    start=lines.index('$Elements');n_elements=int(lines[start+1]);counts={};bounds={};tetra=0;ids=set()
    for line in lines[start+2:start+2+n_elements]:
        row=list(map(int,line.split()));element,kind,tags=row[:3]
        if element in ids:raise ValueError('duplicate mesh element')
        ids.add(element)
        if kind!=4:continue
        if tags<1 or len(row)!=3+tags+4:raise ValueError('invalid tetrahedron record')
        physical=row[3];vertices=row[3+tags:]
        if physical not in [*groups,200,300] or any(x not in nodes for x in vertices):raise ValueError('mesh material/node assignment differs')
        xyz=np.array([nodes[k] for k in vertices]);lo,hi=xyz.min(axis=0),xyz.max(axis=0)
        if physical not in bounds:bounds[physical]=[lo,hi]
        else:bounds[physical]=[np.minimum(bounds[physical][0],lo),np.maximum(bounds[physical][1],hi)]
        counts[physical]=counts.get(physical,0)+1;tetra+=1
    if lines[start+2+n_elements]!='$EndElements':raise ValueError('mesh element terminator differs')
    if len(ids)!=n_elements or tetra!=mesh['tetrahedra'] or not 0<tetra<=1000000 or set(counts)!=set([*groups,200,300]):raise ValueError('mesh tetrahedral inventory differs')
    for physical,stock in zip([*groups,200],expected_stock):
        box=stock['box_m'];target=[np.asarray(box[:3]),np.asarray(box[:3])+np.asarray(box[3:])]
        if not np.allclose(bounds[physical],target,rtol=0,atol=1e-8):raise ValueError('mesh material bounds differ from physical source')
    if not np.allclose(bounds[300],[np.asarray(expected_box[:3]),np.asarray(expected_box[:3])+np.asarray(expected_box[3:])],rtol=0,atol=1e-8):raise ValueError('actual mesh air-box bounds differ')
    return dict(nodes=len(nodes),tetrahedra=tetra,physical_tetrahedra={str(k):v for k,v in counts.items()},mesh_sha256=sha256(path.read_bytes()).hexdigest())


def checked_table(path,columns):
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size>64*1024**2:raise ValueError('bounded ordinary field table required')
    data=np.loadtxt(path)
    if data.ndim!=2 or data.shape[1]!=columns or not len(data) or not np.isfinite(data).all():raise ValueError('finite complete field table required')
    return data


def validate_contours(directory,boxes,mesh,value):
    outer=mesh['outer_box_m'];outer_lo=np.asarray(outer[:3]);outer_hi=outer_lo+np.asarray(outer[3:]);rows=[]
    for index,(lo,hi) in enumerate(boxes):
        lo=np.asarray(lo);hi=np.asarray(hi)
        if np.any(lo<=outer_lo) or np.any(hi>=outer_hi) or np.any(hi<=lo):raise ValueError('air contour outside finite domain')
        for stock in mesh['magnetic_stock']:
            box=stock['box_m'];lower=np.asarray(box[:3]);upper=lower+np.asarray(box[3:])
            for axis in range(3):
                others=[i for i in range(3) if i!=axis]
                for coordinate in (lo[axis],hi[axis]):
                    if lower[axis]-1e-10<=coordinate<=upper[axis]+1e-10 and all(hi[k]>lower[k]+1e-10 and lo[k]<upper[k]-1e-10 for k in others):raise ValueError('Maxwell integration surface intersects magnetic material')
        for axis in range(3):
            others=[i for i in range(3) if i!=axis]
            for side in (0,1):
                path=Path(directory)/f'face-{index}-{axis}-{side}.txt';data=checked_table(path,6);points=data[:,:3];expected=(COUNTS[others[0]]+1)*(COUNTS[others[1]]+1)
                if len(points)!=expected or len(np.unique(np.round(points,12),axis=0))!=expected:raise ValueError('air-face grid count/uniqueness differs')
                if not np.allclose(points[:,axis],hi[axis] if side else lo[axis],rtol=0,atol=1e-10):raise ValueError('air-face normal-plane coordinate differs')
                for k in others:
                    grid=np.unique(np.round(points[:,k],12));target=np.linspace(lo[k],hi[k],COUNTS[k]+1)
                    if len(grid)!=len(target) or not np.allclose(grid,target,rtol=0,atol=2e-10):raise ValueError('air-face bounds/spacing differ')
                rows.append(dict(path=path.name,samples=len(points),sha256=sha256(path.read_bytes()).hexdigest()))
    return rows


def tetra_centroids(path,groups):
    lines=Path(path).read_text().splitlines();start=lines.index('$Nodes');count=int(lines[start+1]);nodes={int(v[0]):np.asarray(list(map(float,v[1:]))) for v in (line.split() for line in lines[start+2:start+2+count])};start=lines.index('$Elements');count=int(lines[start+1]);result={group:[] for group in groups}
    for line in lines[start+2:start+2+count]:
        row=list(map(int,line.split()))
        if row[1]==4 and row[3] in result:result[row[3]].append(np.mean([nodes[k] for k in row[3+row[2]:]],axis=0))
    return {key:np.asarray(value) for key,value in result.items()}


def validate_scalar_coverage(directory,mesh):
    directory=Path(directory);centroids=tetra_centroids(directory/'coupon.msh',[*mesh['physical_pm'],200]);checks=[]
    for filename,groups in [('PM-H.txt',mesh['physical_pm']),('steel-B.txt',[200])]:
        data=checked_table(directory/filename,4);expected=np.vstack([centroids[group] for group in groups]);actual=data[:,:3]
        if len(actual)!=len(expected) or len(np.unique(np.round(actual,12),axis=0))!=len(actual):raise ValueError('scalar field element coverage/count differs: '+filename)
        def ordered(points):return points[np.lexsort(tuple(np.round(points,11)[:,k] for k in (2,1,0)))]
        if not np.allclose(ordered(actual),ordered(expected),rtol=0,atol=2e-10):raise ValueError('scalar field coordinates differ from physical tetrahedral centroids: '+filename)
        checks.append(dict(path=filename,element_samples=len(actual),sha256=sha256((directory/filename).read_bytes()).hexdigest()))
    return checks


def analyze(directory,source,mesh,boxes,legacy):
    value=validate_source(source);scalar_checks=validate_scalar_coverage(directory,mesh);face_checks=validate_contours(directory,boxes,mesh,value);forces=legacy.maxwell(Path(directory),boxes)
    pm=checked_table(Path(directory)/'PM-H.txt',4);steel=checked_table(Path(directory)/'steel-B.txt',4)
    grade=value['materials'][value['grade_id']];hcj=grade['hcj_20c_a_m']*(1+grade['hcj_temperature_coefficient_per_k']*60);limit=grade['demag_hcj_fraction_limit']*hcj;minimum=float(pm[:,-1].min())
    symmetry=[]
    for result in forces:
        f=np.asarray(result['force_N']);m=np.asarray(result['moment_Nm']);scale=max(abs(f[2]),1e-12)
        symmetry.append(dict(Fx_over_absFz=abs(float(f[0]))/scale,Fy_over_absFz=abs(float(f[1]))/scale,abs_moment_Nm=np.abs(m).tolist(),moment_over_force_times_length=float(np.linalg.norm(m))/scale/value['length_x_m']))
    return dict(air_contour_results=forces,face_checks=face_checks,scalar_checks=scalar_checks,PM_Hparallel_min_A_per_m=minimum,steel_B_peak_T=float(steel[:,-1].max()),demag_proxy_limit_A_per_m=limit,demag_proxy_margin_A_per_m=limit+minimum,demag_proxy_screen_pass=limit+minimum>=0,demag_scope='Element-centroid Hparallel against 80% temperature-adjusted minimum Hcj; not measured knee/irreversible demagnetisation or local-peak convergence',symmetry_residuals=symmetry)


def change(a,b):
    va=np.asarray(a,dtype=float);vb=np.asarray(b,dtype=float);delta=vb-va
    return dict(delta=delta.tolist(),absolute_norm=float(np.linalg.norm(delta)),relative_norm=float(np.linalg.norm(delta))/max(float(np.linalg.norm(vb)),1e-12))


def comparisons(rows):
    usable={r['case']:r for r in rows if r.get('force_credit')};result={}
    for name,a,b in [('mesh','coarse','fine'),('domain','fine','expanded')]:
        if a not in usable or b not in usable:result[name]=dict(evaluated=False,reason='Both full-source cases with guarded output required');continue
        result[name]=dict(evaluated=True,from_case=a,to_case=b,contours=[dict(force=change(x['force_N'],y['force_N']),moment=change(x['moment_Nm'],y['moment_Nm'])) for x,y in zip(usable[a]['analysis']['air_contour_results'],usable[b]['analysis']['air_contour_results'])],PM_Hparallel_min_change_A_per_m=usable[b]['analysis']['PM_Hparallel_min_A_per_m']-usable[a]['analysis']['PM_Hparallel_min_A_per_m'],steel_peak_change_T=usable[b]['analysis']['steel_B_peak_T']-usable[a]['analysis']['steel_B_peak_T'])
    result['air_contours']={name:dict(force=change(row['analysis']['air_contour_results'][0]['force_N'],row['analysis']['air_contour_results'][1]['force_N']),moment=change(row['analysis']['air_contour_results'][0]['moment_Nm'],row['analysis']['air_contour_results'][1]['moment_Nm'])) for name,row in usable.items()}
    result['scope']='Differences of finite sampled diagnostics; no default acceptance threshold, converged force map or physical material validation'
    return result
