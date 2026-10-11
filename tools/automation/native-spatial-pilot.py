#!/usr/bin/env python3
"""Retain native Rust/mechanical/electrical/thermal coupling for the compiled twin."""
import argparse,gzip,hashlib,json,os,subprocess,sys
from pathlib import Path
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from osr_mech.engineering_definition import fingerprint,load_definition
from engineering.civil_exploration.spatial_vehicle import run_spatial
from engineering.integration_programme.native_spatial import NativeSpatialLoop
from engineering.integration_programme.joints import battery_mount
import numpy as np


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2,allow_nan=False)+'\n')
def sources():
    files=[*sorted((ROOT/'engineering/civil_exploration').rglob('*.py')),*sorted((ROOT/'engineering/integration_programme').rglob('*.py')),
           *sorted((ROOT/'design/component-catalogue/src/osr_mech').rglob('*.py')),ROOT/'crates/osr-sim/examples/twin_controller_bridge.rs',ROOT/'engineering/integration_programme/data/controller-input.json',ROOT/'Cargo.lock',Path(__file__)]
    files += sorted((ROOT/'crates').rglob('*.rs'))+sorted((ROOT/'crates').rglob('Cargo.toml'))+[ROOT/'Cargo.toml']
    return {p.relative_to(ROOT).as_posix():sha(p) for p in files}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['run','verify']);p.add_argument('--output',type=Path,required=True);p.add_argument('--package',type=Path);p.add_argument('--maps',type=Path);p.add_argument('--binary',type=Path,default=ROOT/'target/debug/examples/twin_controller_bridge');p.add_argument('--duration',type=float,default=.1);p.add_argument('--dt',type=float,default=.005);p.add_argument('--fault-after',type=float,default=.05);a=p.parse_args();folder=a.output.resolve();frozen=sources()
    if a.command=='verify':
        receipt=load_definition(folder/'receipt.json')
        if receipt['source_sha256']!=frozen:raise ValueError('native spatial implementation changed')
        if sha(a.binary)!=receipt['binary_sha256']:raise ValueError('native spatial executable changed')
        for collection in ('input_sha256','output_sha256'):
            for name,digest in receipt[collection].items():
                base=ROOT if collection=='input_sha256' else folder;target=(base/name).resolve()
                if not target.is_relative_to(base) or sha(target)!=digest:raise ValueError('native spatial evidence changed: '+name)
        print(json.dumps(dict(verified=True,physical_validation=False)));return
    if not a.package or not a.maps:p.error('run requires a compiled --package and explicit --maps')
    if folder.exists():raise ValueError('retain prior evidence; use a fresh output directory')
    if not .01<=a.duration<=1. or not 0<a.fault_after<a.duration or not 1e-4<=a.dt<=.01 or a.duration/a.dt>10000:raise ValueError('research coupling duration/fault budget invalid')
    subprocess.run([sys.executable,str(ROOT/'tools/automation/design-best-practice-twin.py'),'verify','--output',str(a.package)],check=True)
    if a.binary.resolve()==(ROOT/'target/debug/examples/twin_controller_bridge').resolve():
        subprocess.run(['cargo','build','-p','osr-sim','--example','twin_controller_bridge','--quiet'],cwd=ROOT,check=True)
    binary_sha256=sha(a.binary)
    model=load_definition(a.package/'model.json');pack=load_definition(a.package/'battery.json');cfg=load_definition(a.package/'spatial_configuration.json');maps=load_definition(a.maps);request=load_definition(ROOT/'engineering/integration_programme/data/controller-input.json')
    group=battery_mount(pack,dict(diameter_m=.012,grip_m=.018,youngs_pa=210e9))
    cfg['equipment_mounts']={car['id']+'/battery':dict(stiffness_si=group['stiffness_si'],damping_si=np.zeros((6,6)).tolist(),motion_bounds_si=[[-.01,.01]]*6,basis='engaged elastic shanks at actual battery datum; preload/fit/member/thread/capacity/fatigue open') for car in model['family_definition']['cars']}
    cfg['flexible_vehicle']=dict(ei_nm2=3e8,mode_count=2,damping_ratio=.02)
    cfg['actuator_contract']=dict(kind='native Rust software-in-loop',reference_translation_bound_m=.2,drive_torque_nm=100.,fault_after_s=a.fault_after,
        coupling='previous converged numerical state to native controller; torque to monolithic mechanics; converged wheel work to battery/thermal plant; next-step feedback',physical_validation=False)
    folder.mkdir(parents=True);write(folder/'configuration.json',cfg);write(folder/'mount.json',group);write(folder/'battery-maps.json',maps)
    loop=NativeSpatialLoop(model,pack,maps,request,a.binary,fault_after_s=a.fault_after)
    try:
        result=run_spatial(model,cfg,dt=a.dt,duration_s=a.duration,deck_mesh=2,rail_step=2.,actuator_callback=loop.prepare,sample_callback=loop.observe)
        raw=gzip.compress(json.dumps(result.pop('history'),sort_keys=True,allow_nan=False).encode(),mtime=0);(folder/'mechanical-history.json.gz').write_bytes(raw)
        write(folder/'dynamics.json',result);write(folder/'controller-plant-history.json',loop.history)
        isolated=all(c['native_output']['bms']['contactor']!='Closed' for h in loop.history if h['time_s']>=a.fault_after for c in h['cars'])
        energy=max(abs(c['battery']['electrical_residual_j']) for h in loop.history for c in h['cars'])
        if not isolated or energy>1e-6:raise ValueError('native coupling protection/energy checks failed')
        review=dict(schema='osr-native-spatial-pilot/1',configuration_sha256=fingerprint(model),analysis_configuration_sha256=fingerprint(cfg),
            steps=result['steps'],car_count=len(loop.controllers),dt_s=a.dt,duration_s=a.duration,fault_after_s=a.fault_after,binary_sha256=loop.binary_sha256,
            full_sparse_structure_solved=True,vehicle_modal_reduction_used=True,finite_battery_mounts_solved=True,native_controller_actuation_executed=True,
            fault_isolated=isolated,maximum_electrical_energy_residual_j=energy,complete_passage_qualified=False,physical_validation=False,production_released=False,
            open_domains=['short prescribed-transport perturbation experiment','temporal/mesh/controller-step convergence','physical shell/bogie modal correlation','actual contact/adhesion/drive maps','cell/fluid/refrigerant spatial resolution','target I/O timing and physical calibration'])
        write(folder/'review.json',review)
    finally:loop.close()
    if sources()!=frozen or sha(a.binary)!=binary_sha256:raise ValueError('native coupling source or binary changed during execution')
    inputs=[a.package/'model.json',a.package/'battery.json',a.package/'spatial_configuration.json',a.package/'receipt.json']
    outputs={q.relative_to(folder).as_posix():sha(q) for q in sorted(folder.iterdir()) if q.is_file()}
    write(folder/'receipt.json',dict(schema='osr-native-spatial-execution/1',source_sha256=frozen,binary_sha256=binary_sha256,input_sha256={q.resolve().relative_to(ROOT).as_posix():sha(q) for q in inputs},output_sha256=outputs,physical_validation=False))
    print(json.dumps(review))


if __name__=='__main__':main()
