#!/usr/bin/env python3
"""Publish verified full-passage coverage, unweighted ride and separate refinements."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[2]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('coarse','temporal','spatial','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();api=runpy.run_path(str(ROOT/'tools/automation/shared-service-envelope.py'))
    common=runpy.run_path(str(ROOT/'tools/automation/shared-engineering-campaign.py'))
    sources=api['source_hashes'](common);environment=common['common_api']()['solver_environment']()
    reports=[];bindings={}
    for name,folder in [('coarse',a.coarse),('temporal',a.temporal),('spatial',a.spatial)]:
        receipt=json.loads((folder/'receipt.json').read_text())
        if receipt['sources_sha256']!=sources or receipt['solver_environment']!=environment:raise ValueError('service implementation/environment changed')
        for relative,digest in receipt['outputs_sha256'].items():
            path=(folder/relative).resolve()
            if not path.is_relative_to(folder.resolve()) or not path.is_file() or sha(path)!=digest:raise ValueError('changed service output: '+relative)
        reports.append(json.loads((folder/'summary.json').read_text()))
        bindings[name]=dict(receipt_sha256=sha(folder/'receipt.json'),output_count=len(receipt['outputs_sha256']))
    if len({r['hardware_definition_sha256'] for r in reports})!=1:raise ValueError('service refinements use different hardware definitions')
    by_case=[{r['case']:r for r in report['cases']} for report in reports]
    if not by_case[0] or any(set(rows)!=set(by_case[0]) for rows in by_case[1:]):raise ValueError('refinement case coverage differs')
    budgets=[r['budgets'] for r in reports]
    if budgets[0]['deck_mesh']!=budgets[1]['deck_mesh'] or budgets[0]['rail_step_m']!=budgets[1]['rail_step_m'] or budgets[0]['time_step_s']==budgets[1]['time_step_s']:
        raise ValueError('temporal refinement must change time only')
    if budgets[1]['time_step_s']!=budgets[2]['time_step_s'] or (budgets[1]['deck_mesh'],budgets[1]['rail_step_m'])==(budgets[2]['deck_mesh'],budgets[2]['rail_step_m']):
        raise ValueError('spatial refinement must hold time fixed and change mesh')
    from engineering.civil_exploration.constraints import convergence
    metrics=['minimum_contact_n','maximum_contact_n','peak_carbody_acceleration_m_s2']
    cases=[]
    for key in sorted(by_case[0]):
        rows=[r[key] for r in by_case]
        if any(r['status']!='completed' for r in rows):raise ValueError('a failed passage cannot be exported as refinement evidence')
        configs=[json.loads((folder/key/'configuration.json').read_text()) for folder in (a.coarse,a.temporal,a.spatial)]
        if configs[1:]!=[configs[0],configs[0]]:raise ValueError('refinement configuration changed')
        cases.append(dict(case=key,levels=rows,temporal_refinement=convergence(rows[:2],metrics),spatial_refinement=convergence(rows[1:],metrics),
            complete_modelled_passage=all(r['complete_passage'] for r in rows),within_adapter_domain=all(r['within_adapter_domain'] for r in rows),
            physical_validation=False,engineering_released=False))
    fine=reports[-1]
    output=dict(schema='osr-shared-service-review/1',scope='synthetic two-car full passage; nominal linearised contact stations, rigid-CG unweighted ride',
        hardware_definition_sha256=fine['hardware_definition_sha256'],sources_sha256=sources,solver_environment=environment,
        publication_source_sha256=sha(__file__),campaign_bindings=bindings,budgets=budgets,cases=cases,
        unexecuted_case_ids=fine['unexecuted_case_ids'],all_planned_cases_executed=fine['all_planned_cases_executed'],
        numerical_refinement_passed=all(c['temporal_refinement']['passed'] and c['spatial_refinement']['passed'] and c['within_adapter_domain'] and c['complete_modelled_passage'] for c in cases),
        iso_comfort_evaluated=False,physical_validation=False,engineering_released=False,open_gates=fine['open_gates'])
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(output,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps(dict(published=str(a.output),numerical_refinement_passed=output['numerical_refinement_passed'],all_planned_cases_executed=output['all_planned_cases_executed'],engineering_released=False)))


if __name__=='__main__':main()
