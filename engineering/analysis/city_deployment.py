#!/usr/bin/env python3
"""Derive actionable deployment gaps from current city evidence, not file counts."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import tomllib

ROOT=Path(__file__).resolve().parents[2]


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def generate(city_dir):
    design=tomllib.loads((city_dir/'design.toml').read_text())
    engineering=city_dir/'engineering'; sources={}; reports={}
    def read(relative):
        path=engineering/relative
        if not path.is_file(): return {}
        sources[relative]=sha(path)
        value=json.loads(path.read_text());reports[relative]=value
        return value
    gaps=[]
    def gate(identifier,closed,owner,action,evidence,detail=None):
        gaps.append(dict(id=identifier,status='closed' if closed else 'open',owner_role=owner,closure_action=action,evidence=evidence,detail=detail))
    ground_release=read('survey/drainage-ground-readiness.json')
    accepted_ground=ground_release.get('authority_accepted') is True
    soil=read('soil/summary.json')
    gate('soil-desktop-inputs',(soil.get('desktop_screen_generated') is True or accepted_ground),'civil/geotechnical designer','Sample current station and civil geometry from the pinned soilDB source and retain means, uncertainty and nodata.','soil/summary.json')
    gate('soil-coverage',((bool(soil) and soil.get('missing_profile_count')==0) or accepted_ground),'geotechnical investigator','Fill mapped coverage gaps through local records and targeted sampling; keep estimated and measured records distinct.','soil/civil-investigation-plan.json',{'missing_profiles':soil.get('missing_profile_count')})
    for stem, owner, action in (
        ('control-processing','survey team','Receive survey control observations; process and check the project CRS, datum and residuals.'),
        ('ground-model','survey team','Receive and inspect the terrain, point cloud and ground-model deliveries against independent control.'),
        ('surveyed-alignment','alignment designer','Replace or confirm generated geometry with checked survey alignment and platform reconciliation.'),
        ('route-station-fit','civil/station designer','Resolve utilities, land/access, flood levels, station access and construction staging against the current route.'),
        ('drainage-ground','civil/geotechnical designer','Use the soil investigation plan to collect local geotechnics and groundwater, size foundations/treatment, and check drainage with local rainfall and surveyed levels.'),
        ('structural-release','structural designer and checker','Complete route-specific support/span, foundation, movement and erection calculations and close checking comments.'),
    ):
        r=read('survey/'+stem+'-readiness.json')
        gate(stem,r.get('authority_accepted') is True,owner,action,'survey/'+stem+'-readiness.json',{'report_status':r.get('status'),'missing_technical_roles':r.get('missing_technical_roles',[])})
    operations=read('simulation/operations-crosscheck.json')
    gate('model-timing-comparison',operations.get('automatic_crosscheck_passed') is True,'simulation engineer','Reconcile current native reference journey times with SUMO using the same scenario dwells and route.','simulation/operations-crosscheck.json',{'failed_lines':[r['line_id'] for r in operations.get('line_comparisons',[]) if not r['passed']]})
    gate('full-service-validation',operations.get('full_service_evidence_passed') is True,'simulation engineer','Run current nominal and degraded full-service cases against the current scenario and simulator; retain failures and exact provenance.','simulation/validation-summary.json')
    gate('operating-release',operations.get('authority_accepted') is True,'operator','Complete conflict-aware capacity and degraded-operation review and sign the bound operating evidence.','simulation/operations-crosscheck.json')
    stabling=read('stabling/summary.json'); allocation=stabling.get('hybrid_allocation',{})
    gate('morning-fleet-allocation',allocation.get('allocation_passed') is True,'service planner','Reconcile revenue fleet with required morning departures on each line; retain two station berths and same-line overflow storage.','stabling/summary.json',{'missing_morning_directions':allocation.get('missing_morning_directions',[]),'station_trainsets':allocation.get('station_trainsets'),'depot_trainsets':allocation.get('depot_trainsets')})
    hybrid=read('stabling/hybrid-cycle-screen.json')
    gate('continuous-stabling-replay',hybrid.get('passed') is True,'simulation engineer','Run the selected line-local station/depot candidate across consecutive evenings and synchronised morning starts.','stabling/hybrid-cycle-screen.json')
    gate('stabling-physical-fit',stabling.get('deployment_release_ready') is True,'track/station designer','Locate usable station and line-local depot tracks, shared charging, isolation, inspection access and protected morning release slots.','stabling/summary.json',{'open_gates':stabling.get('open_gates',[])})
    energy=read('energy/summary.json')
    simulation=read('simulation/validation-summary.json')
    full=max(simulation.get('runs',[]),key=lambda r:r.get('duration_s',0),default={})
    gate('solar-storage-endurance',energy.get('operating_energy_validated') is True,'energy designer','Bind declared station/ROW/dedicated PV to site storage and actual charging duty, reconcile conversion losses and prove replenishment across adverse weather; specify residual backup duty explicitly.','energy/summary.json',{'snapshot_passed':energy.get('passed'),'retained_run_duration_s':full.get('duration_s'),'retained_run_pv_generated_kwh':full.get('trackside_pv_generated_kwh'),'retained_run_grid_imported_kwh':full.get('trackside_grid_imported_kwh'),'retained_run_delivered_kwh':full.get('trackside_energy_delivered_kwh'),'interpretation':'Retained-run diagnostics are not a new grid requirement or proof of solar/storage endurance.'})
    depot=read('depot-scope/summary.json')
    gate('depot-placement-and-budget',depot.get('deployment_release_ready') is True,'depot and cost designer','Place the declared PV/storage inventory within the controlled site layout and reconcile itemised installed costs and renewal scope with existing allowances.','depot-scope/summary.json',{'open_gates':depot.get('open_gates',[])})
    report=dict(schema_version=1,city=design['city']['slug'],scope='city civil and operating deployment evidence; manufacturing and system certification remain in their own release registers',design_sha256=sha(city_dir/'design.toml'),generator_sha256=sha(__file__),evidence_sha256=sources,gates=gaps,open_gate_count=sum(g['status']=='open' for g in gaps),closed_gate_count=sum(g['status']=='closed' for g in gaps),deployment_release_ready=all(g['status']=='closed' for g in gaps))
    output=engineering/'deployment';output.mkdir(parents=True,exist_ok=True)
    (output/'summary.json').write_text(json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    lines=[f"# {city_dir.name} deployment gaps",'',f"{report['closed_gate_count']} closed checks; {report['open_gate_count']} open gates. Status follows the linked evidence; generating a receipt template does not count as receiving field data.",'','[Soil inputs](../soil/README.md) include a route/station investigation plan.','', '| Gate | Status | Responsible function | Closure work |','|---|---|---|---|']
    for g in gaps:
        target=engineering/g['evidence']; label=f"[{g['id']}](../{g['evidence']})" if target.exists() else g['id']+' (evidence missing)'
        lines.append(f"| {label} | {g['status']} | {g['owner_role']} | {g['closure_action']} |")
    lines.extend(['',report['scope']+'.',''])
    (output/'README.md').write_text('\n'.join(lines))
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--design',type=Path);p.add_argument('--all',action='store_true');a=p.parse_args()
    if a.all==bool(a.design):p.error('choose --all or --design')
    designs=sorted((ROOT/'cities/catalogue').glob('*/*/*/design.toml')) if a.all else [a.design.resolve()]
    reports=[generate(d.parent) for d in designs]
    if a.all:
        counts=Counter(g['id'] for r in reports for g in r['gates'] if g['status']=='open')
        out=ROOT/'engineering/analysis/deployment-summary.json'
        out.write_text(json.dumps(dict(city_count=len(reports),open_gates_by_city_count=dict(sorted(counts.items())),cities=[dict(city=r['city'],open_gate_count=r['open_gate_count'],closed_gate_count=r['closed_gate_count']) for r in reports]),indent=2,sort_keys=True)+'\n')
        rows=['# Catalogue deployment evidence', '',
              'City registers distinguish completed screening and data work from field investigation, physical design and operating release. Soil means and uncertainty are planning inputs.', '',
              '| City | Soil complete / sampled locations | Open deployment gates | Soil inputs | Deployment work |',
              '|---|---:|---:|---|---|']
        for design_path, report in zip(designs, reports):
            city_dir=design_path.parent
            soil_path=city_dir/'engineering/soil/summary.json'
            soil=json.loads(soil_path.read_text()) if soil_path.exists() else {}
            prefix='../../'+city_dir.relative_to(ROOT).as_posix().replace(' ', '%20')+'/engineering'
            rows.append(f"| {report['city']} | {soil.get('complete_profile_count', 0)} / {soil.get('sample_count', 0)} | {report['open_gate_count']} | [soil]({prefix}/soil/README.md) | [register]({prefix}/deployment/README.md) |")
        (ROOT/'engineering/analysis/deployment-summary.md').write_text('\n'.join(rows)+'\n')
    print(f'{len(reports)} deployment registers generated')
    return 0


if __name__=='__main__':raise SystemExit(main())
