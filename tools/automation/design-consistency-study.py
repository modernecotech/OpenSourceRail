#!/usr/bin/env python3
"""Generate linked research demonstrators; verify source/representation consistency."""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from engineering.design_consistency import demonstrators as d
from engineering.design_consistency.contracts import summary
from engineering.design_consistency.analysis import bolt_screen,interface_modes,civil_stages
from osr_mech.engineering_definition import fingerprint
DEFAULT=ROOT/'engineering/design_consistency/examples'


def encode(value):return (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
def sources():
    paths=sorted((ROOT/'engineering/design_consistency').glob('*.py'))+[Path(__file__),ROOT/'tools/automation/verify-design-consistency-cad.py',ROOT/'engineering/composite_panels/config/development.json',ROOT/'engineering/industrialisation/vehicle-civil-load-trace.json']
    paths.extend(ROOT/'design/component-catalogue/src/osr_mech'/p for p in ['automated_geometry.py','section_contract.py','engineering_definition.py','rolling_stock/composite_panels.py'])
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}


def build():
    config=json.loads((ROOT/'engineering/composite_panels/config/development.json').read_text());trace=json.loads((ROOT/'engineering/industrialisation/vehicle-civil-load-trace.json').read_text())
    models=dict(side=d.panel_bay(config),roof=d.panel_bay(config,crown=.05,aperture=False),interface=d.interface(),viaduct=d.viaduct())
    outputs={k+'.json':encode(v)for k,v in models.items()}
    outputs.update({'correspondence.json':encode({k:summary(v)for k,v in models.items()}),'construction-front.json':encode(d.front(models['viaduct'])),
        'interface-joint-screen.json':encode(bolt_screen(models['interface']['assembly_joints'][0])),
        'interface-modes.json':encode(interface_modes(models['interface'])),'civil-stages.json':encode(civil_stages(models['viaduct'],trace))})
    outputs['manifest.json']=encode(dict(schema='osr-design-consistency-package/1',source_sha256=sources(),
        output_sha256={k:hashlib.sha256(v).hexdigest()for k,v in outputs.items()},model_sha256={k:fingerprint(v)for k,v in models.items()},
        production_released=False,physical_validation=False))
    return outputs,models


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=DEFAULT);parser.add_argument('--check',action='store_true');parser.add_argument('--ifc',action='store_true');parser.add_argument('--search',action='store_true');parser.add_argument('--solvers',action='store_true');args=parser.parse_args()
    outputs,models=build()
    if args.check:
        changed=[n for n,b in outputs.items()if not(args.output/n).is_file()or(args.output/n).read_bytes()!=b]
        if changed:raise SystemExit('Stale design-consistency package: '+', '.join(changed))
        # External/native evidence is checked against its own source/output hashes.
        for receipt in ('cad/verification.json','ifc-verification.json','solver/verification.json','mixed-search.json'):
            path=args.output/receipt
            if path.is_file():
                value=json.loads(path.read_text())
                if value['source_sha256']!=sources():raise SystemExit('Stale evidence: '+receipt)
                for relative,digest in value.get('output_sha256',{}).items():
                    if hashlib.sha256((args.output/relative).read_bytes()).hexdigest()!=digest:raise SystemExit('Changed evidence output: '+relative)
        print('Shared definitions and retained evidence are current');return
    args.output.mkdir(parents=True,exist_ok=True)
    for n,b in outputs.items():(args.output/n).write_bytes(b)
    if args.ifc:
        from engineering.design_consistency.ifc import export
        report=export(models['viaduct'],args.output/'viaduct.ifc');report.update(source_sha256=sources(),output_sha256={'viaduct.ifc':hashlib.sha256((args.output/'viaduct.ifc').read_bytes()).hexdigest()})
        (args.output/'ifc-verification.json').write_bytes(encode(report))
    if args.search:
        from engineering.design_consistency.search import run
        report=run(json.loads((ROOT/'engineering/composite_panels/config/development.json').read_text()));report['source_sha256']=sources()
        (args.output/'mixed-search.json').write_bytes(encode(report))
    if args.solvers:
        from engineering.design_consistency.solver import section_benchmark
        coarse=section_benchmark(args.output/'solver/coarse',mesh_size=.06);fine=section_benchmark(args.output/'solver/refined',mesh_size=.04)
        error=abs(coarse['solid']['mean_tip_uz_m']/fine['solid']['mean_tip_uz_m']-1)
        paths=sorted((args.output/'solver').glob('*/*'))
        report=dict(schema='osr-design-consistency-solver-receipt/1',source_sha256=sources(),output_sha256={p.relative_to(args.output).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in paths if p.suffix in ('.inp','.dat','.log','.json')},refinement_relative_difference=error,
            bending_agreement_screen_passed=coarse['agreement_screen_passed']and fine['agreement_screen_passed']and error<.01,physical_validation=False)
        (args.output/'solver/verification.json').write_bytes(encode(report))
    print('Generated four research demonstrators; physical release remains false')
if __name__=='__main__':main()
