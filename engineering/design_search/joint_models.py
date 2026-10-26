"""Bounded, synthetic native transfer-joint method fixtures.

Two collinear bearing points are a rank-five control. Four noncollinear points
and four finite-area backing pads are separate fixtures. None is a qualified
bolt, adhesive, slip, preload, fatigue or vehicle joint model.
"""
from pathlib import Path
from math import isfinite
from math import log
import os, resource, subprocess, time, re
import numpy as np
from engineering.station_rail import FLAGS
from engineering.station_rail.common import digest, identity, encoded
from engineering.design_search.structural_families import _coupon_mesh, rigid_pad_rank

PRODUCER='engineering/design_search/joint_models.py'
KINDS=('two_bolt_control','four_bolt','finite_area')
REGULARIZER_NM_PER_RAD=.01


def joint_definition(kind='four_bolt'):
    if kind not in KINDS:raise ValueError('Explicit bounded transfer geometry required')
    points=[[-.02,0.,0.],[.02,0.,0.]] if kind=='two_bolt_control' else [[x,0.,z] for x in (-.02,.02) for z in (-.02,.02)]
    pads=[] if kind!='finite_area' else [dict(at_m=[x-.008,-.002,z-.008],size_m=[.016,.002,.016],density_kg_m3=7850.,material='synthetic-steel-E200GPa') for x,y,z in points]
    return dict(kind=kind,transfer_points_m=points,plate=dict(at_m=[-.04,0.,-.04],size_m=[.08,.004,.08],density_kg_m3=2710.,E_Pa=69e9,nu=.33),
        backing_pads=pads,backing_stock_mass_kg=sum(np.prod(p['size_m'])*p['density_kg_m3'] for p in pads),
        synthetic_assumptions=['Perfectly intact isotropic aluminium loading plate; no bolt-hole stress resolution','Rigid external front-face loading fixture is massless and is not body hardware','Point fixtures constrain translations at bolt axes; finite-area pads are perfectly bonded and fixed at their rear faces','Diagnostic rotational spring is numerical regularisation, not physical joint hardware'],
        regularizer_Nm_per_rad=REGULARIZER_NM_PER_RAD,**FLAGS)


def _transfer_matrix(points):
    rows=[]
    for x,y,z in points:
        rows.extend([[1,0,0,0,z,-y],[0,1,0,-z,0,x],[0,0,1,y,-x,0]])
    return np.asarray(rows,dtype=float)


def rank_and_work_checks(definition):
    A=_transfer_matrix(definition['transfer_points_m']);q=np.array([.11,-.07,.03,.02,-.04,.06]);f=np.arange(1,len(A)+1,dtype=float)/17
    singular=np.linalg.svd(A,compute_uv=False);work=float((A@q)@f);reference=float(q@(A.T@f))
    return dict(rank=int(np.linalg.matrix_rank(A,tol=1e-11)),singular_values=singular.tolist(),virtual_work_residual=abs(work-reference),
        generalized_force_from_nodal=dict(zip(('Fx','Fy','Fz','Mx','My','Mz'),(A.T@f).tolist())))


def deck(kind='four_bolt',mesh=1,regularizer=REGULARIZER_NM_PER_RAD):
    if mesh not in (1,2,3,4):raise ValueError('Bounded native mesh levels1..4 only')
    d=joint_definition(kind);cuts=sorted({-.04,-.02,0.,.02,.04}|({-.028,-.012,.012,.028} if kind=='finite_area' else set()))
    def refined(values):return sorted({a+(b-a)*i/mesh for a,b in zip(values,values[1:]) for i in range(mesh+1)})
    xs=refined(cuts);zs=xs;ys=[.004*i/mesh for i in range(mesh+1)]
    ns,es=_coupon_mesh(xs,ys,zs);groups={'PLATE':[e['id'] for e in es]};lookup={tuple(round(x,12) for x in p):n for n,p in ns.items()}
    def merge(nodes,elements):
        ids={}
        for old,p in nodes.items():
            key=tuple(round(x,12) for x in p)
            if key not in lookup:lookup[key]=len(ns)+1;ns[lookup[key]]=p
            ids[old]=lookup[key]
        added=[]
        for e in elements:
            n=len(es)+1;es.append(dict(id=n,nodes=[ids[i] for i in e['nodes']]));added.append(n)
        return added
    if kind=='finite_area':
        groups['PAD']=[]
        for pad in d['backing_pads']:
            a,b,c=pad['at_m'];lx,ly,lz=pad['size_m'];pp,ee=_coupon_mesh([x for x in xs if a-1e-10<=x<=a+lx+1e-10],[b+ly*i/mesh for i in range(mesh+1)],[z for z in zs if c-1e-10<=z<=c+lz+1e-10]);groups['PAD']+=merge(pp,ee)
    # The plate grid has pad boundary cuts; pad interfaces share the same nodes.
    supported=[n for n,p in ns.items() if abs(p[1]+.002)<1e-10] if kind=='finite_area' else [lookup[tuple(p)] for p in d['transfer_points_m']]
    ref=len(ns)+1;rot=ref+1;ns[ref]=[0.,0.,.004];ns[rot]=[0.,0.,.004]
    lines=['*HEADING','Six-axis synthetic joint fixture; SI N-m-Pa','*NODE']+[str(n)+','+','.join(f'{x:.14g}' for x in p) for n,p in ns.items()]
    for group,ids in groups.items():
        lines.append('*ELEMENT,TYPE=C3D20,ELSET='+group)
        for eid in ids:
            nodes=es[eid-1]['nodes'];lines += [str(eid)+','+','.join(map(str,nodes[:15]))+',',','.join(map(str,nodes[15:]))]
    lines += ['*ELSET,ELSET=SOLIDS','PLATE'+(',PAD' if kind=='finite_area' else ''), '*ELEMENT,TYPE=SPRING1,ELSET=REG',f'{len(es)+1},{rot}', '*SPRING,ELSET=REG','1',f'{regularizer:.14g}.0' if float(regularizer).is_integer() else f'{regularizer:.14g}',
        '*MATERIAL,NAME=AL','*ELASTIC','69000000000.,.33','*DENSITY','2710.','*SOLID SECTION,ELSET=PLATE,MATERIAL=AL']
    if kind=='finite_area':lines += ['*MATERIAL,NAME=STEEL','*ELASTIC','200000000000.,.3','*DENSITY','7850.','*SOLID SECTION,ELSET=PAD,MATERIAL=STEEL']
    lines += ['*BOUNDARY']+[f'{n},1,3' for n in supported]
    # Translation-only equations, rotation variables represented by DOF1..3.
    for n,p in ns.items():
        if n in (ref,rot) or abs(p[1]-.004)>1e-10:continue
        x,y,z=[p[j]-ns[ref][j] for j in range(3)]
        coefficients=[[(2,-z),(3,y)],[(1,z),(3,-x)],[(1,-y),(2,x)]]
        for j in range(3):
            terms=[(n,j+1,1.),(ref,j+1,-1.)]+[(rot,k,v) for k,v in coefficients[j] if abs(v)>1e-14]
            lines += ['*EQUATION',str(len(terms)),','.join(f'{a},{b},{c:.14g}' for a,b,c in terms)]
    lines += ['*NSET,NSET=REFS',f'{ref},{rot}','*NSET,NSET=SUPPORTS']
    lines += [','.join(map(str,supported[i:i+16])) for i in range(0,len(supported),16)]
    loads=[]
    for j in range(6):
        # Fz at the front face also excites Mx through the4mm offset.
        # Keep the deliberate soft-mode diagnostic inside small rotation;
        # all reported compliances are divided by this load amplitude.
        load=(1e-5 if j==3 else 1e-3 if j==2 else 1.) if kind=='two_bolt_control' else 1.;loads.append(load)
        lines += ['*STEP','*STATIC','*CLOAD,OP=NEW',f'{ref if j<3 else rot},{j%3+1},{load:.14g}','*NODE PRINT,NSET=REFS','U','*NODE PRINT,NSET=SUPPORTS','RF','*EL PRINT,ELSET=SOLIDS,TOTALS=ONLY','ELSE','*END STEP']
    lines += ['*STEP','*FREQUENCY','6','*END STEP','']
    d.update(mesh_level=mesh,nodes=ns,supported_nodes=supported,translation_ref=ref,rotation_ref=rot,solid_elements=len(es),native_element_kind='C3D20',regularizer_Nm_per_rad=regularizer,load_amplitudes=loads,
        load_order=['Fx','Fy','Fz','Mx','My','Mz'],rank_check=rank_and_work_checks(d))
    return '\n'.join(lines),d


def _parse(path):
    cases=[];mode=None;current=None;frequencies=[];energy_next=False;freq=False;modal=False
    for line in Path(path).read_text().splitlines():
        low=line.lower();f=line.split()
        if 'E I G E N V A L U E   O U T P U T' in line:modal=True;mode=None
        if modal:
            if 'MODE NO' in line and 'EIGENVALUE' in line:freq=True
            elif freq and len(f)==5 and f[0].isdigit() and len(frequencies)<6:frequencies.append(float(f[3]))
            elif frequencies and not f:freq=False
            continue
        if 'displacements' in low:
            current=dict(u={},rf={});cases.append(current);mode='u'
        elif 'forces' in low and current is not None:mode='rf'
        elif 'total internal energy' in low:mode=None;energy_next=True
        elif energy_next and len(f)==1:
            try:current['solid_energy_J']=float(f[0]);energy_next=False
            except ValueError:pass
        elif mode and len(f)==4 and f[0].isdigit():current[mode][int(f[0])]=list(map(float,f[1:]))
    return cases,frequencies


def analyse(folder,definition):
    states,freq=_parse(Path(folder)/'joint.dat');d=definition;ns={int(n):p for n,p in d['nodes'].items()};C=np.zeros((6,6));results=[]
    if len(states)!=6:raise ValueError(f'Expected six independent native states, got {len(states)}')
    for j,(state,load) in enumerate(zip(states,d['load_amplitudes'])):
        q=np.array(state['u'][d['translation_ref']]+state['u'][d['rotation_ref']]);C[:,j]=q/load;applied=np.zeros(6);applied[j]=load
        reaction=np.zeros(6)
        for n,f in state['rf'].items():reaction[:3]+=f;reaction[3:]+=np.cross(np.array(ns[n])-np.array(ns[d['translation_ref']]),f)
        reg_moment=-d['regularizer_Nm_per_rad']*q[3];reaction[3]+=reg_moment
        external=.5*float(applied@q);reg=.5*d['regularizer_Nm_per_rad']*q[3]**2;solid=state.get('solid_energy_J')
        residual=reaction+applied
        results.append(dict(load=d['load_order'][j],load_amplitude=load,generalized_displacement=q.tolist(),reaction=result_list(reaction),
            force_residual_N=result_list(residual[:3]),moment_residual_Nm=result_list(residual[3:]),external_work_J=external,solid_energy_J=solid,regularizer_energy_J=reg,
            regularizer_energy_fraction=reg/abs(external) if external else None,energy_relative_residual=abs(external-reg-solid)/abs(external) if solid is not None and external else None))
    scales=np.sqrt(np.maximum(np.abs(np.diag(C)),1e-30));reciprocity=float(np.max(np.abs(C-C.T)/np.outer(scales,scales)))
    finite=all(isfinite(x) for x in C.flat);equilibrium=max(max(abs(x) for x in r['force_residual_N']+r['moment_residual_Nm'])/max(r['load_amplitude'],1e-12) for r in results)
    energy=max((r['energy_relative_residual'] if r['energy_relative_residual'] is not None else float('inf')) for r in results)
    mechanism=d['kind']=='two_bolt_control';regmax=max(r['regularizer_energy_fraction'] or 0 for r in results)
    return dict(execution='completed',numerical_validity='valid' if finite and equilibrium<1e-4 and energy<1e-4 and reciprocity<1e-4 else 'unknown',
        engineering_screen='fail-mechanism-control' if mechanism else 'method-only',static_states=6,states=results,compliance_matrix=C.tolist(),reciprocity_relative_residual=reciprocity,
        maximum_equilibrium_relative_residual=equilibrium,maximum_energy_relative_residual=energy,maximum_regularizer_energy_fraction=regmax,modal_frequencies_Hz=freq,
        modal_scope='Fixture plate/pads only; no installed bolt mass, no validated preload or vehicle mode',rank_check=d['rank_check'])


def result_list(a):return [float(x) for x in a]


def refinement_checks(cases):
    """All-axis trends, including coupling and modes; no claimed stress limit."""
    records=[]
    for kind in KINDS:
        rr=sorted([r for r in cases if r['kind']==kind and r['execution']=='completed'],key=lambda r:r['mesh_level'])
        if len(rr)<2:continue
        pairs=[]
        for a,b in zip(rr,rr[1:]):
            A,B=[np.array(r['compliance_matrix']) for r in (a,b)];di=np.maximum(np.abs(np.diag(B)),1e-30);change=np.abs(np.diag(A)-np.diag(B))/di
            coupling=float(np.max(np.abs(A-B)/np.sqrt(np.outer(di,di))))
            fa,fb=[np.array(r['modal_frequencies_Hz']) for r in (a,b)];modal=float(max(abs(fa-fb)/fb)) if len(fa)==len(fb)==6 and min(fb)>0 else None
            pairs.append(dict(coarse_mesh=a['mesh_level'],fine_mesh=b['mesh_level'],diagonal_compliance_relative_change=change.tolist(),scaled_coupled_compliance_change=coupling,
                modal_frequency_relative_change=modal,mesh_confirmed=bool(max(change)<.05 and coupling<.05 and modal is not None and modal<.05 and a['numerical_validity']==b['numerical_validity']=='valid')))
        richardson=[]
        if len(rr)>=3:
            selected=rr[-3:];hs=[1/r['mesh_level'] for r in selected]
            for j in range(6):
                values=[r['compliance_matrix'][j][j] for r in selected];d0=values[0]-values[1];d1=values[1]-values[2];record=dict(axis=selected[0]['states'][j]['load'],mesh_levels=[r['mesh_level'] for r in selected],compliance_values=values,state='unknown')
                if d0*d1>0:
                    ratio=d0/d1
                    def theoretical(p):return (hs[0]**p-hs[1]**p)/(hs[1]**p-hs[2]**p)
                    if theoretical(.1)<=ratio<=theoretical(8.):
                        lo,hi=.1,8.
                        for _ in range(60):
                            mid=(lo+hi)/2
                            if theoretical(mid)<ratio:lo=mid
                            else:hi=mid
                        order=(lo+hi)/2;infinity=values[2]+(values[2]-values[1])/((hs[1]/hs[2])**order-1)
                        record.update(state='conditional_asymptotic_estimate',observed_order=order,extrapolated_compliance=infinity,estimated_fine_relative_error=abs(values[2]-infinity)/max(abs(infinity),1e-30))
                richardson.append(record)
        records.append(dict(kind=kind,pairs=pairs,mesh_confirmed=pairs[-1]['mesh_confirmed'],richardson=richardson,
            scope='Six-axis work-conjugate compliance and fixture-frequency trends; extrapolation assumes a smooth asymptotic sequence, not physical calibration',point_support_stress_convergence='not claimed'))
    return records


def run_benchmarks(output,*,plan=None):
    output=Path(output).resolve()
    if output.exists():raise ValueError('Fresh immutable run directory required')
    output.mkdir(parents=True);sources={PRODUCER:digest(__file__),'engineering/design_search/structural_families.py':digest(Path(__file__).with_name('structural_families.py'))}
    ccx=Path('/usr/bin/ccx').resolve();limits=[n for n in resource.getrlimit(resource.RLIMIT_AS) if n!=resource.RLIM_INFINITY]
    tool=dict(ccx_path=str(ccx),ccx_sha256=digest(ccx),OMP_threads=1,RLIMIT_AS_bytes=min([2*1024**3,*limits]),timeout_s=45)
    results=[];plan=list(plan) if plan is not None else [(kind,mesh) for kind in KINDS for mesh in (1,2)]
    if not 1<=len(plan)<=8 or len(set(plan))!=len(plan):raise ValueError('One to eight unique bounded native jobs required')
    for kind,mesh in plan:
            raw,d=deck(kind,mesh);folder=output/f'{kind}-{mesh}';folder.mkdir();(folder/'joint.inp').write_text(raw);(folder/'definition.json').write_bytes(encoded(d));start=time.monotonic()
            def bounded():resource.setrlimit(resource.RLIMIT_AS,(tool['RLIMIT_AS_bytes'],tool['RLIMIT_AS_bytes']))
            r=dict(case=folder.name,kind=kind,mesh_level=mesh,execution='tool_error')
            try:
                proc=subprocess.run([str(ccx),'joint'],cwd=folder,capture_output=True,timeout=45,preexec_fn=bounded,env={**os.environ,'OMP_NUM_THREADS':'1'})
                (folder/'stdout.log').write_bytes(proc.stdout);(folder/'stderr.log').write_bytes(proc.stderr);r['returncode']=proc.returncode
                if proc.returncode==0:r.update(analyse(folder,d))
            except subprocess.TimeoutExpired as e:
                (folder/'stdout.log').write_bytes(e.stdout or b'');(folder/'stderr.log').write_bytes(e.stderr or b'');r.update(execution='interrupted',reason='45second native job limit')
            except (OSError,ValueError,KeyError) as e:r.update(execution='tool_error',reason=str(e))
            r['runtime_s']=time.monotonic()-start;results.append(r)
    if sources[PRODUCER]!=digest(__file__) or sources['engineering/design_search/structural_families.py']!=digest(Path(__file__).with_name('structural_families.py')):raise ValueError('Source changed during native execution')
    if tool['ccx_sha256']!=digest(ccx):raise ValueError('CCX binary changed during native execution')
    refinements=refinement_checks(results)
    value=dict(schema='osr-transfer-joint-method-benchmarks/1',source_sha256=sources,tool=tool,tool_binary_unchanged=True,native_jobs=len(plan),static_states=6*len(plan),modal_jobs=len(plan),cases=results,refinements=refinements,
        execution='completed' if all(r['execution']=='completed' for r in results) else 'completed_with_errors',scope='Synthetic transfer formulation benchmark; rank, force/moment balance, reciprocity, solid+regularizer energy and fixture modes; no body or physical joint acceptance',**FLAGS)
    value['evaluation_id']=identity(value);(output/'result.json').write_bytes(encoded(value));manifest=dict(schema='osr-transfer-joint-manifest/1',evaluation_id=value['evaluation_id'],source_sha256=sources,tool=tool,files_sha256={p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file()},**FLAGS);manifest['manifest_id']=identity(manifest);(output/'manifest.json').write_bytes(encoded(manifest));return value


def run_refinement(output):
    return run_benchmarks(output,plan=[('finite_area',m) for m in (2,3,4)])
