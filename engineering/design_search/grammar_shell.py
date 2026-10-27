"""Conformal layered-solid shell/frame method with finite-face admission.

Explicit C3D8I or C3D20 prisms resolve bending/shear and declared orthotropic
laws. Incompatible modes have known torsion limitations. Intact shared faces
are an explicit weld/bond hypothesis, not joint tests.
"""
from pathlib import Path
from math import ceil,prod,isfinite
import os,resource,subprocess,time,re
import numpy as np
from engineering.station_rail import ROOT,FLAGS
from engineering.station_rail.common import identity,digest,encoded
from engineering.design_search import design_grammar
PRODUCER='engineering/design_search/grammar_shell.py'
MISSING=['Joint/HAZ/adhesive strength, slip and fatigue calibration','Stress allowables, local/global buckling, modes, crash and fire','C3D8I torsion limitation and independent quadratic/whole-body torsion confirmation','Complete installed stock/CG/inertia, component load locations and swept clearances','Prototype and independent qualification review']


def _law(material):
    if not material.get('source_basis'):raise ValueError('Traceable declared material law required')
    kind=material.get('constitutive_kind')
    if kind=='isotropic':
        E,nu=material.get('E_Pa'),material.get('nu')
        if not isinstance(E,(int,float)) or E<=0 or not isinstance(nu,(int,float)) or not -1<nu<.5:raise ValueError('Complete isotropic research law required')
        return ['*ELASTIC',f'{E:.14g},{nu:.14g}']
    if kind=='orthotropic':
        c=material.get('engineering_constants',[])
        if len(c)!=9 or any(not isinstance(v,(int,float)) or not isfinite(v) for v in c):raise ValueError('Nine explicit orthotropic engineering constants required')
        E1,E2,E3,n12,n13,n23,G12,G13,G23=c
        if min(E1,E2,E3,G12,G13,G23)<=0:raise ValueError('Positive orthotropic stiffness required')
        S=np.diag([1/E1,1/E2,1/E3,1/G23,1/G13,1/G12]);S[0,1]=S[1,0]=-n12/E1;S[0,2]=S[2,0]=-n13/E1;S[1,2]=S[2,1]=-n23/E2
        if min(np.linalg.eigvalsh(S))<=0:raise ValueError('Orthotropic compliance is not positive definite')
        return ['*ELASTIC,TYPE=ENGINEERING CONSTANTS',','.join(f'{v:.14g}' for v in c[:8]),f'{c[8]:.14g}']
    raise ValueError('Density/axial-only data do not define a shell/solid material law')


def plan(candidate):
    design_grammar.validate(candidate);issues=[];model=candidate.get('shell_model')
    if not model:issues+=['Counted finite-area shell/frame connections and upper-joint model missing','Current generated upper-post/floor and side/roof attachment gaps must be filled by physical stock']
    ids=set(model.get('structural_part_ids',[])) if model else {p['id'] for p in candidate['parts'] if 'primary' in p.get('load_roles',[])}
    for p in candidate['parts']:
        if p['id'] not in ids:continue
        if p['kind']!='box':issues.append('Non-prismatic/mitered member adapter missing: '+p['id']);continue
        try:_law(candidate['materials'][p['material_id']])
        except ValueError as e:issues.append(p['material_id']+': '+str(e))
    gaps={}
    if not model:
        posts=[p for p in candidate['parts'] if p['id'].startswith('upper/post/')];floors=[p for p in candidate['parts'] if p['id'].startswith('floor/') and p['kind']=='box']
        if posts and floors:gaps['upper_post_to_floor_m']=min(min(p['start_m'][2],p['end_m'][2]) for p in posts)-max(p['at_m'][2]+p['size_m'][2] for p in floors)
    return dict(candidate_id=candidate['candidate_id'],admitted=not issues,issues=sorted(set(issues)),quantified_attachment_gaps=gaps,model_scope='Conformal layered-solid frame/shell under declared intact finite-face weld/bond assumptions; finite-face connectivity checked before dispatch',missing_gates=MISSING,**FLAGS)


def _mesh(parts,step,element_kind='C3D8I'):
    if element_kind not in ('C3D8I','C3D20'):raise ValueError('Explicit incompatible-mode or quadratic solid formulation required')
    if not .01<=step<=2.:raise ValueError('Fixture mesh construction domain .01..2m, not a project requirement')
    axes=[]
    for d in range(3):
        cuts={round(p['at_m'][d]+s*p['size_m'][d],10) for p in parts for s in (0,1)};lo=min(cuts);hi=max(cuts);cuts.update(round(lo+(hi-lo)*i/ceil((hi-lo)/step),10) for i in range(ceil((hi-lo)/step)+1));axes.append(sorted(cuts))
    maps=[{v:i for i,v in enumerate(a)} for a in axes];cells={}
    for p in parts:
        ranges=[range(maps[d][round(p['at_m'][d],10)],maps[d][round(p['at_m'][d]+p['size_m'][d],10)]) for d in range(3)]
        for i in ranges[0]:
            for j in ranges[1]:
                for k in ranges[2]:
                    if (i,j,k) in cells:raise ValueError('Positive-volume structural stock overlap; trim actual geometry before meshing')
                    cells[i,j,k]=p
    nodes={};lookup={};elements=[];edge=((0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7))
    def node(xyz):
        key=tuple(round(v,12) for v in xyz)
        if key not in lookup:lookup[key]=len(nodes)+1;nodes[lookup[key]]=list(key)
        return lookup[key]
    for key,p in sorted(cells.items()):
        i,j,k=key;a,b=axes[0][i:i+2];c,d=axes[1][j:j+2];e,f=axes[2][k:k+2];xyz=[[a,c,e],[b,c,e],[b,d,e],[a,d,e],[a,c,f],[b,c,f],[b,d,f],[a,d,f]]
        if element_kind=='C3D20':xyz += [[(xyz[a][q]+xyz[b][q])/2 for q in range(3)] for a,b in edge]
        elements.append(dict(id=len(elements)+1,nodes=[node(x) for x in xyz],volume_m3=(b-a)*(d-c)*(f-e),part_id=p['id'],material_id=p['material_id'],role=p.get('structural_role'),bounds=[a,b,c,d,e,f],cell=key))
    remaining=set(cells);components=[]
    while remaining:
        stack=[remaining.pop()];component=[]
        while stack:
            q=stack.pop();component.append(q)
            for d in range(3):
                for delta in (-1,1):
                    r=list(q);r[d]+=delta;r=tuple(r)
                    if r in remaining:remaining.remove(r);stack.append(r)
        components.append(component)
    expected=sum(p['volume_m3'] for p in parts);actual=sum(e['volume_m3'] for e in elements)
    if abs(actual-expected)>max(1e-9,expected*1e-8):raise ValueError('Mesh volume differs from actual counted stock')
    return nodes,elements,dict(finite_face_components=len(components),component_cell_counts=[len(c) for c in components],actual_stock_volume_m3=expected,meshed_volume_m3=actual,solid_elements=len(elements),node_count=len(nodes),mesh_m=step,element_kind=element_kind,element_limitations='C3D8I has known torsion limitations; quadratic/full-body torsion confirmation remains held' if element_kind=='C3D8I' else 'Quadratic full integration; independent mesh confirmation remains required')


def _base(nodes,elements,materials):
    lines=['*HEADING','Conformal full-integration solid shell/frame; SI N-m-Pa-kg','*NODE']+[str(n)+','+','.join(f'{v:.14g}' for v in xyz) for n,xyz in nodes.items()];groups={}
    for e in elements:groups.setdefault(e['material_id'],[]).append(e)
    for i,(mid,group) in enumerate(groups.items()):
        lines += [f'*ELEMENT,TYPE='+('C3D20' if len(group[0]['nodes'])==20 else 'C3D8I')+f',ELSET=M{i}']
        for e in group:
            ids=e['nodes'];lines += [str(e['id'])+','+','.join(map(str,ids[:15]))+(',' if len(ids)>15 else '')]
            if len(ids)>15:lines += [','.join(map(str,ids[15:]))]
        lines += [f'*MATERIAL,NAME=MAT{i}',*_law(materials[mid]),'*DENSITY',f'{materials[mid]["density_kg_m3"]:.14g}',f'*SOLID SECTION,ELSET=M{i},MATERIAL=MAT{i}']
    lines += ['*ELSET,ELSET=ALLSOLIDS',','.join(f'M{i}' for i in range(len(groups))),'*NSET,NSET=ALLN'];ids=sorted(nodes);lines += [','.join(map(str,ids[i:i+16])) for i in range(0,len(ids),16)]
    return lines


def _finish(lines,nodes,supports,loads,prescribed=None):
    lines+=['*BOUNDARY']+[f'{n},{d},{d},{value:.14g}' for n,d,value in (prescribed or [(n,d,0.) for n,ds in supports.items() for d in ds])]+['*NSET,NSET=SUPPORTS'];ids=sorted(supports);lines += [','.join(map(str,ids[i:i+16])) for i in range(0,len(ids),16)]+['*STEP','*STATIC'];rows=[f'{n},{d+1},{force:.14g}' for n,vector in loads.items() for d,force in enumerate(vector) if abs(force)>1e-20]
    if rows:lines += ['*CLOAD',*rows]
    lines+=['*NODE PRINT,NSET=ALLN','U','*NODE PRINT,NSET=SUPPORTS','RF','*EL PRINT,ELSET=ALLSOLIDS,TOTALS=ONLY','ELSE','*END STEP','']
    return '\n'.join(lines)


def deck(candidate,*,mesh_m=.8,load_case='normal',load_mass_kg=None,load_basis=None,element_kind='C3D8I'):
    if not .4<=mesh_m<=2.:raise ValueError('Bounded whole-body mesh domain .4..2m; finer models require a resource revision')
    p=plan(candidate)
    if not p['admitted']:raise ValueError('Candidate non-admitted: '+'; '.join(p['issues']))
    ids=set(candidate['shell_model']['structural_part_ids']);parts=[q for q in candidate['parts'] if q['id'] in ids];nodes,elements,meta=_mesh(parts,mesh_m,element_kind)
    if meta['finite_face_components']!=1:raise ValueError('Disconnected load path: '+str(meta['component_cell_counts']))
    if load_case not in candidate['load_cases']:raise ValueError('Explicit generated load case required')
    mass=candidate['load_cases'][load_case]['sprung_mass_hypothesis_kg'] if load_mass_kg is None else load_mass_kg
    if load_mass_kg is not None and abs(mass-candidate['load_cases'][load_case]['sprung_mass_hypothesis_kg'])>1e-6 and not load_basis:raise ValueError('Changed coupled load mass requires explicit source-bound basis')
    stockmass=sum(e['volume_m3']*candidate['materials'][e['material_id']]['density_kg_m3'] for e in elements)
    if mass<stockmass or not isfinite(mass):raise ValueError('Load mass cannot omit counted structural stock')
    loads={n:np.zeros(3) for n in nodes};g=9.80665;area=0.;top=(4,5,6,7,12,13,14,15)
    for e in elements:
        weight=e['volume_m3']*candidate['materials'][e['material_id']]['density_kg_m3']*g
        for n,w in zip(e['nodes'],[-1/8]*8+[1/6]*12 if element_kind=='C3D20' else [1/8]*8):loads[n][2]-=weight*w
        if e['role']=='floor' and abs(e['bounds'][5]-1.)<1e-9:area+=(e['bounds'][1]-e['bounds'][0])*(e['bounds'][3]-e['bounds'][2])
    if area<=0:raise ValueError('Counted passenger floor load surface missing')
    pressure=(mass-stockmass)*g/area
    for e in elements:
        if e['role']=='floor' and abs(e['bounds'][5]-1.)<1e-9:
            force=pressure*(e['bounds'][1]-e['bounds'][0])*(e['bounds'][3]-e['bounds'][2])
            for index,w in zip(top,[-1/12]*4+[1/3]*4 if element_kind=='C3D20' else [1/4]*4):loads[e['nodes'][index]][2]-=force*w
    model=candidate['shell_model'];supports={};patches=[]
    for x in model['support_x_m']:
        for y in model['support_y_m']:
            ns=[n for n,q in nodes.items() if abs(q[2]-model['support_z_m'])<1e-9 and abs(q[0]-x)<=.100001 and abs(q[1]-y)<=.090001]
            if len(ns)<8:raise ValueError('Counted finite bearing patch not resolved')
            for n in ns:supports[n]={3}
            patches.append(dict(x_m=x,y_m=y,node_count=len(ns)))
    ordered=sorted(supports,key=lambda n:(nodes[n][0],nodes[n][1]));supports[ordered[0]].update((1,2));supports[ordered[-1]].add(2)
    raw=_finish(_base(nodes,elements,candidate['materials']),nodes,supports,loads)
    return raw,dict(**meta,candidate_id=candidate['candidate_id'],load_case=load_case,load_mass_kg=mass,load_basis=load_basis or candidate['load_cases'][load_case],structural_selfweight_mass_kg=stockmass,floor_lumped_remaining_mass_kg=mass-stockmass,load_distribution='Consistent element selfweight + uniform additional floor pressure; actual equipment/roof load locations held',support_patches=patches,support_assumption='Rigid flat finite bearing pads, one XY datum and one Y datum; bogie compliance held',joint_assumption=model['joint_assumption'],nodes=nodes,supports={str(n):sorted(ds) for n,ds in supports.items()},loads_N={str(n):v.tolist() for n,v in loads.items()})


def _read(path):
    U={};RF={};active=None;energy=None;want=False
    for line in Path(path).read_text().splitlines():
        f=line.split();low=line.lower()
        if 'displacements' in low:active=U
        elif 'forces' in low:active=RF
        elif 'total internal energy' in low:active=None;want=True
        elif want and len(f)==1:
            try:energy=float(f[0]);want=False
            except ValueError:pass
        elif active is not None and len(f)==4 and f[0].isdigit():active[int(f[0])]=list(map(float,f[1:]))
    if not U or energy is None or any(not isfinite(x) for v in list(U.values())+list(RF.values()) for x in v):raise ValueError('Incomplete/nonfinite native fields')
    return U,RF,energy


def analyse(definition,path):
    if definition.get('benchmark_kind') in ('orthotropic_axial','orthotropic_shear'):return _analyse_patch(definition,path)
    U,RF,energy=_read(path);nodes={int(n):v for n,v in definition['nodes'].items()};loads={int(n):np.array(v) for n,v in definition['loads_N'].items()};supports={int(n):ds for n,ds in definition['supports'].items()};reaction={n:np.array(RF[n])-loads.get(n,np.zeros(3)) for n in supports};F=sum(loads.values(),np.zeros(3));R=sum(reaction.values(),np.zeros(3));moment=sum((np.cross(nodes[n],v) for n,v in loads.items()),np.zeros(3))+sum((np.cross(nodes[n],v) for n,v in reaction.items()),np.zeros(3));force_scale=max(sum(np.linalg.norm(v) for v in loads.values()),1.);length=max(np.linalg.norm(np.ptp(np.array(list(nodes.values())),axis=0)),1.);work=.5*sum(float(v@U[n]) for n,v in loads.items());ee=abs(work-energy)/max(abs(work),1e-30);fe=float(max(abs(F+R)))/force_scale;me=float(max(abs(moment)))/(force_scale*length)
    maxima={name:max(abs(v[d]) for v in U.values()) for d,name in enumerate(('longitudinal_m','lateral_m','vertical_m'))}
    result=dict(execution='completed',numerical_validity='equilibrium_energy_confirmed_only' if max(ee,fe,me)<1e-4 else 'unknown',engineering_screen='unknown',maximum_displacements=maxima,force_relative_residual=fe,moment_relative_residual=me,force_residual_N=(F+R).tolist(),moment_residual_Nm=moment.tolist(),external_work_J=work,native_internal_energy_J=energy,energy_relative_residual=ee)
    if definition.get('benchmark_kind')=='bending':
        actual=-sum(U[int(n)][2]*w for n,w in definition['tip_weights'].items());expected=definition['expected_tip_m'];error=abs(actual-expected)/expected;result.update(tip_work_displacement_m=actual,expected_tip_m=expected,analytical_relative_error=error,method_screen='pass' if error<.05 and max(ee,fe,me)<1e-4 else 'fail')
    return result


def run(candidate,output,*,root=ROOT,mesh_m=.8,load_case='normal',load_mass_kg=None,load_basis=None,memory_mb=5120,timeout_s=90,element_kind='C3D8I'):
    output=Path(output).resolve()
    if output.exists():raise ValueError('Fresh immutable shell/frame package required')
    raw,definition=deck(candidate,mesh_m=mesh_m,load_case=load_case,load_mass_kg=load_mass_kg,load_basis=load_basis,element_kind=element_kind);sources={**candidate['sources'],PRODUCER:digest(__file__)}
    for name,sha in sources.items():
        if digest(Path(root)/name)!=sha:raise ValueError('Shell source mismatch: '+name)
    result=_execute(raw,definition,output,memory_mb,timeout_s);(output/'candidate.json').write_bytes(encoded(candidate));result.update(candidate_id=candidate['candidate_id'],definition_id=candidate['definition_id'],source_sha256=sources,missing_gates=MISSING,orthotropic_axes='GlobalXYZ only; arbitrary ply rotation/ABD mapping requires a separate validated adapter',**FLAGS)
    for name,sha in sources.items():
        if digest(Path(root)/name)!=sha:raise ValueError('Shell source changed: '+name)
    return _seal(output,result,sources)


def _execute(raw,definition,output,memory_mb,timeout_s):
    if isinstance(memory_mb,bool) or not isinstance(memory_mb,int) or memory_mb not in (3072,5120) or timeout_s not in (90,150):raise ValueError('Explicit3/5GiB and90/150second resource revision required')
    output.mkdir(parents=True);(output/'model.inp').write_text(raw);(output/'definition.json').write_bytes(encoded(definition));cap=min([memory_mb*1024**2,*[n for n in resource.getrlimit(resource.RLIMIT_AS) if n!=resource.RLIM_INFINITY]]);tool=dict(ccx_path='/usr/bin/ccx',ccx_sha256=digest('/usr/bin/ccx'),requested_memory_mb=memory_mb,RLIMIT_AS_bytes=cap,OMP_threads=1,timeout_s=timeout_s);start=time.monotonic()
    def bounded():resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
    result=dict(execution='tool_error',numerical_validity='unknown',engineering_screen='unknown')
    try:
        proc=subprocess.run([tool['ccx_path'],'model'],cwd=output,capture_output=True,timeout=timeout_s,preexec_fn=bounded,env={**os.environ,'OMP_NUM_THREADS':'1'});(output/'stdout.log').write_bytes(proc.stdout);(output/'stderr.log').write_bytes(proc.stderr);result['returncode']=proc.returncode
        if proc.returncode==0:result.update(analyse(definition,output/'model.dat'))
    except subprocess.TimeoutExpired as e:
        (output/'stdout.log').write_bytes(e.stdout or b'');(output/'stderr.log').write_bytes(e.stderr or b'');result.update(execution='interrupted',reason='bounded native limit')
    except (OSError,ValueError,KeyError,subprocess.SubprocessError) as e:result['reason']=str(e)
    if digest(tool['ccx_path'])!=tool['ccx_sha256']:raise ValueError('Native solver changed during shell solve')
    return dict(**result,tool=tool,runtime_s=time.monotonic()-start,mesh_summary={k:v for k,v in definition.items() if k not in ('nodes','loads_N','supports')})


def _seal(output,result,sources):
    result.update(schema='osr-solid-shell-frame-evaluation/1',source_sha256=sources,**FLAGS);result['evaluation_id']=identity(result);(output/'result.json').write_bytes(encoded(result));manifest=dict(evaluation_id=result['evaluation_id'],source_sha256=sources,tool=result.get('tool'),files_sha256={p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file()},**FLAGS);manifest['manifest_id']=identity(manifest);(output/'manifest.json').write_bytes(encoded(manifest));return result


def benchmark_plan():
    """Four independent method fixtures; synthetic laws are never supplier data."""
    al=dict(constitutive_kind='isotropic',E_Pa=69e9,nu=.33,density_kg_m3=2710.,source_basis='Declared reference metal method law')
    ortho=dict(constitutive_kind='orthotropic',engineering_constants=[25e9,8e9,8e9,.25,.25,.25,4e9,3e9,3e9],density_kg_m3=1900.,source_basis='Explicit synthetic orthotropic method fixture; not a qualified GFRP or supplier property table')
    cases=[]
    for n in (10,20):
        # Fine case has a separate finite-area internal interface, not a gap tie.
        parts=[dict(id='beam'+str(i),at_m=[a,0.,0.],size_m=[b-a,.2,.02],volume_m3=(b-a)*.2*.02,material_id='m') for i,(a,b) in enumerate([(0.,2.)] if n==10 else [(0.,1.),(1.,2.)])]
        ns,es,meta=_mesh(parts,2/n);supports={i:[1,2,3] for i,p in ns.items() if abs(p[0])<1e-10};loads={i:np.zeros(3) for i in ns};weights={};face=(1,2,6,5,9,18,13,17)
        for e in es:
            if abs(e['bounds'][1]-2.)>1e-10:continue
            share=(e['bounds'][3]-e['bounds'][2])*(e['bounds'][5]-e['bounds'][4])/(.2*.02)
            for j,w in zip(face,[1/4]*4):node=e['nodes'][j];weights[node]=weights.get(node,0.)+share*w;loads[node][2]-=10*share*w
        E=69e9;G=E/(2*(1+.33));expected=10*2**3/(3*E*(.2*.02**3/12))+10*2/((5/6)*G*.2*.02)
        definition=dict(**meta,benchmark_kind='bending',nodes=ns,supports={str(i):d for i,d in supports.items()},loads_N={str(i):v.tolist() for i,v in loads.items()},tip_weights=weights,expected_tip_m=expected,joint_scope='Coarse single prism versus fine two-prism shared finite face; ideal intact continuum, no calibrated weld')
        cases.append(dict(id='bending-'+str(n),raw=_finish(_base(ns,es,{'m':al}),ns,supports,loads),definition=definition))
    for name in ('orthotropic_axial','orthotropic_shear'):
        parts=[dict(id='patch',at_m=[0.,0.,0.],size_m=[.2,.1,.04],volume_m3=.2*.1*.04,material_id='m')];ns,es,meta=_mesh(parts,1.);eps=1e-4;prescribed=[];supports={i:[1,2,3] for i in ns}
        for i,(x,y,z) in ns.items():
            values=[eps*x,-.25*eps*y,-.25*eps*z] if name.endswith('axial') else [eps*z,0.,0.]
            prescribed.extend((i,d+1,v) for d,v in enumerate(values))
        modulus=25e9 if name.endswith('axial') else 3e9;area=.1*.04 if name.endswith('axial') else .2*.1;axis=0 if name.endswith('axial') else 2;upper=.2 if axis==0 else .04
        definition=dict(**meta,benchmark_kind=name,nodes=ns,supports={str(i):d for i,d in supports.items()},loads_N={},prescribed=prescribed,expected_resultant_N=modulus*eps*area,expected_energy_J=.5*modulus*eps**2*.2*.1*.04,resultant_nodes=[i for i,p in ns.items() if abs(p[axis]-upper)<1e-10],resultant_component=0,constitutive=ortho)
        cases.append(dict(id=name,raw=_finish(_base(ns,es,{'m':ortho}),ns,supports,{},prescribed),definition=definition))
    return dict(cases=cases,maximum_native_jobs=4,scope='Constitutive affine patches, bending/shear and intact shared-face continuum method checks; no complete vehicle qualification',**FLAGS)


def _analyse_patch(definition,path):
    U,RF,energy=_read(path);actual=sum(RF[int(n)][definition['resultant_component']] for n in definition['resultant_nodes']);expected=definition['expected_resultant_N'];forceerror=abs(actual-expected)/expected;energyerror=abs(energy-definition['expected_energy_J'])/definition['expected_energy_J'];work=.5*sum(RF[int(n)][d-1]*v for n,d,v in definition['prescribed']);workerror=abs(work-energy)/max(abs(energy),1e-30)
    return dict(execution='completed',numerical_validity='verified_constitutive_patch' if max(forceerror,energyerror,workerror)<1e-5 else 'unknown',engineering_screen='unknown',method_screen='pass' if max(forceerror,energyerror,workerror)<1e-5 else 'fail',actual_resultant_N=actual,expected_resultant_N=expected,resultant_relative_error=forceerror,native_internal_energy_J=energy,expected_energy_J=definition['expected_energy_J'],energy_relative_error=energyerror,external_work_J=work,work_energy_relative_error=workerror)


def run_benchmark(case,output,*,root=ROOT,memory_mb=3072,timeout_s=90):
    output=Path(output).resolve()
    if output.exists():raise ValueError('Fresh immutable method fixture required')
    source=digest(__file__);sources={PRODUCER:source};result=_execute(case['raw'],case['definition'],output,memory_mb,timeout_s)
    if digest(__file__)!=source or digest(Path(root)/PRODUCER)!=source:raise ValueError('Fixture producer changed or differs from declared source root')
    result['benchmark_id']=case['id'];return _seal(output,result,sources)
