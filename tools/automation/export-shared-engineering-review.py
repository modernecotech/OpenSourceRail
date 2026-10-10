#!/usr/bin/env python3
"""Export compact numerical evidence and a standalone comparison figure."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('campaign',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--native',type=Path,required=True);p.add_argument('--plot',type=Path)
    a=p.parse_args();api=runpy.run_path(str(ROOT/'tools/automation/shared-train-viaduct.py'))
    receipt=json.loads((a.campaign/'receipt.json').read_text())
    if receipt['sources_sha256']!=api['source_hashes']() or receipt['solver_environment']!=api['solver_environment']():
        raise ValueError('shared research inputs or numerical environment changed')
    for name,digest in receipt['outputs_sha256'].items():
        path=(a.campaign/name).resolve()
        if not path.is_relative_to(a.campaign.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError('shared research output changed: '+name)
    report=json.loads((a.campaign/'comparison.json').read_text());native=json.loads(a.native.read_text())
    base=json.loads((a.campaign/'baseline/definition.json').read_text())
    from osr_mech.engineering_definition import fingerprint,validate
    validate(base)
    if native['configuration_sha256']!=fingerprint(base) or not native['nominal_datums_reconciled']:
        raise ValueError('native assembly belongs to another configuration or failed')
    for source,digest in native['sources_sha256'].items():
        if hashlib.sha256((ROOT/source).read_bytes()).hexdigest()!=digest:raise ValueError('native assembly source changed')
    cad=a.native.with_name(a.native.name.replace('.native.json','.FCStd'))
    if hashlib.sha256(cad.read_bytes()).hexdigest()!=native['fcstd_sha256']:raise ValueError('native assembly geometry changed')
    benchmark=json.loads((a.campaign/'native-deck-benchmark.json').read_text())
    passed=(benchmark['numerical_benchmark_passed'] and all(r['within_adapter_domain'] for r in report['cases']) and
            all(r['numerical_screen_passed'] for r in report['convergence']))
    impact={}
    for folder in a.campaign.iterdir():
        path=folder/'verification-register.json'
        if path.is_file():impact[folder.name]=json.loads(path.read_text())['invalidated']
    compact=dict(schema='osr-shared-engineering-review/1',numerical_screens_passed=passed,
        scope='synthetic two-car, single-track vertical coupled benchmark; no production or railway acceptance',
        sources_sha256=receipt['sources_sha256'],solver_environment=receipt['solver_environment'],
        publication_sources_sha256={str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        retained_campaign_receipt_sha256=hashlib.sha256((a.campaign/'receipt.json').read_bytes()).hexdigest(),
        cases=report['cases'],convergence=report['convergence'],native_deck_benchmark=benchmark,
        native_assembly_receipt_path=str(a.native.relative_to(ROOT)) if a.native.is_absolute() else str(a.native),
        native_assembly_receipt_sha256=hashlib.sha256(a.native.read_bytes()).hexdigest(),
        instance_count=native['instance_count'],joint_count=len(native['joints']),
        changed_dependencies=impact,physical_validation=False,engineering_released=False,
        cost_qualified=False,drawing_issued=False,next_stages=report['next_stages'])
    if a.plot:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        speed=20.;rows=[r for r in report['cases'] if r['speed_m_s']==speed]
        labels=[r['case'].replace('-','\n') for r in rows]
        fig,axes=plt.subplots(1,3,figsize=(12,4),layout='constrained')
        metrics=[('peak_rail_displacement_m',1000,'Peak rail displacement (mm)'),
                 ('peak_bearing_force_n',.001,'Peak bearing force (kN)'),
                 ('peak_vehicle_acceleration_m_s2',1,'Peak body acceleration (m/s²)')]
        for ax,(key,factor,title) in zip(axes,metrics):
            ax.bar(range(len(rows)),[r[key]*factor for r in rows],color=['#4d708e','#cf934f','#638b75','#8c749e','#ba6870'])
            ax.set_xticks(range(len(rows)),labels,fontsize=7);ax.set_title(title,fontsize=10);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
        fig.suptitle('Shared car-pair / three-span research model — 20 m/s\nSynthetic inputs; numerical comparison, physical qualification open',fontsize=12)
        a.plot.parent.mkdir(parents=True,exist_ok=True);fig.savefig(a.plot,dpi=180);plt.close(fig)
        compact['figure_sha256']=hashlib.sha256(a.plot.read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(compact,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(f'Exported {len(report["cases"])} runs, {len(report["convergence"])} refinement checks and native assembly evidence; numerical pass={passed}')
    return 0 if passed else 2


if __name__=='__main__':raise SystemExit(main())
