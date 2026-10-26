"""Native maintenance must preserve missing tools, domains and raw outputs."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import pytest
from engineering.engineering_status import native as n
from engineering.trip_dynamics.scenario import scenario
from engineering.trip_dynamics.formation import definition


def chrono_pair():
    value={}
    for name,step in (('coarse',.01),('fine',.005)):
        trace=[]
        for k in range(1251):
            t=k/10.;x=.4*t*t if t<=25 else 250+20*(t-25) if t<=100 else 2000-.4*(125-t)**2
            speed=.8*t if t<=25 else 20. if t<=100 else .8*(125-t)
            trace.append(dict(time_s=t,cars=[dict(position_m=[x-i*17.5,0,0],velocity_m_s=[speed,0,0]) for i in range(6)]))
        states=trace[-1]['cars'];spec=definition([30000.]*6)
        case=scenario('scheduled-native-2000-AW3',2000,'AW3',mode='benchmark',mechanical_step_s=step)
        value[name]=dict(scope='Genuine Chrono rigid-body/coupler integration with prescribed ideal station force and ideal support; benchmark only',
            physical_accepted=False,journey_accepted=False,dt_s=step,backend={'fallback':False},
            inputs=dict(scenario=case,vehicle=spec,vehicle_id=spec['vehicle_id'],scenario_id=case['scenario_id']),
            state='completed',summary=dict(relative_work_energy_residual=0.,terminal_screen_pass=True,
                terminal_max_distance_error_m=0.,terminal_max_speed_m_s=0.,
                peak_coupler_force_N=[0.]*5,peak_coupler_extension_m=[0.]*5,work_energy_residual_J=0.),
            final_state=deepcopy(states),trace=trace)
    return value


def test_native_ideal_pair_cannot_accept_different_distance_or_forged_endpoint():
    value=chrono_pair();assert n.assess_chrono(value)['state']=='pass'
    value['fine']['inputs']['scenario']['distance_m']=1500
    with pytest.raises(ValueError,match='scenario differs'):n.assess_chrono(value)
    value=chrono_pair();value['fine']['final_state'][0]['position_m'][0]=1900
    with pytest.raises(ValueError,match='final states'):n.assess_chrono(value)
    value=chrono_pair();value['fine']['physical_accepted']=True
    with pytest.raises(ValueError,match='candidate dynamics'):n.assess_chrono(value)
    value=chrono_pair();value['fine']['trace']=value['fine']['trace'][-1:]
    with pytest.raises(ValueError,match='full 0 to 125'):n.assess_chrono(value)
    value=chrono_pair();value['fine']['trace'][10]['cars'].pop()
    with pytest.raises(ValueError,match='every car'):n.assess_chrono(value)


def test_unavailable_methods_remain_unknown_without_a_surrogate(tmp_path,monkeypatch):
    monkeypatch.setattr(n,'sources',lambda root:{'source/fixture':'a'*64})
    monkeypatch.setattr(n,'tools',lambda *a,**k:dict(chrono={'python':None,'backend':None},magnetic=None,structure=None))
    result=n.run(tmp_path/'run',root=tmp_path)
    assert not result['method_campaign_passed']
    assert [r['state'] for r in result['rows']]==['unknown']*3
    assert all(r['execution']=='not-run' for r in result['rows'])
    assert n.verify(tmp_path/'run',tmp_path)['current']
    assert n._assessment('structure',dict(method_screen='unknown'))['state']=='unknown'


def test_resealed_request_cannot_relax_native_budget(tmp_path,monkeypatch):
    monkeypatch.setattr(n,'sources',lambda root:{'source/fixture':'a'*64})
    monkeypatch.setattr(n,'tools',lambda *a,**k:dict(chrono={'python':None,'backend':None},magnetic=None,structure=None))
    d=tmp_path/'run';n.run(d,root=tmp_path)
    q=json.loads((d/'request.json').read_bytes());r=json.loads((d/'result.json').read_bytes());m=json.loads((d/'manifest.json').read_bytes())
    q['budget']['seconds_per_method']=600;q['request_id']=n.identity({k:v for k,v in q.items() if k!='request_id'})
    r['request_id']=q['request_id'];r['evaluation_id']=n.identity({k:v for k,v in r.items() if k!='evaluation_id'})
    (d/'request.json').write_bytes(n.encoded(q));(d/'result.json').write_bytes(n.encoded(r))
    m['files_sha256']=n.inventory(d,('manifest.json',));(d/'manifest.json').write_bytes(n.encoded(m))
    with pytest.raises(ValueError,match='contract differs'):n.verify(d,tmp_path)


def test_resealed_magnetic_scalar_is_rejected_by_native_output_parser(tmp_path):
    from engineering.trip_dynamics.fixtures.magnetics import run_fixture
    fixture=Path(run_fixture.__file__).parent;records=[]
    for name,h in (('coarse',.025),('fine',.0125)):
        d=tmp_path/'field'/name;d.mkdir(parents=True)
        (d/'slab.geo').write_text((fixture/'slab.geo').read_text().replace('h = {0.025}',f'h = {{{h:.17g}}}'))
        (d/'slab.pro').write_bytes((fixture/'slab.pro').read_bytes())
        (d/'slab.msh').write_text('$MeshFormat\n2.2 0 8\n$EndMeshFormat\n$Nodes\n4\n1 0 0 0\n2 1 0 0\n3 0 1 0\n4 0 0 1\n$EndNodes\n$Elements\n1\n1 4 0 1 2 3 4\n$EndElements\n')
        (d/'mean-Bz.txt').write_text('1.0\n');(d/'air-force.txt').write_text('2.0\n');(d/'getdp.stdout.log').write_text('PICARD 4 1e-12 1e-12\n')
        records.append(dict(name=name,mesh_size_m=h,files_sha256=n.inventory(d),mean_air_Bz_T=1.,air_pressure_force_N=2.,
            nonlinear_iterations=4,residual_absolute=1e-12,residual_relative=1e-12,nonlinear_converged=True,tetrahedra=1,
            command=['/getdp','slab.pro','-msh','slab.msh','-solve','Solve','-pos','Results']))
    value=dict(getdp_executable_sha256='b'*64,source_sha256={name:sha256((fixture/name).read_bytes()).hexdigest() for name in ('slab.geo','slab.pro','run_fixture.py')},records=records)
    n._verify_magnetic(tmp_path,value,{'sha256':'b'*64,'path':'/getdp'})
    value['records'][0]['air_pressure_force_N']=9999.
    with pytest.raises(ValueError,match='solver output'):n._verify_magnetic(tmp_path,value,{'sha256':'b'*64,'path':'/getdp'})
