"""Failure-driven, current-excited wheel-rail LIM research adapter.

Physical parameters are separate from operating/mesh hypotheses. Frozen native
A-u mathematics and finite-primary meshing receive explicit dictionaries;
there are no patched globals or imposed magnetic-gap fields. Results remain
2D research, including when necessary force/material screens pass.
"""
from copy import deepcopy
from pathlib import Path
from math import sqrt,isfinite
import json,os,re,resource,subprocess,time
from engineering.station_rail import ROOT,FLAGS
from engineering.station_rail.common import encoded,identity,digest,source_map
from engineering.station_rail import station_motor as base,long_motor as native
PRODUCER='engineering/design_search/wheel_motor.py'
PRODUCERS=(PRODUCER,base.PRODUCER,native.PRODUCER)
TOOLS_ROOT=ROOT
GETDP=TOOLS_ROOT/'build/trip-dynamics/tools/getdp-3.5.0-Linux64/bin/getdp'
LIMIT_BYTES=3*1024**3


def default_parameters():
    return dict(physical=dict(name='reference',primary_length_m=12.5,periods=25,pole_pitch_m=.25,
        slots_per_period=6,slot_width_m=.04,slot_depth_m=.055,backiron_m=.025,
        turns_per_coil=40,conductor_area_m2=25e-6,active_height_m=.16,
        secondary_length_m=9.,secondary_thickness_m=.015,secondary_bottom_TOR_m=.02,
        gap_each_side_m=.015,parallel_paths_per_phase=10,phase_sequence=['A+','C-','B+','A-','C+','B-']),
        evaluation=dict(current_peak_A=140.,slip_frequency_Hz=10.,phase_direction=1,
            scenarios=[dict(speed_m_s=0.,temperature_C=80.,gap_m=.015),
                dict(speed_m_s=20.,temperature_C=80.,gap_m=.015)],
            mesh_m=.01,gap_mesh_m=.00375,longitudinal_air_margin_m=.5,transverse_air_margin_m=.20,
            runtime_per_solve_s=60,maximum_nodes=300000,linear_steel_relative_mu=1000.,
            linear_peak_field_limit_T=1.3,wire_density_limit_RMS_A_mm2=4.,dc_bus_V=750.))


def initial_parameters():
    reference=default_parameters();wide=deepcopy(reference)
    wide['physical'].update(name='conservative-wide',periods=20,pole_pitch_m=.3125,
        slot_width_m=.045,slot_depth_m=.065,backiron_m=.060,turns_per_coil=48,
        conductor_area_m2=35e-6,active_height_m=.18,parallel_paths_per_phase=10)
    wide['evaluation']['current_peak_A']=170.
    return [reference,wide]


def revise(parameters,diagnostics,generation):
    """Change teeth/backiron/winding stock in response to measured failures."""
    if type(generation) is not int or generation<1:raise ValueError('Positive generation required')
    value=deepcopy(parameters);p=value['physical'];e=value['evaluation']
    text=json.dumps(diagnostics,sort_keys=True).lower()
    if generation==1 and p['name']=='reference':return initial_parameters()[1]
    if 'fail' in text or 'insufficient' in text or 'satur' in text:
        # More tooth section and return iron address the observed 2.24T field.
        # The 15mm physical gap is retained, rather than optimized away.
        p.update(name='wide-return-g'+str(generation),backiron_m=min(.1,p['backiron_m']*1.3),
            slot_width_m=max(.030,p['slot_width_m']*.90),slot_depth_m=min(.095,p['slot_depth_m']*1.10))
        p['conductor_area_m2']=min(p['conductor_area_m2'],.58*p['slot_width_m']*p['slot_depth_m']/p['turns_per_coil'])
        e['current_peak_A']=min(e['current_peak_A'],3.8*sqrt(2)*p['conductor_area_m2']*1e6)
    else:
        e['slip_frequency_Hz']=max(3.,e['slip_frequency_Hz']*.75)
    value['revision_reason']='Respond to retained force/material diagnostics; no numerical result presumed'
    definition(value)
    return value


def definition(parameters):
    p=parameters['physical'];e=parameters['evaluation']
    numbers=[v for k,v in p.items() if type(v) in (int,float)]
    if any(not isfinite(v) or v<=0 for v in numbers):raise ValueError('Positive finite physical dimensions required')
    if p['slots_per_period']!=6 or p['phase_sequence']!=['A+','C-','B+','A-','C+','B-']:raise ValueError('Only explicit six-slot balanced topology supported')
    if type(p['periods']) is not int or type(p['turns_per_coil']) is not int or type(p['parallel_paths_per_phase']) is not int:raise ValueError('Integer periods/turns/parallel paths required')
    if abs(p['primary_length_m']-2*p['pole_pitch_m']*p['periods'])>1e-9:raise ValueError('Whole periods must fit the named primary')
    if p['secondary_length_m']>p['primary_length_m'] or p['secondary_bottom_TOR_m']+p['active_height_m']>.200000001:raise ValueError('Secondary/primary or track-height envelope exceeded')
    if abs(p['gap_each_side_m']-.015)>1e-12:raise ValueError('Physical gap remains 15mm')
    pitch=2*p['pole_pitch_m']/6
    if p['slot_width_m']>=pitch or p['slot_width_m']<=0:raise ValueError('Positive tooth width required')
    if (p['periods']*2)%p['parallel_paths_per_phase']:raise ValueError('Equal paths must divide the coil count per phase')
    d=base.definition();d.pop('motor_component_id')
    d.update({k:p[k] for k in ('pole_pitch_m','slot_width_m','slot_depth_m','backiron_m','turns_per_coil','conductor_area_m2','active_height_m','secondary_length_m','secondary_thickness_m')})
    d.update(wavelength_m=2*p['pole_pitch_m'],slot_pitch_m=pitch,addressed_module_length_m=p['primary_length_m'],
        steel_relative_permeability_hypothesis=e['linear_steel_relative_mu'],linear_steel_peak_field_limit_T_hypothesis=1.3)
    d['slot_fill_fraction']=p['turns_per_coil']*p['conductor_area_m2']/(p['slot_width_m']*p['slot_depth_m'])
    if d['slot_fill_fraction']>.6:raise ValueError('Conductor stock exceeds 60 percent slot fill')
    if e['linear_peak_field_limit_T']!=1.3 or e['wire_density_limit_RMS_A_mm2']>4:raise ValueError('Cannot relax declared material/current limits')
    if e['current_peak_A']<0 or e['slip_frequency_Hz']<=0 or e['phase_direction'] not in (-1,1):raise ValueError('Invalid source current/slip/phase')
    if not 1<=e['runtime_per_solve_s']<=90 or not 1<=e['maximum_nodes']<=400000:raise ValueError('Native resource budget exceeded')
    if min(e['mesh_m'],e['gap_mesh_m'],e['longitudinal_air_margin_m'],e['transverse_air_margin_m'])<=0:raise ValueError('Positive mesh and boundary dimensions required')
    if not 1<=len(e['scenarios'])<=3:raise ValueError('One to three native samples per candidate')
    if any(s['temperature_C'] not in (20.,80.) or not 0<=s['speed_m_s']<=20 or not .015<=s['gap_m']<=.02 for s in e['scenarios']):raise ValueError('Outside temperature/speed/gap sample domain')
    d['wire_length_m_per_coil']=p['turns_per_coil']*(2*(p['active_height_m']+p['pole_pitch_m'])+d['end_turn_extra_length_m'])
    d['coils_both_sides_per_m']=6/d['wavelength_m']
    d['copper_kg_per_m']=d['wire_length_m_per_coil']*p['conductor_area_m2']*8960*d['coils_both_sides_per_m']
    d['primary_steel_kg_per_m']=2*(p['backiron_m']+p['slot_depth_m']*(1-p['slot_width_m']/pitch))*p['active_height_m']*7850
    d['bare_primary_stock_kg_per_m']=d['copper_kg_per_m']+d['primary_steel_kg_per_m']
    d['bare_900m_stock_kg_per_direction']=900*d['bare_primary_stock_kg_per_m']
    d['bare_12_5m_module_stock_kg_both_sides']=p['primary_length_m']*d['bare_primary_stock_kg_per_m']
    d['physical_configuration']=deepcopy(p);d['motor_component_id']=identity({k:v for k,v in p.items() if k!='name'})
    return d


def stock(parameters):
    """Counted material stock, with train and wayside installation separated.

    Copper rows are equal-volume stock, not finished coil placement or a
    clearance demonstration. End-turn lengths are counted in the material.
    """
    p=parameters['physical'];d=definition(parameters);rows=[]
    def box(name,at,size,rho,material,installation,role):
        volume=size[0]*size[1]*size[2]
        rows.append(dict(id=name,kind='box',at_m=list(at),size_m=list(size),density_kg_m3=rho,
            volume_m3=volume,mass_kg=volume*rho,material=material,system='station-propulsion',
            cg_m=[a+s/2 for a,s in zip(at,size)],installation=installation,role=role,
            geometry_status='equivalent-volume-stock' if role=='copper-stock' else 'counted-material',
            motor_component_id=d['motor_component_id']))
    h=p['active_height_m'];L=p['primary_length_m'];half=p['secondary_thickness_m']/2;face=half+p['gap_each_side_m'];pitch=d['slot_pitch_m']
    box('station-secondary/active-fin',[-p['secondary_length_m']/2,-half,p['secondary_bottom_TOR_m']],
        [p['secondary_length_m'],p['secondary_thickness_m'],h],2710.,'aluminium-secondary','onboard','passive-fin')
    for side in (-1,1):
        outer=face+p['slot_depth_m']+p['backiron_m'];y=face+p['slot_depth_m'] if side>0 else -outer
        box(f'station-lim/primary/{side}/backiron',[0,y,p['secondary_bottom_TOR_m']],[L,p['backiron_m'],h],7850.,'linear-steel-hypothesis','wayside','backiron')
        intervals=[];left=0.
        for k in range(p['periods']*6):
            edge=(k+.5)*pitch-p['slot_width_m']/2;intervals.append((left,edge-left));left=edge+p['slot_width_m']
        intervals.append((left,L-left))
        for k,(x,length) in enumerate(intervals):
            box(f'station-lim/primary/{side}/tooth/{k}',[x,face if side>0 else -face-p['slot_depth_m'],p['secondary_bottom_TOR_m']],
                [length,p['slot_depth_m'],h],7850.,'linear-steel-hypothesis','wayside','tooth')
        thickness=d['copper_kg_per_m']/2/8960/h
        box(f'station-lim/primary/{side}/copper-stock',[0,face if side>0 else -face-thickness,p['secondary_bottom_TOR_m']],
            [L,thickness,h],8960.,'copper-conductor','wayside','copper-stock')
    return rows


def _case(parameters,scenario,confirmation):
    p=parameters['physical'];e=parameters['evaluation'];d=definition(parameters)
    gapmesh=e['gap_mesh_m']*(2/3 if confirmation else 1.)
    c=dict(speed_m_s=scenario['speed_m_s'],frequency_Hz=scenario['speed_m_s']/d['wavelength_m']+e['slip_frequency_Hz'],
        current_peak_A=e['current_peak_A'],current_RMS_A=e['current_peak_A']/sqrt(2),phase_direction=e['phase_direction'],
        temperature_C=scenario['temperature_C'],gap_each_side_m=scenario['gap_m'],periods=p['periods'],active_length_m=p['primary_length_m'],
        secondary_length_m=p['secondary_length_m'],secondary_start_x_m=(p['primary_length_m']-p['secondary_length_m'])/2,
        secondary_end_x_m=(p['primary_length_m']+p['secondary_length_m'])/2,mesh_m=e['mesh_m']*(.75 if confirmation else 1.),
        plate_gap_mesh_m=gapmesh,transverse_outer_air_margin_m=e['transverse_air_margin_m'],outer_margin_m=e['longitudinal_air_margin_m'],
        aluminium_conductivity_S_m=32e6 if scenario['temperature_C']==20 else 20e6,
        wire_current_density_RMS_A_mm2=e['current_peak_A']/sqrt(2)/(p['conductor_area_m2']*1e6))
    c['case_id']=identity(c);return c


def _effective_limit():
    inherited=resource.getrlimit(resource.RLIMIT_AS)
    return min([LIMIT_BYTES,*[v for v in inherited if v!=resource.RLIM_INFINITY]])


def _limits():
    limit=_effective_limit()
    resource.setrlimit(resource.RLIMIT_AS,(limit,limit))


def _metrics(parameters,c,folder,d):
    h=d['active_height_m'];F=base._scalar(folder/'force.txt').real*h;heat=base._scalar(folder/'joule.txt').real*h;P=base._scalar(folder/'power.txt')*h
    B=[]
    for group in re.findall(r'S(?:T|Q|P)\([^)]*\)\{([^}]+)\}',(folder/'steelB.pos').read_text()):B.extend(float(x) for x in group.split(','))
    peak=max(B) if B else None
    p=parameters['physical'];rho=1.724e-8*(1+.00393*(c['temperature_C']-20));R=rho*d['wire_length_m_per_coil']/p['conductor_area_m2'];Irms=c['current_RMS_A'];coils=p['periods']*2
    copper_phase=Irms**2*R*coils;phases=[]
    for phase in 'ABC':
        S=base._scalar(folder/('phase'+phase+'.txt'))*h
        phases.append(abs(complex(S.real+copper_phase,-S.imag))/Irms if Irms else 0.)
    residual=abs(P.real-heat-F*c['speed_m_s'])/max(1.,abs(P.real),heat,abs(F*c['speed_m_s']))
    J=c['wire_current_density_RMS_A_mm2'];paths=p['parallel_paths_per_phase'];V=max(phases)/paths
    material='pass' if peak is not None and peak<=1.3 else 'fail'
    return dict(force_N=F,secondary_Joule_W=heat,source_field_real_W=P.real,primary_copper_W=3*copper_phase,
        mechanical_W=F*c['speed_m_s'],maximum_steel_phasor_B_bound_T=peak,relative_energy_residual=residual,
        linear_material_screen=material,nonlinear_material_confirmation='unknown',wire_density_RMS_A_mm2=J,
        wire_density_screen='pass' if J<=4 else 'fail',slot_fill_fraction=d['slot_fill_fraction'],
        equal_group_phase_voltage_RMS_V=V,converter_phase_current_RMS_A=Irms*paths,
        arithmetic_voltage_screen='pass' if V<=parameters['evaluation']['dc_bus_V']/sqrt(6) else 'fail',
        actual_branch_voltage_and_current_sharing='unknown',thermal_equilibrium_C=None,
        finite_height_3D_current_closure='unknown',available_installed_force_N=None)


def _run(parameters,c,folder,source,tool):
    folder.mkdir(parents=True);d=definition(parameters);started=time.monotonic()
    (folder/'input.json').write_bytes(encoded(dict(physical=parameters['physical'],case=c,definition=d,source_sha256=source,tool=tool)))
    row=dict(case=c,execution='running',numerical_validity='unknown',model_domain='unknown',engineering_screen='unknown',raw_package_path=str(folder),**FLAGS)
    try:
        meta=native.mesh(folder,c,d);(folder/'mesh.json').write_bytes(encoded(meta))
        if meta['node_count']>parameters['evaluation']['maximum_nodes']:raise RuntimeError('Native node budget exceeded')
        (folder/'motor.pro').write_text(native.formulation(c,d))
        command=[str(GETDP),'motor.pro','-msh','motor.msh','-solve','Solve','-pos','Result','-v','4']
        proc=subprocess.run(command,cwd=folder,capture_output=True,text=True,timeout=parameters['evaluation']['runtime_per_solve_s'],
            preexec_fn=_limits,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
        (folder/'stdout.log').write_text(proc.stdout);(folder/'stderr.log').write_text(proc.stderr)
        if proc.returncode:raise RuntimeError('GetDP exit '+str(proc.returncode))
        metrics=_metrics(parameters,c,folder,d)
        row.update(execution='completed',numerical_validity='valid' if metrics['relative_energy_residual']<1e-6 else 'invalid',
            model_domain='within_linear_hypothesis' if metrics['linear_material_screen']=='pass' else 'outside_linear_material_hypothesis',metrics=metrics)
    except subprocess.TimeoutExpired as error:
        (folder/'stdout.log').write_bytes(error.stdout or b'');(folder/'stderr.log').write_bytes(error.stderr or b'')
        row.update(execution='interrupted',failure_reason='Native timeout; outputs retained')
    except Exception as error:
        (folder/'exception.log').write_text(type(error).__name__+': '+str(error)+'\n')
        row.update(execution='tool_error',failure_reason=str(error))
    row['elapsed_s']=time.monotonic()-started;row['evaluation_id']=identity(row);(folder/'result.json').write_bytes(encoded(row));return row


def evaluate(parameters,required_force_N,output,*,root=ROOT,confirmation=False):
    """Run <=3 operating samples, or same-model finer samples for comparison.

    The campaign coordinator enforces its aggregate12+4 native-case budget.
    Each call is capped to three60s solves, 3GiB address space and one thread.
    """
    root=Path(root).resolve();output=Path(output).resolve()
    if not isfinite(required_force_N) or required_force_N<=0:raise ValueError('Positive force requirement required')
    d=definition(parameters);source=source_map(root,PRODUCERS)
    tool=dict(getdp_sha256=digest(GETDP),gmsh_version=__import__('gmsh').__version__,threads=1,address_space_limit_bytes=_effective_limit())
    samples=parameters['evaluation']['scenarios']
    cases=[_case(parameters,s,confirmation) for s in samples]
    request=dict(parameters=parameters,required_force_N=required_force_N,confirmation=confirmation,cases=cases,source_sha256=source,tool=tool)
    cache_key=identity(request)
    if output.exists():
        old=json.loads((output/'result.json').read_bytes())
        if old['cache_key']!=cache_key:raise ValueError('Refuse mixed native cache identities')
        verify(output,root);return old
    output.mkdir(parents=True);(output/'request.json').write_bytes(encoded(request))
    rows=[_run(parameters,c,output/f'case-{i:02d}-{c["case_id"][:8]}',source,tool) for i,c in enumerate(cases)]
    if source!=source_map(root,PRODUCERS) or tool['getdp_sha256']!=digest(GETDP):raise ValueError('Method or native tool changed; unsealed execution retained')
    usable=[r for r in rows if r['execution']=='completed' and r['numerical_validity']=='valid']
    failures=[]
    if len(usable)!=len(rows):failures.append('incomplete_or_invalid_native_execution')
    for r in usable:
        m=r['metrics']
        if m['linear_material_screen']=='fail':failures.append('linear_steel_field_limit')
        if m['wire_density_screen']=='fail':failures.append('wire_density_limit')
        if m['force_N']<required_force_N:failures.append('insufficient_conditional_2D_force')
        if m['arithmetic_voltage_screen']=='fail':failures.append('necessary_voltage_bound')
    result=dict(schema='osr-wheel-LIM-search-evaluation/1',cache_key=cache_key,motor_component_id=d['motor_component_id'],physical=parameters['physical'],
        execution='completed' if len(usable)==len(rows) else 'incomplete',numerical_validity=('valid_finer_samples_require_comparison' if confirmation else 'valid_samples_require_refinement') if len(usable)==len(rows) else 'unknown',
        model_domain='outside' if any(r['model_domain']=='outside_linear_material_hypothesis' for r in rows) else 'unknown',
        engineering_screen='fail' if failures else 'unknown',failure_reasons=sorted(set(failures)),required_force_N=required_force_N,
        cases=rows,native_case_count=len(rows),confirmation=confirmation,source_sha256=source,tool=tool,
        raw_package_path=str(output),complete_installed_force_map=False,available_installed_force_N=None,
        missing_evidence=['Nonlinear steel/material correlation','Finite height and end-return3D fields','Local-field and air-boundary convergence',
            'Actual parallel branch flux/current sharing','Cooling and repeated sectional duty','Full transient inverter/section handoff','Temperature, speed and gap operating envelope'],same_model_confirmation=confirmation,independent_domain_confirmation=False,**FLAGS)
    result['evaluation_id']=identity(result);(output/'result.json').write_bytes(encoded(result))
    m=dict(source_sha256=source,files_sha256={p.relative_to(output).as_posix():digest(p) for p in sorted(output.rglob('*')) if p.is_file()},**FLAGS)
    m['manifest_id']=identity(m);(output/'manifest.json').write_bytes(encoded(m));return result


def verify(output,root=ROOT):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes());r=json.loads((output/'result.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Native search receipt differs')
    if any(digest(Path(root)/n)!=h for n,h in m['source_sha256'].items()):raise ValueError('Native search method differs')
    if {p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file() and p.name!='manifest.json'}!=m['files_sha256']:raise ValueError('Native search payload differs')
    if r['evaluation_id']!=identity({k:v for k,v in r.items() if k!='evaluation_id'}):raise ValueError('Native search evaluation differs')
    if any(r.get(k) is not v or m.get(k) is not v for k,v in FLAGS.items()):raise ValueError('Search cannot qualify railway hardware')
    return dict(verified=True,evaluation_id=r['evaluation_id'],native_case_count=r['native_case_count'],**FLAGS)
