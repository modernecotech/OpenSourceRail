#!/usr/bin/env python3
"""Publish a compact review from verified spatial and engineering campaigns."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[2]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('spatial','search','joint-coarse','joint-fine','correlation','native','output'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--plot',type=Path);a=p.parse_args()
    api=runpy.run_path(str(ROOT/'tools/automation/shared-engineering-campaign.py'))
    sources=api['sources'](api['common_api']());environment=api['common_api']()['solver_environment']()
    bindings={}
    for label,folder in [('spatial',a.spatial),('search',a.search),('joint-coarse',a.joint_coarse),('joint-fine',a.joint_fine),('correlation',a.correlation)]:
        receipt=json.loads((folder/'receipt.json').read_text())
        if receipt['sources_sha256']!=sources or receipt['solver_environment']!=environment:raise ValueError('campaign implementation/environment changed: '+label)
        for relative,digest in receipt['outputs_sha256'].items():
            path=(folder/relative).resolve()
            if not path.is_relative_to(folder.resolve()) or not path.is_file() or sha(path)!=digest:raise ValueError('changed campaign output: '+label+'/'+relative)
        bindings[label]=dict(receipt_sha256=sha(folder/'receipt.json'),output_count=len(receipt['outputs_sha256']))
    summary=json.loads((a.spatial/'summary.json').read_text());search=json.loads((a.search/'search.json').read_text())
    correlation=json.loads((a.correlation/'correlation.json').read_text());native=json.loads(a.native.read_text())
    model=api['load_definition'](a.spatial/'definition.json');identity=api['fingerprint'](model)
    if native['configuration_sha256']!=identity or search['hardware_definition_sha256']!=identity or correlation['hardware_definition_sha256']!=identity:
        raise ValueError('review campaigns do not describe the same frozen hardware configuration')
    for path,digest in native['sources_sha256'].items():
        if sha(ROOT/path)!=digest:raise ValueError('native assembly source changed')
    if sha(a.native.with_name(a.native.name.replace('.native.json','.FCStd')))!=native['fcstd_sha256']:raise ValueError('native assembly geometry changed')
    for path,digest in correlation['evidence_sha256'].items():
        if sha(ROOT/path)!=digest:raise ValueError('correlation evidence changed')
    joints=[json.loads((folder/'summary.json').read_text()) for folder in (a.joint_coarse,a.joint_fine)]
    if any(r['load_case']['hardware_definition_sha256']!=identity for r in joints):raise ValueError('local joint load belongs to another hardware definition')
    changes={key:abs(joints[-1][key]-joints[0][key])/max(abs(joints[-1][key]),1e-12)
        for key in ('maximum_displacement_m','shank_volume_weighted_rms_von_mises_pa')}
    report=dict(schema='osr-shared-spatial-engineering-review/1',scope='synthetic articulated car pair and three-span two-track numerical research; startup transients included',
        sources_sha256=sources,solver_environment=environment,campaign_bindings=bindings,
        publication_source_sha256=sha(__file__),spatial=summary,
        mixed_search=dict(budgets=search['budgets'],methods=search['methods'],comparison_scope=search['comparison_scope'],
            unique_candidates=len(search['candidates']),
            beam_families=sorted({r['choice']['beam'] for r in search['candidates']}),
            pier_families=sorted({r['choice']['pier'] for r in search['candidates']}),
            connection_schemes=sorted({r['choice']['connection_scheme'] for r in search['candidates']}),
            detailed_finalists=[r['candidate_id'] for r in search['finalist_confirmations']],
            qualified_feasible_pareto_set=[],open_gates=search['open_gates']),
        native_assembly=dict(receipt_sha256=sha(a.native),configuration_sha256=native['configuration_sha256'],
            nominal_datums_reconciled=native['nominal_datums_reconciled'],drawing_visible_edges=native['drawing_visible_edges'],drawing_issued=False),
        joint_mesh_refinement=dict(levels=[{k:v for k,v in r.items() if k!='outputs_sha256'} for r in joints],
            relative_changes=changes,numerical_screen_passed=max(changes.values())<=.05 and all(r['numerical_equilibrium_passed'] for r in joints),
            singular_peak_is_not_strength_acceptance=True),
        synthetic_correlation=correlation,physical_validation=False,engineering_released=False,
        open_gates=['released supplier/manufacturing geometry and properties','adopted standards and project acceptance limits',
                    'complete operating/erection envelope and local resistance', 'actual calibration/independent physical holdout',
                    'independent authority acceptance'])
    if a.plot:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        cases=summary['cases'];fig,axes=plt.subplots(1,3,figsize=(12,4),layout='constrained')
        labels=[r['case'].replace('-','\n') for r in cases]
        for ax,(key,scale,title) in zip(axes,[('peak_contact_n',.001,'Peak wheel contact (kN)'),
            ('peak_carbody_acceleration_m_s2',1.,'Peak carbody acceleration (m/s²)'),('unloading',1.,'Peak wheel unloading fraction')]):
            ax.bar(range(len(cases)),[r[key]*scale for r in cases],color=['#4d708e','#cf934f','#638b75','#8c749e'])
            ax.set_xticks(range(len(cases)),labels,fontsize=8);ax.set_title(title,fontsize=10);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
        fig.suptitle('Spatial shared train / viaduct research — short startup cases\nSynthetic inputs; physical and project acceptance remain open',fontsize=12)
        a.plot.parent.mkdir(parents=True,exist_ok=True);fig.savefig(a.plot,dpi=180);plt.close(fig);report['figure_sha256']=sha(a.plot)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps(dict(published=str(a.output),temporal_screen=summary['temporal_refinement']['passed'],
        spatial_screen=summary['spatial_refinement']['passed'],joint_mesh_screen=report['joint_mesh_refinement']['numerical_screen_passed'],engineering_released=False)))


if __name__=='__main__':main()
