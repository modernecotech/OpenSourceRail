#!/usr/bin/env python3
"""City organisation, delivery work and interface refinement from current inputs."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import asdict
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'design/component-catalogue/src'))
sys.path.insert(0, str(ROOT / 'engineering/analysis'))
from osr_mech.civil.continuity import semi_continuous_unit_plan
from detail_checks import thermal_movement_mm


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def allocate(total, roles):
    """Integer FTE preserving the funded total, stable id tie-breaks; fail on minima."""
    if total < 0 or int(total) != total or not roles:
        raise ValueError('invalid workforce total or empty roles')
    minimum = sum(r['minimum_fte'] for r in roles)
    if total < minimum:
        raise ValueError('funded group cannot cover declared function minima')
    weight = sum(r['weight'] for r in roles)
    if weight <= 0 or any(r['weight'] < 0 or r['minimum_fte'] < 0 for r in roles):
        raise ValueError('invalid allocation weights/minima')
    quota = {r['id']: (total-minimum)*r['weight']/weight for r in roles}
    result = {r['id']: r['minimum_fte']+math.floor(quota[r['id']]) for r in roles}
    order = sorted(quota, key=lambda key: (-(quota[key]-math.floor(quota[key])), key))
    for key in order[:total-sum(result.values())]:
        result[key] += 1
    return result


def construction_workload(tasks):
    """Inclusive day ranges; resources are crews/workstations, not assumed people."""
    centers = defaultdict(lambda: dict(events=Counter(), resource_days=0, roles=set(), tasks=set(), missing_resources=0))
    for task in tasks:
        center = centers[task['work_center']]
        start, end = int(task['planned_start_day']), int(task['planned_finish_day'])
        # An unsized task occupies a scheduled work slot, but cannot prove crew capacity.
        missing = task['resource_count'] in ('', None)
        resources = 1 if missing else int(task['resource_count'])
        center['missing_resources'] += int(missing)
        if end < start or resources < 1:
            raise ValueError('invalid manufacturing task interval/resources')
        center['events'][start] += resources
        center['events'][end+1] -= resources
        center['resource_days'] += (end-start+1)*resources
        center['roles'].update(s.strip() for s in task['staff_roles'].split(';') if s.strip())
        center['tasks'].add(task['package_id'])
    result = []
    for name, c in sorted(centers.items()):
        active = peak = peak_day = 0
        for day, change in sorted(c['events'].items()):
            active += change
            if active > peak:
                peak, peak_day = active, day
        result.append(dict(work_center=name, peak_concurrent_resources=None if c['missing_resources'] else peak,
                           peak_concurrent_task_slots=peak, peak_day=peak_day,
                           resource_days=None if c['missing_resources'] else c['resource_days'],
                           tasks_missing_resource_count=c['missing_resources'],
                           required_skills=sorted(c['roles']), package_ids=sorted(c['tasks']),
                           workers_per_resource=None, worker_headcount=None,
                           closure='Confirm named crew mix and measured productivity; resource_count is not a worker count.'))
    return result


def refinement(design, scenario, climate, soil, *, span_m=25.0, unit_spans=4):
    # Ambient sensitivities are intentionally not installed movement allowances.
    reference = float(climate['ambient_c_average'])
    hot = float(climate['ambient_c_design'])
    cold = climate.get('ambient_c_min')
    segments = []
    for i, seg in enumerate(design.get('civil_segments', [])):
        if seg['class'] != 'elevated':
            continue
        length = float(seg['to_station_m'])-float(seg['from_station_m'])
        plan = semi_continuous_unit_plan(length, span_m=span_m, unit_spans=unit_spans)
        longest = min(plan.spans, plan.unit_spans)*plan.span_m
        segments.append(dict(segment_index=i, line=seg['line'], from_chainage_m=seg['from_station_m'],
            to_chainage_m=seg['to_station_m'], plan=asdict(plan), longest_planned_unit_m=longest,
            hot_movement_sensitivity_mm={str(a): round(thermal_movement_mm(longest,a,hot-reference),3) for a in (8,10,12)},
            cold_movement_sensitivity_mm=None if cold is None else {str(a): round(thermal_movement_mm(longest,a,float(cold)-reference),3) for a in (8,10,12)}))
    return dict(climate_preset=design['climate']['preset'], climate_inputs=climate,
        scenario_ambient_c=scenario.get('climate', {}).get('ambient_c'),
        thermal_basis='Free movement alpha*L*deltaT. 8/10/12 microstrain/K are declared sensitivity cases, not measured concrete properties. Reference is the preset annual mean, not installation temperature; sunlit component temperatures and gradients require separate inputs.',
        elevated_segments=segments,
        civil_quantity_basis=f'Each elevated segment is separate; {span_m:g} m catalogue span, up to {unit_spans} spans/unit from the shared production/continuity templates, two tracks and two webs. Rounded spans are a procurement screen, not surveyed support positions. Deck gaps count the existing catalogue unit interfaces; abutment details remain separate.',
        cold_temperature_missing=cold is None,
        soil_investigation_flags=soil['investigation_flag_counts'], missing_soil_profiles=soil['missing_profile_count'],
        soil_use='Prioritise investigation and settlement/drainage monitoring; mapped pH/texture do not determine bearing resistance, pile depth, sulfate/chloride exposure or a coating category.',
        interface_release_inputs={
            'civil_movement':['component temperature extremes and erection temperature','measured concrete CTE/shrinkage/creep','bearing restraint, rail interaction, seismic and foundation movement','surveyed supports and abutment movement details'],
            'fasteners':['joint loads and fatigue spectrum','fastener grade and proof load','actual finish/lubrication torque-tension trial','preload loss, slip/separation, bearing and thread checks'],
            'seals':['supplier qualified compression range and ageing','actual thickness, land gap and tolerances','module thermal mismatch and vibration','water-ingress test after assembly and cleaning'],
            'finishes':['local exposure and substrate preparation qualification','approved product system and batch TDS limits','DFT/adhesion/cure and fire/UV/wash qualification','masking, repair and inspection records'],
            'cleaning':['measured washable area by material, not canopy area','trial person-minutes, water and safe access windows','detergent/nozzle/material compatibility','wash-water collection and local disposal route'],
        })


def generate(city):
    sources = {}
    def read(path, kind='json'):
        # Large operations bundles are local regeneration products in most cities.
        # Their tracked manifest binds the compressed bytes without requiring the
        # bundle itself in a fresh Git checkout's provenance review.
        if kind != 'gzip': sources[path.relative_to(ROOT).as_posix()] = sha(path)
        if kind == 'toml': return tomllib.loads(path.read_text())
        if kind == 'gzip': return json.loads(gzip.decompress(path.read_bytes()))
        return json.loads(path.read_text())
    design = read(city/'design.toml','toml'); slug = design['city']['slug']
    scenario = read(city/f'{slug}.toml','toml')
    template = read(ROOT/'lib/templates/workforce.toml','toml')
    civil_policy = read(ROOT/'lib/templates/civil-construction-systems.toml','toml')
    manufacturing = read(ROOT/'lib/templates/manufacturing-schedule.toml','toml')
    span_m = manufacturing['civil_production']['primary_span_m']
    if span_m not in civil_policy['viaduct']['standard_spans_m']:
        raise ValueError('production span is outside the controlled civil catalogue')
    presets = read(ROOT/'lib/templates/climate.toml','toml')['presets']
    climate = {**presets[design['climate']['preset']], **{k:v for k,v in design['climate'].items() if k!='preset'}}
    finance = read(city/'engineering/finance/summary.json')
    manifest = read(city/'operations'/f'{slug}-operations-manifest.json')
    bundle_path = city/'operations'/f'{slug}-operations.json.gz'
    if manifest['compressed_sha256'] != sha(bundle_path):
        raise ValueError('operations bundle differs from its tracked manifest')
    bundle = read(bundle_path,'gzip')
    soil = read(city/'engineering/soil/summary.json')
    for relative in ('lib/templates/maintenance-schedule.toml','lib/templates/manufacturing-schedule.toml',
                     'tools/automation/generate-qa-maintenance-data.py','tools/automation/project_twin.py',
                     'engineering/analysis/detail_checks.py','design/component-catalogue/src/osr_mech/civil/continuity.py',
                     'design/component-catalogue/catalog/buildable-trainset/exterior-finish-system.json',
                     'design/component-catalogue/catalog/buildable-trainset/joint-control-schedule.json'):
        sources[relative] = sha(ROOT/relative)
    workforce = finance['workforce']; rows = []
    for group, total in sorted(workforce['groups_fte'].items()):
        roles = [r for r in template['role'] if r['group']==group]
        counts = allocate(total, roles)
        rows.extend(dict(**r, fte=counts[r['id']]) for r in roles)
    if sum(r['fte'] for r in rows) != workforce['total_fte']:
        raise ValueError('role FTE must reconcile to finance')
    maintenance = Counter(t['task_id'] for t in bundle['maintenance_tasks'])
    report = dict(schema_version=1, city=slug, status='planning-work-package',
        generator_sha256=sha(__file__), input_sha256=sources,
        organisation=dict(policy=template['policy'], finance_basis=workforce, roles=rows,
            roster_validated=False, training_plan='Recruit and apprentice locally; assess practical task competence, isolate/hold/release authority and refresher needs. Training duration follows the demonstrated skills gap, not a universal weeks-to-qualification claim.',
            open_work=['named duty and leave roster including service-depot turnaround crews','measured cleaning/inspection person-minutes and simultaneous arrivals','country/local pay and actual grade costs','local employment/rest requirements and night emergency cover']),
        construction=construction_workload(bundle['manufacturing_tasks']),
        mechanical_civil=refinement(design,scenario,climate,soil,span_m=span_m,
                                   unit_spans=civil_policy['viaduct']['expansion_unit_spans']),
        maintenance_task_counts=dict(sorted(maintenance.items())),
        design_release_ready=False)
    output = city/'engineering/delivery'; output.mkdir(parents=True,exist_ok=True)
    (output/'summary.json').write_text(json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    with (output/'workforce.csv').open('w') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    detail = report['mechanical_civil']
    lines=[f'# {city.name} organisation and design work', '',
        f"{workforce['total_fte']} indicative operating FTE, including management; annual labour allowance ${workforce['annual_labour_usd']:,.0f}. Group totals reconcile to the existing finance model. Individual role shares are editable planning allocations, not measured workload or an accepted duty roster.", '',
        'GoA 4 control and remote assistance; local station batteries supply train top-ups. Two revenue trainsets per selected station with same-line depot overflow. Shared domestic design/software/factory capability serves city teams.', '',
        '## City operating organisation', '',
        '| Function | FTE | Reports to | Skills | Tasks |','|---|---:|---|---|---|']
    for r in rows: lines.append(f"| {r['title']} | {r['fte']} | {r['reports_to']} | {r['skills']} | {r['tasks']} |")
    lines += ['',report['organisation']['training_plan'],'',
        'Quality and safety staff can escalate holds directly to the local owner board. Functions can be combined where competence and cover permit. Management allocations are already inside the operating totals.', '',
        'Roster closure: '+ '; '.join(report['organisation']['open_work'])+'.','',
        '## Construction and domestic manufacturing work', '',
        'Concurrent crews/workstations below come from the existing dated work orders, with inclusive finish days. Worker headcount awaits an explicit crew mix; named skills are not assumed to mean one person each. Factory capacity is shared across city orders. Peaks from different work centres need not occur together.', '',
        '| Work centre | Peak resources (unknown if unsized) | Peak task slots | First peak day | Resource-days | Skills/tasks |','|---|---:|---:|---:|---:|---|']
    for c in report['construction']:
        lines.append(f"| {c['work_center']} | {c['peak_concurrent_resources'] if c['peak_concurrent_resources'] is not None else 'unknown'} | {c['peak_concurrent_task_slots']} | {c['peak_day']} | {c['resource_days'] if c['resource_days'] is not None else 'unknown'} | {'; '.join(c['required_skills'])} / {', '.join(c['package_ids'])} |")
    lines += ['', '## Civil and mechanical refinements', '',
        f"Climate: {detail['climate_preset']}; {climate['ambient_c_average']} °C reference, {climate['ambient_c_design']} °C upper ambient. Cold ambient: {climate.get('ambient_c_min','missing')}.", '',detail['thermal_basis'],'',detail['civil_quantity_basis'],'',
        '| Elevated segment | Longest unit m | Bearings | Link slabs | Hot movement mm at 8 / 10 / 12 µstrain/K |', '|---|---:|---:|---:|---|']
    for s in detail['elevated_segments']:
        lines.append(f"| {s['line']} {s['from_chainage_m']}–{s['to_chainage_m']} m | {s['longest_planned_unit_m']} | {s['plan']['bearings']} | {s['plan']['link_slabs']} | {' / '.join(str(v) for v in s['hot_movement_sensitivity_mm'].values())} |")
    if not detail['elevated_segments']: lines.append('| No elevated segments in this design | — | — | — | — |')
    lines += ['',f"Mapped soil has {detail['missing_soil_profiles']} incomplete profiles. "+detail['soil_use'], '',
        '[Location-specific soil investigation plan](../soil/README.md). Flag counts: '+json.dumps(detail['soil_investigation_flags'],sort_keys=True)+'.','',
        '## Joints, paints, finishes and cleaning', '',
        'Steel, GFRP body and roof finish zones retain their shared qualified process. Protect electrical bond lands, seals, drains, PV glass and inspection areas. Radiative paint remains a trial option; no unverified cooling benefit enters the energy model.', '',
        '| Work package | Asset-level tasks generated |','|---|---:|']
    for key in ('rs-finish-seal-joint','rs-controlled-wash','civil-joint-drain-finish','energy-soiling-cleaning'):
        lines.append(f'| {key} | {maintenance[key]} |')
    lines += ['', 'The operations bundle carries these inspection/cleaning triggers, owners and required work-order evidence. Cleaning intervals follow measured condition and access; material compatibility and wash-water handling must be qualified locally.', '',
        'Release inputs still required:', '']
    lines += ['- '+key.replace('_',' ')+': '+ '; '.join(value)+'.' for key,value in detail['interface_release_inputs'].items()]
    lines += ['', '[Structured report](summary.json) · [Workforce spreadsheet](workforce.csv) · [Deployment gates](../deployment/README.md)', '']
    (output/'README.md').write_text('\n'.join(lines))
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--design',type=Path);p.add_argument('--all',action='store_true');a=p.parse_args()
    if a.all==bool(a.design): p.error('choose --all or --design')
    paths=sorted((ROOT/'cities/catalogue').glob('*/*/*/design.toml')) if a.all else [a.design.resolve()]
    reports=[generate(path.parent) for path in paths]
    if a.all:
        rows=['# City organisation and design work', '',
              'Generated from current city finance, work orders, climate presets and mapped soil. All figures remain planning quantities pending local workforce and design qualification.', '',
              '| City | Operating FTE | Organisation, skills, tasks and design refinements |','|---|---:|---|']
        for path,report in zip(paths,reports):
            target='../../'+path.parent.relative_to(ROOT).as_posix().replace(' ','%20')+'/engineering/delivery/README.md'
            rows.append(f"| {report['city']} | {report['organisation']['finance_basis']['total_fte']} | [city work package]({target}) |")
        (ROOT/'engineering/analysis/city-delivery-index.md').write_text('\n'.join(rows)+'\n')
    print(f'{len(reports)} city organisation/design work packages generated')


if __name__=='__main__': main()
