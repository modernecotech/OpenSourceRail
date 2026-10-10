#!/usr/bin/env python3
"""Run, fingerprint and refine the shared car-pair/viaduct research demonstration."""
from __future__ import annotations
import argparse
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import sys
import os
import platform
import importlib.metadata
for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):
    os.environ[key]='1'

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from osr_mech.engineering_definition import fingerprint, model_mass_properties, verification_register, engineering_identity, load_definition, validate
from osr_mech.provenance import deterministic_gzip
from engineering.civil_exploration.shared_demo import demonstration, variants
from engineering.civil_exploration.train_bridge import run, native_deck_benchmark
from engineering.civil_exploration.commercial import bill


def source_hashes():
    paths=[*(ROOT/'engineering/civil_exploration').glob('*.py'),
        *(ROOT/'design/component-catalogue/src/osr_mech/civil').glob('*.py'),
        *(ROOT/'design/component-catalogue/src/osr_mech').glob('*.py'),
        ROOT/'design/component-catalogue/src/osr_mech/vehicle_mass_properties.py',ROOT/'lib/templates/rolling-stock.toml',Path(__file__),
        ROOT/'design/component-catalogue/schemas/shared-engineering-model.json',
        ROOT/'engineering/civil_exploration/config/reference.json']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def solver_environment():
    import scipy.linalg._flapack as lapack
    import scipy.sparse.linalg._dsolve._superlu as superlu
    import numpy._core._multiarray_umath as numpy_native
    import openseespy.opensees
    opensees_native=next((sys.modules[name] for name in ('openseespylinux.opensees','openseespymac.opensees','openseespywin.opensees') if name in sys.modules),None)
    if opensees_native is None:raise RuntimeError('cannot fingerprint the active native OpenSees module')
    native={name:hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
            for name,module in [('scipy-lapack',lapack),('scipy-superlu',superlu),('numpy-core',numpy_native),('opensees',opensees_native)]}
    return dict(python=platform.python_version(),libraries={name:importlib.metadata.version(name) for name in ('numpy','scipy','openseespy')},
                native_library_sha256=native,thread_limits={k:os.environ[k] for k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS')})


def publish(output, value):
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'build/engineering/shared-train-viaduct')
    parser.add_argument('--model',type=Path,help='a filled shared engineering definition; otherwise explicitly synthetic demo')
    parser.add_argument('--family',default='metro-6car')
    parser.add_argument('--speeds',default='15,20,25',help='comma-separated operating/resonance screen speeds in m/s')
    parser.add_argument('--dt',type=float,default=.0025);parser.add_argument('--mesh',type=int,default=8)
    parser.add_argument('--baseline-only',action='store_true');parser.add_argument('--no-refinement',action='store_true')
    parser.add_argument('--verify',type=Path,help='verify a retained demonstration against current inputs and source')
    args=parser.parse_args();sources=source_hashes();environment=solver_environment()
    if args.verify:
        receipt=json.loads((args.verify/'receipt.json').read_text())
        if receipt['sources_sha256']!=sources:raise ValueError('shared demonstration implementation/source changed')
        if receipt['solver_environment']!=environment:raise ValueError('shared demonstration numerical environment changed')
        for name,digest in receipt['outputs_sha256'].items():
            p=(args.verify/name).resolve()
            if not p.is_relative_to(args.verify.resolve()) or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('shared demonstration output changed: '+name)
        for path in args.verify.glob('*/definition.json'):validate(load_definition(path))
        print('Shared engineering source and retained output hashes pass');return 0
    if args.output.exists():raise ValueError('use a fresh output directory; retained evidence is immutable')
    speeds=[float(v) for v in args.speeds.split(',')]
    if not 1<=len(speeds)<=81:raise ValueError('speed campaign budget is 1..81 evaluations per case')
    model=load_definition(args.model) if args.model else demonstration(args.family)
    base_register=verification_register(model,implementation_hashes=sources)
    cases={'baseline':model}
    if not args.baseline_only:
        if args.model:raise ValueError('controlled synthetic variants only apply to the supplied demonstration')
        cases.update(variants(model))
    # Validate all cases before creating any outputs.
    masses={name:model_mass_properties(case) for name,case in cases.items()}
    benchmark=native_deck_benchmark(model['bridge'],args.mesh)
    publish(args.output/'native-deck-benchmark.json',benchmark)
    reports=[]
    for name,case in cases.items():
        folder=args.output/name
        publish(folder/'definition.json',case);publish(folder/'mass-properties.json',masses[name])
        publish(folder/'erp-engineering-identity.json',engineering_identity(case))
        register=verification_register(case,base_register,implementation_hashes=sources);publish(folder/'verification-register.json',register)
        bridge=case['bridge'];study=deepcopy(bridge['study']);study['route_length_m']=bridge['span_count']*bridge['candidate']['definition']['deck']['span_m']
        # Existing equal-scope civil takeoff remains a double-track bill.
        cost=dict(vehicle_mass_kg=masses[name]['total_mass_kg'],vehicle_component_counts={p['id']:p['quantity'] for p in case['instances']},
                  double_track_civil_bill=bill(bridge['candidate'],study),rate_quote_sources=[],installed_cost_usd=None,engineering_released=False)
        publish(folder/'cost-scope.json',cost)
        for speed in speeds:
            result=run(case,speed=speed,dt=args.dt,mesh=args.mesh)
            history=result.pop('history');filename=f'speed-{speed:g}'
            (folder/(filename+'.history.json.gz')).write_bytes(deterministic_gzip(json.dumps(history,allow_nan=False).encode()))
            publish(folder/(filename+'.json'),result);reports.append(dict(case=name,**result))
            print(f'{name} {speed:g} m/s: rail {result["peak_rail_displacement_m"]:.6g} m; contact domain {result["within_adapter_domain"]}',flush=True)
    convergence=[]
    if not args.no_refinement:
        for speed in speeds:
            base=next(r for r in reports if r['case']=='baseline' and r['speed_m_s']==speed)
            # Separate temporal and spatial refinements avoid cancelling errors.
            for axis,dt,mesh in [('timestep',args.dt/2,args.mesh),('mesh',args.dt,args.mesh*2)]:
                refined=run(model,speed=speed,dt=dt,mesh=mesh);history=refined.pop('history')
                (args.output/'baseline'/f'speed-{speed:g}-{axis}.history.json.gz').write_bytes(deterministic_gzip(json.dumps(history,allow_nan=False).encode()))
                publish(args.output/'baseline'/f'speed-{speed:g}-{axis}.json',refined)
                errors={key:abs(refined[key]-base[key])/max(abs(refined[key]),1e-12) for key in ['peak_rail_displacement_m','peak_deck_acceleration_m_s2','peak_bearing_force_n','maximum_contact_n']}
                convergence.append(dict(axis=axis,speed_m_s=speed,relative_errors=errors,numerical_screen_passed=max(errors.values())<=.05))
    publish(args.output/'comparison.json',dict(schema='osr-shared-engineering-demonstration/1',cases=reports,convergence=convergence,
        sources_sha256=sources,solver_environment=environment,physical_validation=False,engineering_released=False,
        next_stages=['released powered-bogie/underframe/articulation drawings and physical joint properties','3D curved-track railway contact adapter benchmarks',
                     'candidate material/connection nonlinear capacity and robust optimisation','instrumented prototype calibration and independent holdout correlation']))
    if source_hashes()!=sources:raise ValueError('source changed during shared demonstration')
    for case in cases.values():validate(case)
    outputs={str(p.relative_to(args.output)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(args.output.rglob('*')) if p.is_file()}
    publish(args.output/'receipt.json',dict(schema='osr-shared-engineering-receipt/1',sources_sha256=sources,solver_environment=environment,outputs_sha256=outputs))
    print(f'Retained {len(reports)} runs and {len(convergence)} convergence checks in {args.output}')
    return 0 if benchmark['numerical_benchmark_passed'] and all(r['within_adapter_domain'] for r in reports) and all(r['numerical_screen_passed'] for r in convergence) else 2


if __name__=='__main__':raise SystemExit(main())
