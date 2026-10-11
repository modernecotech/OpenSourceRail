#!/usr/bin/env python3
"""Execute retained integration pilots; never synthesize physical completion."""
from pathlib import Path
import argparse,gzip,hashlib,json,os,subprocess,sys
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):os.environ[key]='1'
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from osr_mech.engineering_definition import fingerprint,load_definition
from engineering.integration_programme import battery,controllers,flexible,joints,stations,lifecycle,osrd_examples,profile_examples
from engineering.integration_programme.flexible_vehicle import FlexibleVehicle
from engineering.integration_programme.correspondence import audit
from engineering.civil_exploration.spatial_structure import SpatialStructure
from engineering.civil_exploration.spatial_vehicle import SpatialVehicle,loaded_model
from engineering.civil_exploration.spatial_structure import Route


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,value):p.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
def sources():
    data=ROOT/'engineering/integration_programme/data'
    paths=[*sorted((ROOT/'engineering/integration_programme').rglob('*.py')),data/'controller-input.json',data/'controller-basis.json',ROOT/'crates/osr-sim/examples/twin_controller_bridge.rs',ROOT/'Cargo.lock',Path(__file__)]
    paths += sorted(p for sub in ('osrd','contact') for p in (data/sub).iterdir() if p.is_file())
    paths += sorted((ROOT/'engineering/civil_exploration').glob('*.py'))
    paths += sorted((ROOT/'crates').rglob('*.rs'))+sorted((ROOT/'crates').rglob('Cargo.toml'))+[ROOT/'Cargo.toml']
    return {p.relative_to(ROOT).as_posix():sha(p) for p in paths}


def run(output,package,service):
    if output.exists():raise ValueError('use a fresh integration evidence directory')
    frozen_sources=sources()
    subprocess.run([sys.executable,str(ROOT/'tools/automation/design-best-practice-twin.py'),'verify','--output',str(package)],check=True)
    if service:subprocess.run([sys.executable,str(ROOT/'tools/automation/shared-service-envelope.py'),'verify','--output',str(service.parent)],check=True)
    model=load_definition(package/'model.json');pack=load_definition(package/'battery.json');cfg=fingerprint(model);output.mkdir(parents=True)
    maps=dict(soc=[.1,.5,.9],temperature_c=[-10.,25.,60.],ocv_v=[[pack['nominal_voltage_v']*f for f in (.95,.99,1.03)],[pack['nominal_voltage_v']*f for f in (.96,1.,1.04)],[pack['nominal_voltage_v']*f for f in (.965,1.005,1.045)]],resistance_ohm=[[pack['resistance_ohm']*2]*3,[pack['resistance_ohm']]*3,[pack['resistance_ohm']*.9]*3],capacity_reference_soh=1.,basis='synthetic verification maps; not manufacturer data or calibrated physical properties')
    write(output/'battery-maps.json',maps);request=load_definition(ROOT/'engineering/integration_programme/data/controller-input.json');request['configuration_sha256']=cfg
    binary=ROOT/'target/debug/examples/twin_controller_bridge'
    subprocess.run(['cargo','build','-p','osr-sim','--example','twin_controller_bridge','--quiet'],cwd=ROOT,check=True)
    result=controllers.run(pack,maps,request,binary)
    if not result['fault_isolated'] or result['maximum_electrical_energy_residual_j']>1e-5:raise ValueError('native control/energy experiment failed')
    result['configuration_sha256']=cfg;result['binary_sha256']=sha(binary);write(output/'controller-execution.json',result)
    modes=flexible.beam_modes(18.5,400.,3e8);write(output/'beam-modes.json',modes);write(output/'modal-attachment.json',flexible.modal_joint(modes,4.,2e6))
    structure=SpatialStructure(model['bridge'],Route(load_definition(package/'spatial_configuration.json')['route']),deck_mesh=2,rail_step=2.)
    write(output/'civil-cad-analysis-audit.json',audit(model,load_definition(package/'infrastructure.json'),structure,load_definition(package/'spatial_configuration.json')))
    vehicle=FlexibleVehicle(model,load_definition(package/'spatial_configuration.json')['joint_laws'])
    K,C,M,(_,plans)=vehicle.matrices(Route(load_definition(package/'spatial_configuration.json')['route']),0.,0.)
    write(output/'flexible-vehicle-operators.json',dict(configuration_sha256=cfg,rigid_dofs=vehicle.rigid_size,flexible_dofs=vehicle.size-vehicle.rigid_size,
        total_mass_kg=vehicle.total_mass,static_reaction_n=sum(c['static_n'] for c in vehicle.contacts),operator_sha256=fingerprint(dict(K=K.tolist(),C=C.tolist(),M=M.tolist())),
        joint_jacobian_sha256=fingerprint([p['J'].tolist() for p in plans]),represented_car_ids=sorted(vehicle.modal),
        basis='original reduced Euler-Bernoulli carbody transfer, uniform equivalent body mass, declared EI and damping; shell correlation separate',
        static_modal_coordinates=vehicle.static_coordinates[vehicle.rigid_size:].tolist(),full_spatial_dynamic_execution=False,physical_validation=False))
    write(output/'contact-profile-examples.json',dict(profiles=[profile_examples.parse(name) for name in ('MBench_S1002_v3.prw','MBench_UIC60_v3.prr')],curve_adopted=False,physical_validation=False))
    stock,provenance=osrd_examples.retained_example()
    write(output/'osrd-example-acceleration.json',osrd_examples.acceleration_experiment(stock))
    write(output/'osrd-twin-comparison.json',dict(configuration_sha256=cfg,upstream_example=provenance,
        example_mass_kg=stock['mass'],example_length_m=stock['length'],compiled_osr_mass_kg=vehicle.total_mass,compiled_osr_length_m=model['family_definition']['length_m'],
        example_supply_modes=list(stock['effort_curves']['modes']),osr_pack_nominal_voltage_v=pack['nominal_voltage_v'],
        resistance_coefficient_units=['N/kg','(N/kg)/(m/s)','(N/kg)/(m/s)^2'],
        reference_effort_n_at_15mps=osrd_examples.effort(stock,15.),reference_resistance_n_at_15mps=osrd_examples.resistance(stock,15.),
        source_curve_adopted_as_osr_rating=False,source_mass_adopted=False,physical_validation=False,
        open_domains=['actual inverter/motor/gearing curves','pack-to-supply compatibility','calibrated Davis coefficients','braking/adhesion and stopping envelopes','full spatial controller force feedback']))
    shell=flexible.carbody_shell(output/'carbody-shell');write(output/'carbody-shell/definition.json',shell)
    with (output/'carbody-shell/native.log').open('w') as log:
        proc=subprocess.run(['ccx','-i','carbody'],cwd=output/'carbody-shell',stdout=log,stderr=subprocess.STDOUT,timeout=300)
    shell['native_exit_code']=proc.returncode;shell['native_results_present']=(output/'carbody-shell/carbody.frd').is_file() and (output/'carbody-shell/carbody.dat').is_file()
    shell['modal_result']=flexible.read_native_modes(output/'carbody-shell/carbody.dat')
    if proc.returncode or not shell['native_results_present']:raise RuntimeError('native shell execution failed; evidence retained')
    write(output/'shell-execution.json',shell)
    n=[dict(id='platform'),dict(id='concourse'),dict(id='safe',exit=True)];e=[dict(id='stairs',**{'from':'platform','to':'concourse'},mobility=['walking'],capacity_people_s=2.,travel_s=8.),dict(id='lift',**{'from':'platform','to':'concourse'},mobility=['walking','wheelchair'],capacity_people_s=.5,travel_s=20.),dict(id='exit',**{'from':'concourse','to':'safe'},mobility=['walking','wheelchair'],capacity_people_s=3.,travel_s=8.)];c=[dict(id='walking',node='platform',people=150.,mobility='walking'),dict(id='wheelchair',node='platform',people=5.,mobility='wheelchair')]
    write(output/'station-cases.json',dict(healthy=stations.simulate(n,e,c),lift_power_outage=stations.simulate(n,e,c,outages=[dict(edge='lift',start_s=0,end_s=1000)]),exit_fire_blocked=stations.simulate(n,e,c,outages=[dict(edge='exit',start_s=0,end_s=1000)]),all_inputs_basis='OSR synthetic queue verification; no local passenger counts or adopted fire limits'))
    entries=[dict(id=category,category=category,quantity=1.,unit_price_usd=None,year=0. if category in {'manufacture','transport','erection','temporary-works','land-access'} else 30. if category=='decommission' else 10.,basis='unpriced required installed lifecycle scope') for category in sorted(lifecycle.REQUIRED)]
    write(output/'civil-lifecycle-ledger.json',entries);write(output/'civil-lifecycle-review.json',lifecycle.installed_cost(entries,years=30,discount_rate=.03))
    if service:
        dynamics=load_definition(service/'dynamics.json')
        if dynamics['hardware_definition_sha256']!=cfg:raise ValueError('joint pilot and passage use different full train configurations')
        history=service/'history.jsonl.gz';group=joints.battery_mount(pack,dict(diameter_m=.012,grip_m=.018,youngs_pa=210e9));row=next(r for r in model['instances'] if r['id']=='car-1/battery');service_cfg=load_definition(service/'configuration.json');entry=next(t for t in service_cfg['traffic'] if t['id']=='train-A');actual_vehicle=SpatialVehicle(loaded_model(model,entry['load_case']),service_cfg['joint_laws'],equipment_mounts=service_cfg.get('equipment_mounts'));body_cg=actual_vehicle.groups['car-1']['cg'];import numpy as np
        cg=np.asarray(pack['properties']['cg_m']);Q=np.asarray(row['transform']['rotation']);offset=np.asarray(row['transform']['translation_m'])+Q@cg-body_cg;I=Q@np.asarray(pack['properties']['inertia_tensor_kg_m2'])@Q.T;mass=pack['properties']['mass_kg'];peak=None;count=0
        with gzip.open(history,'rt') as stream:
            for line in stream:
                h=json.loads(line);b=next(r for r in h['bodies'] if r['train']=='train-A' and r['body']=='car-1');R=np.asarray(b['frame_to_global']);omega=R.T@b['angular_velocity_global_rad_s'];alpha=np.asarray(b['angular_acceleration_body_rad_s2']);a=np.asarray(b['acceleration_body_m_s2'])+np.cross(alpha,offset)+np.cross(omega,np.cross(omega,offset));F=mass*(a+R.T@np.array([0.,0.,9.81]));moment=I@alpha+np.cross(omega,I@omega)+np.cross(Q@cg,F);screen=joints.assess(group,np.r_[Q.T@F,Q.T@moment]);count+=1
                if peak is None or screen['peak_tension_n']+screen['peak_shear_n']>peak['screen']['peak_tension_n']+peak['screen']['peak_shear_n']:peak=dict(time_s=h['time_s'],screen=screen)
        write(output/'battery-mount-pilot.json',dict(configuration_sha256=cfg,group=group,peak_simultaneous_sample=peak,history_sha256=sha(history),sample_count=count,body_reference_cg_m=body_cg.tolist(),load_case_sha256=fingerprint(entry['load_case']),equipment_offset_from_loaded_body_cg_m=offset.tolist(),force_convention='required support on pack; positive vertical treated as conservative tension screen; actual bearing/member load share open',compliance_inserted_into_full_train=False,physical_validation=False))
    if sources()!=frozen_sources:raise ValueError('integration sources changed during execution; retained outputs are unqualified')
    inputs=[*sorted(package.glob('*.json'))]
    if service:inputs += [service/'dynamics.json',service/'history.jsonl.gz',service/'coverage.json',service/'configuration.json',service.parent/'receipt.json']
    outputs={p.relative_to(output).as_posix():sha(p) for p in sorted(output.rglob('*')) if p.is_file()}
    write(output/'receipt.json',dict(schema='osr-integration-programme-execution/1',configuration_sha256=cfg,source_sha256=frozen_sources,
        inputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in inputs},outputs_sha256=outputs,physical_validation=False,production_released=False))
    print(json.dumps(dict(configuration_sha256=cfg,native_controller_fault_isolated=result['fault_isolated'],shell_native_exit_code=proc.returncode,physical_validation=False)))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['run','verify']);p.add_argument('--output',type=Path,required=True);p.add_argument('--package',type=Path);p.add_argument('--service',type=Path);a=p.parse_args()
    output=a.output.resolve()
    if a.command=='run':
        if not a.package:p.error('run requires actual compiled --package')
        run(output,a.package.resolve(),a.service.resolve() if a.service else None)
    else:
        r=load_definition(output/'receipt.json')
        if r['source_sha256']!=sources():raise ValueError('integration implementation or inputs changed')
        for name,digest in r['inputs_sha256'].items():
            target=(ROOT/name).resolve()
            if not target.is_relative_to(ROOT) or sha(target)!=digest:raise ValueError('integration upstream evidence changed: '+name)
        for name,digest in r['outputs_sha256'].items():
            target=(output/name).resolve()
            if not target.is_relative_to(output) or sha(target)!=digest:raise ValueError('integration evidence changed: '+name)
        print(json.dumps(dict(verified=True,physical_validation=False)))


if __name__=='__main__':main()
