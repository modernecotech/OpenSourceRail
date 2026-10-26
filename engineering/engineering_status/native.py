"""Scheduled native-method checks, never candidate journey performance."""
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
from . import ROOT,FLAGS
from .contracts import encoded,identity


def write(path,value):
    from engineering.design_search.storage import atomic_immutable
    atomic_immutable(Path(path),encoded(value))


def inventory(directory,exclude=()):
    result={}
    for path in sorted(Path(directory).rglob('*')):
        if path.is_symlink():raise ValueError('ordinary native-method artifacts required')
        if path.is_file() and path.relative_to(directory).as_posix() not in exclude:
            result[path.relative_to(directory).as_posix()]=sha256(path.read_bytes()).hexdigest()
    return result


def sources(root=ROOT):
    from engineering.trip_dynamics import chrono_runner,formation,scenario
    from engineering.trip_dynamics.fixtures.magnetics import run_fixture
    from . import contracts
    modules=(chrono_runner,formation,scenario,run_fixture,contracts)
    paths={Path(m.__file__).resolve() for m in modules}|{Path(__file__).resolve(),Path(__file__).with_name('__init__.py')}
    paths.update(p for p in (Path(__file__).with_name('__main__.py'),Path(__file__).parent/'tests/test_native.py') if p.is_file())
    paths.update(Path(run_fixture.__file__).parent/n for n in ('slab.geo','slab.pro'))
    extra={}
    try:
        from engineering.equipped_vehicle import structures
        paths.add(Path(structures.__file__).resolve())
        extra=structures.sources(root)
        if hasattr(structures,'source_paths'):paths.update(Path(p) for p in structures.source_paths())
    except ImportError:pass
    records={}
    for path in paths:
        parts=path.parts;name='/'.join(parts[parts.index('engineering'):])
        records[name]=sha256(path.read_bytes()).hexdigest()
    for name,value in extra.items():
        if name in records and records[name]!=value:raise ValueError('native method source workspaces differ')
        records[name]=value
    return dict(sorted(records.items()))


def _bounded(command,directory,seconds=300):
    env=dict(os.environ,PYTHONPATH=str(ROOT),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    started=time.monotonic()
    with (directory/'stdout.log').open('xb') as stdout,(directory/'stderr.log').open('xb') as stderr:
        process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
        try:code=process.wait(timeout=seconds);timed=False
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGKILL);process.wait();code=process.returncode;timed=True
    return dict(command=command,returncode=code,timed_out=timed,deadline_s=seconds,elapsed_s=time.monotonic()-started)


def tool(path,flag):
    if path is None or not Path(path).is_file():return None
    path=Path(path).resolve();p=subprocess.run([str(path),flag],capture_output=True,text=True,timeout=15)
    return dict(path=str(path),sha256=sha256(path.read_bytes()).hexdigest(),version_stdout=p.stdout,
                version_stderr=p.stderr,probe_returncode=p.returncode)


def tools(chrono_python,getdp,ccx):
    python=tool(chrono_python,'--version');backend=None
    if python:
        p=subprocess.run([python['path'],'-c','import json; from engineering.trip_dynamics.chrono_runner import solver_info; print(json.dumps(solver_info(),sort_keys=True))'],
            capture_output=True,text=True,timeout=30,cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT)))
        if p.returncode==0:backend=json.loads(p.stdout)
    return dict(chrono=dict(python=python,backend=backend),magnetic=tool(getdp,'-version'),structure=tool(ccx,'-v'))


def assess_chrono(value):
    from engineering.trip_dynamics.chrono_runner import compare_timesteps
    from engineering.trip_dynamics.formation import definition
    from engineering.trip_dynamics.scenario import scenario
    a,b=value['coarse'],value['fine']
    for r,step in ((a,.01),(b,.005)):
        if (r.get('scope')!='Genuine Chrono rigid-body/coupler integration with prescribed ideal station force and ideal support; benchmark only'
                or r.get('physical_accepted') is not False or r.get('journey_accepted') is not False
                or r['dt_s']!=step or r['backend'].get('fallback') is not False
                or r['inputs']['scenario']['candidate_id'] is not None):
            raise ValueError('native method cannot assert actual candidate dynamics')
        expected_vehicle=definition([30000.]*6)
        if r['inputs']['vehicle']!=expected_vehicle or r['inputs']['vehicle_id']!=expected_vehicle['vehicle_id']:
            raise ValueError('declared synthetic method vehicle differs')
        s=r['inputs']['scenario']
        if (s['case_id']!='scheduled-native-2000-AW3' or s['distance_m']!=2000 or s['load_case']!='AW3'
                or s['cars']!=6 or s['car_length_m']!=17. or s['powered_zone_m']!=350.
                or s['max_speed_m_s']!=20. or s['acceleration_m_s2']!=.8 or s['fault'] is not None):
            raise ValueError('scheduled native scenario differs')
        expected_scenario=scenario('scheduled-native-2000-AW3',2000,'AW3',mode='benchmark',mechanical_step_s=step)
        if s!=expected_scenario or r['inputs']['scenario_id']!=s['scenario_id']:raise ValueError('native scenario factory identity differs')
        trace=r['trace']
        if len(r['final_state'])!=6 or len(trace)<100 or abs(trace[0]['time_s'])>1e-9 or abs(trace[-1]['time_s']-125.)>step:
            raise ValueError('six-car trajectory requires full 0 to 125 second coverage')
        if any(b['time_s']<=a['time_s'] for a,b in zip(trace,trace[1:])):raise ValueError('native trajectory time is not monotonic')
        for sample in trace:
            if len(sample['cars'])!=6:raise ValueError('native trace requires every car')
            for state in sample['cars']:
                if any(len(state[k])!=3 or not all(type(x) in (int,float) and math.isfinite(x) for x in state[k]) for k in ('position_m','velocity_m_s')):
                    raise ValueError('finite three-dimensional native states required')
        distance=max(abs(state['position_m'][0]+i*17.5-2000) for i,state in enumerate(r['final_state']))
        speed=max(abs(state['velocity_m_s'][0]) for state in r['final_state'])
        if not math.isclose(distance,r['summary']['terminal_max_distance_error_m'],abs_tol=1e-9) or not math.isclose(speed,r['summary']['terminal_max_speed_m_s'],abs_tol=1e-9):
            raise ValueError('native endpoint summary differs from final states')
        terminal=(r['state']=='completed' and distance<=.2 and speed<=.05)
        if r['summary']['terminal_screen_pass']!=terminal:raise ValueError('native endpoint disposition differs')
    convergence=compare_timesteps(a,b)
    coarse_error=abs(a['summary']['relative_work_energy_residual']);fine_error=abs(b['summary']['relative_work_energy_residual'])
    passed=(all(r['summary']['terminal_screen_pass'] for r in (a,b))
        and convergence['maximum_sampled_trajectory_difference_m']<=.15
        and fine_error<=coarse_error*1.15+1e-9)
    return dict(state='pass' if passed else 'fail',timestep_comparison=convergence,
        coarse_relative_work_energy_residual=coarse_error,fine_relative_work_energy_residual=fine_error,
        scope='Two executed ideal-force native-method samples; not a continuum convergence proof or physical journey')


def worker(kind,output,root,getdp=None,ccx=None):
    output=Path(output)
    if kind=='chrono':
        from engineering.trip_dynamics.scenario import scenario
        from engineering.trip_dynamics.chrono_runner import run_benchmark
        result={}
        for name,step in (('coarse',.01),('fine',.005)):
            case=scenario('scheduled-native-2000-AW3',2000,'AW3',mode='benchmark',mechanical_step_s=step)
            result[name]=run_benchmark(case,[30000.]*6,dt_s=step)
        result['assessment']=assess_chrono(result)
    elif kind=='magnetic':
        from engineering.trip_dynamics.fixtures.magnetics.run_fixture import run
        result=run(output/'field',getdp,timeout_s=120)
    elif kind=='structure':
        from engineering.equipped_vehicle.structures import run_structural_fixture
        result=run_structural_fixture(output/'structure',ccx=ccx,root=root)
    else:raise ValueError('declared native method required')
    write(output/'worker-result.json',result)
    return result


def _assessment(kind,value):
    if kind=='chrono':return assess_chrono(value)
    if kind=='magnetic':
        mu0=4*math.pi*1e-7;B=mu0*1000+1.5*math.tanh(1000/1500);force=B*B/(2*mu0)*.01
        records=value['records']
        if len(records)!=2 or value.get('candidate_id') is not None or value.get('physical_accepted') is not False:
            raise ValueError('magnetic method receipt cannot become candidate evidence')
        passed=all(r['returncode']==0 and r['nonlinear_converged'] and abs(r['mean_air_Bz_T']/B-1)<1e-6
                   and abs(r['air_pressure_force_N']/force-1)<1e-6 for r in records)
        difference=abs(records[0]['air_pressure_force_N']-records[1]['air_pressure_force_N'])/force
        return dict(state='pass' if passed and difference<1e-6 else 'fail',relative_mesh_force_difference=difference,
                    scope='Manufactured nonlinear 3D constitutive/method check; not a train-force map')
    # The producer independently re-parses solver output during readback.
    if value.get('method_screen')=='unknown':return dict(state='unknown',scope='Native composite method unavailable; no equipped body credit')
    passed=(value['method_screen']=='pass') if value.get('method_screen') in {'pass','fail'} else value.get('passed',value.get('fixture_passed',value.get('numerical_screen_pass')))
    if type(passed) is not bool:raise ValueError('explicit structural method disposition required')
    return dict(state='pass' if passed else 'fail',scope='Native composite coupon only; no equipped body credit')


def run(output,*,root=ROOT,chrono_python=None,getdp=None,ccx=None):
    output=Path(output).absolute();output.mkdir(parents=True,exist_ok=False)
    before=sources(root);pinned=tools(chrono_python,getdp,ccx or shutil.which('ccx'))
    request=dict(schema='osr-scheduled-native-methods/1',source_sha256=before,
        methods=['chrono','magnetic','structure'],budget=dict(seconds_per_method=300,ordinary_workers=1),
        synthetic_comparison_masses_kg_per_car=[30000.]*6,candidate_id=None,tools=pinned,root=str(Path(root).resolve()),**FLAGS)
    request['request_id']=identity(request);write(output/'request.json',request)
    rows=[]
    for kind in request['methods']:
        directory=output/kind;directory.mkdir()
        python=chrono_python if kind=='chrono' else sys.executable
        available=(pinned['chrono']['backend'] or {}).get('available') is True if kind=='chrono' else pinned[kind] is not None
        if not available or python is None or not Path(python).is_file():
            rows.append(dict(method=kind,execution='not-run',state='unknown',reason='Explicit native tool unavailable'));continue
        command=[str(python),'-m','engineering.engineering_status','native-worker','--kind',kind,'--output',str(directory),'--root',str(root)]
        if getdp is not None:command+=['--getdp',str(getdp)]
        if pinned['structure'] is not None:command+=['--ccx',pinned['structure']['path']]
        execution=_bounded(command,directory)
        if execution['returncode']==0 and not execution['timed_out']:
            try:
                value=json.loads((directory/'worker-result.json').read_bytes());assessment=_assessment(kind,value)
            except (OSError,KeyError,TypeError,ValueError) as error:
                rows.append(dict(method=kind,execution='tool-error',state='fail',reason=str(error),worker_execution=execution));continue
            rows.append(dict(method=kind,execution='completed',assessment=assessment,state=assessment['state'],worker_execution=execution))
        else:rows.append(dict(method=kind,execution='interrupted' if execution['timed_out'] else 'failed',state='fail',worker_execution=execution))
    if sources(root)!=before:raise ValueError('native-method source changed during campaign')
    result=dict(schema=request['schema'],request_id=request['request_id'],source_sha256=before,rows=rows,
        method_campaign_passed=all(r['state']=='pass' for r in rows),
        scope='Numerical-method maintenance only; no candidate performance or physical acceptance',**FLAGS)
    result['evaluation_id']=identity(result);write(output/'result.json',result)
    write(output/'manifest.json',dict(source_sha256=before,files_sha256=inventory(output,('manifest.json',)),**FLAGS))
    return result


def _verify_magnetic(directory,value,pinned):
    from engineering.trip_dynamics.fixtures.magnetics import run_fixture
    if value['getdp_executable_sha256']!=pinned['sha256']:raise ValueError('magnetic solver differs from request')
    if 'getdp_version' in value and value['getdp_version']!=(pinned['version_stdout']+pinned['version_stderr']).strip():raise ValueError('magnetic native solver version differs')
    fixture=Path(run_fixture.__file__).parent
    if value['source_sha256']!={n:sha256((fixture/n).read_bytes()).hexdigest() for n in ('slab.geo','slab.pro','run_fixture.py')}:
        raise ValueError('manufactured magnetic source differs')
    for record,(name,h) in zip(value['records'],(('coarse',.025),('fine',.0125))):
        d=directory/'field'/name
        if record['name']!=name or record['mesh_size_m']!=h or record['files_sha256']!=inventory(d):raise ValueError('magnetic native grid artifacts differ')
        expected_command=[pinned['path'],'slab.pro','-msh','slab.msh','-solve','Solve','-pos','Results']
        if record['command']!=expected_command or not (d/'slab.msh').is_file():raise ValueError('native 3D mesh/solver command missing')
        import gmsh
        gmsh.initialize();gmsh.option.setNumber('General.Terminal',0)
        try:
            gmsh.open(str(d/'slab.msh'));types,tags,_=gmsh.model.mesh.getElements(3)
            count=sum(len(t) for kind,t in zip(types,tags) if kind==4)
        finally:gmsh.finalize()
        if count<=0 or count!=record['tetrahedra']:raise ValueError('positive actual native tetrahedron count required')
        expected=(fixture/'slab.geo').read_text().replace('h = {0.025}',f'h = {{{h:.17g}}}')
        if (d/'slab.geo').read_text()!=expected or (d/'slab.pro').read_bytes()!=(fixture/'slab.pro').read_bytes():raise ValueError('manufactured magnetic input differs')
        bz=float((d/'mean-Bz.txt').read_text().split()[-1]);force=float((d/'air-force.txt').read_text().split()[-1])
        residues=re.findall(r'PICARD\s+(\d+)\s+([\deE+.-]+)\s+([\deE+.-]+)',(d/'getdp.stdout.log').read_text())
        if not residues:raise ValueError('native nonlinear residual record missing')
        iteration,absolute,relative=residues[-1]
        if (bz!=record['mean_air_Bz_T'] or force!=record['air_pressure_force_N']
                or int(iteration)!=record['nonlinear_iterations'] or float(absolute)!=record['residual_absolute'] or float(relative)!=record['residual_relative']
                or record['nonlinear_converged']!=(float(absolute)<=1e-10 or float(relative)<=1e-10)):
            raise ValueError('native magnetic scalars differ from solver output')


def verify(output,root=ROOT):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes());r=json.loads((output/'result.json').read_bytes());q=json.loads((output/'request.json').read_bytes())
    if m['source_sha256']!=sources(root) or q['source_sha256']!=m['source_sha256'] or r['source_sha256']!=m['source_sha256']:raise ValueError('native-method sources differ')
    if inventory(output,('manifest.json',))!=m['files_sha256']:raise ValueError('native-method artifacts differ')
    if q['request_id']!=identity({k:v for k,v in q.items() if k!='request_id'}) or r['request_id']!=q['request_id']:raise ValueError('native-method request differs')
    if (q['schema']!='osr-scheduled-native-methods/1' or q['methods']!=['chrono','magnetic','structure']
            or q['budget']!=dict(seconds_per_method=300,ordinary_workers=1)
            or q['synthetic_comparison_masses_kg_per_car']!=[30000.]*6 or q['candidate_id'] is not None):raise ValueError('declared native method contract differs')
    pinned=q['tools']
    for name in ('magnetic','structure'):
        t=pinned[name]
        if t is not None and t!=tool(t['path'],'-version' if name=='magnetic' else '-v'):raise ValueError('native method tool differs')
    if pinned['chrono']['python'] is not None:
        p=pinned['chrono']['python']
        current=tools(p['path'],None,None)['chrono']
        if current!=pinned['chrono']:raise ValueError('native Chrono interpreter/backend differs')
    if r['evaluation_id']!=identity({k:v for k,v in r.items() if k!='evaluation_id'}):raise ValueError('native-method result differs')
    if [x['method'] for x in r['rows']]!=['chrono','magnetic','structure']:raise ValueError('complete native method inventory required')
    for row in r['rows']:
        if row['execution']=='completed':
            e=row['worker_execution']
            if e['returncode']!=0 or e['timed_out'] or e['deadline_s']!=300:raise ValueError('completed native worker failed')
            value=json.loads((output/row['method']/'worker-result.json').read_bytes())
            if row['method']=='structure':
                from engineering.equipped_vehicle.structures import verify_structural_fixture
                verify_structural_fixture(output/'structure/structure',root=root)
                raw=json.loads((output/'structure/structure/result.json').read_bytes())
                if raw!=value:raise ValueError('structural worker summary differs from parsed fixture')
                if value['tool']!=pinned['structure']:raise ValueError('structural solver differs from parent native request')
            elif row['method']=='magnetic':_verify_magnetic(output/'magnetic',value,pinned['magnetic'])
            else:
                for key in ('coarse','fine'):
                    if value[key]['backend']!=pinned['chrono']['backend']:raise ValueError('executed native Chrono backend differs from request')
            if row['assessment']!=_assessment(row['method'],value) or row['state']!=row['assessment']['state']:raise ValueError('native-method derived disposition differs')
        elif row.get('state')=='pass':raise ValueError('unexecuted native method cannot pass')
    if r['method_campaign_passed']!=all(x['state']=='pass' for x in r['rows']):raise ValueError('native method aggregate differs')
    for value in (q,r,m):
        if any(value.get(k) is not False for k in FLAGS):raise ValueError('native method cannot accept a train')
    return dict(current=True,method_campaign_passed=r['method_campaign_passed'],evaluation_id=r['evaluation_id'],physical_accepted=False)
