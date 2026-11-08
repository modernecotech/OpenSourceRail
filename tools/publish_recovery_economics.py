#!/usr/bin/env python3
"""Publish the frozen recovery run without altering its numerical/source receipts.

The publication tool is deliberately outside the evaluated engineering module:
formatting a later packet must not change the frozen evaluation's source map.
"""
import argparse,gzip,hashlib,io,json,subprocess,sys,tarfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def identity(value):return hashlib.sha256(encoded(value)).hexdigest()
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):
    path=Path(path);raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
def sealed(value,key='evaluation_id'):
    if value[key]!=identity({k:v for k,v in value.items() if k!=key}):raise ValueError('Unsealed '+key)
    return value


def finding(run):
    study=read(run/'study.json');rows=study['rows'];q=read(run/'cases/hydraulic-4MJ-share0.8.json.gz')
    enabled=next(r for r in rows if r['key']=='hydraulic-4MJ-share0.8')
    disabled=next(r for r in rows if r['key']=='hydraulic-4MJ-recovery-disabled')
    cheapest=min((r for r in rows if r['technology'] is not None and r['enabled']),key=lambda r:r['whole_life_NPV_usd_base'])
    events=[e for e in q['result']['events'] if e['station_id']=='A' and e['departure_id'] in ('B-001','A-002')
            and e['kind'] in ('capture-resource-acquired','departure-dispatched','recovery-reset-complete')]
    value=dict(schema='osr-recovery-economics-finding/1',study_id=study['evaluation_id'],
        source_commit=study['source_commit'],native_case_evaluation_id=q['result']['evaluation_id'],
        case_evaluation_id=q['evaluation_id'],body_candidate_id=study['body_candidate_id'],
        common_service='276 normal places, 85% planning occupancy, 4,000 pphpd, H200/phase90, 3 active + 1 reserve, 35 s dwell, 45 s turnback, full-tail terminal quantities, zero nominal grade',
        exact_normal_mass_kg=dict(no_store=rows[0]['normal_mass_kg'],store=enabled['normal_mass_kg']),
        cheapest_tested_store=cheapest['key'],economic_pareto_alternatives=study['pareto_economic_alternatives'],
        matched_hardware_enabled_minus_disabled={k:enabled[k]-disabled[k] for k in
            ('traction_grid_kwh','reset_grid_kwh','annual_grid_kwh_base','whole_life_NPV_usd_base')},
        observed_ownership_events=events,residual_occupancy=q['residual_occupancy'],
        diagnosis='Incoming capture owns station A from about397.5s before its400s departure until arrival+dwell reset at about513.17s; repeating shared-resource timing prevents its release. This is not repaired by capacity/share changes alone.',
        next_experiment_ranking=[
            dict(rank=1,purpose='Numerical experiment only',proposal='Explicit capture-versus-release dispatch priority under the same hardware',
                 required='Model transfer ownership, continuous force handover, lost capture, independent brakes, reset losses and unchanged passenger service. Do not assume preemption is physically available.'),
            dict(rank=2,purpose='New physical alternative only',proposal='Separately controlled capture/release paths or a split bank',
                 required='Add valves/clutches, protection, stock, foundations, cooling, energy losses, mass and renewal costs before comparing.'),
            dict(rank=3,purpose='CAD and measured cost/equipment evidence',proposal='Revisit600kg train interface and fixed station packages',
                 required='A real load path, rated machinery and manufacturable parts must justify any mass or cost reduction; no arbitrary discount.')],
        integrated_selection=None,physical_accepted=False,engineering_accepted=False,
        selected_reference_changed=False,measured_equipment_evidence=False,prices_verified=False)
    value['evaluation_id']=identity(value);return value


def markdown(study,f,usage):
    rows=study['rows'];cheapest=next(r for r in rows if r['key']==f['cheapest_tested_store'])
    delta=f['matched_hardware_enabled_minus_disabled'];occupancy=f['residual_occupancy']
    text=['# Station recovery economics','',
        'The tested no-store powered-wheel research alternative dominates the tested stores on base capital, whole-life NPV and total annual grid energy. This is an economic model result; the selected passive development reference is unchanged.',
        '',f"Frozen source: [`{study['source_commit'][:12]}`](https://github.com/modernecotech/OpenSourceRail/commit/{study['source_commit']}). Study: `{study['evaluation_id']}`.",
        '', 'All 32 nominal model cases complete 16/16 arrivals and the declared model screens. They use eleven physical variants, 276 normal places, 85% planning occupancy, 4,000 pphpd demand, 200 s headway, 90 s opposing phase, 3 active + 1 reserve trains, 35 s dwell, 45 s turnback, full-tail terminal clearance and a 190 s common travel planning bound. The route is 1.5 km, double-track, with two stations/four 125 m boarding faces and zero nominal grade.',
        '', f"The exact normally loaded mass is {f['exact_normal_mass_kg']['no_store']:,.3f} kg without the store interface and {f['exact_normal_mass_kg']['store']:,.3f} kg with it. These retain positive installation reserves and the parent powered-bogie packaging hold; they are not complete admitted installed designs. All candidates retain independent brakes, continuous auxiliary/grid feed, service batteries, backup/maintenance charging, protection and recovery allowances.",
        '', '| Comparison | Traction kWh/16 | Annual total grid MWh | Base capital $m | 30-year base NPV $m |',
        '|---|---:|---:|---:|---:|']
    keys=('no-store','steel-0.25MJ-share0.2','steel-4MJ-share0.8','hydraulic-4MJ-share0.8','hydraulic-4MJ-recovery-disabled')
    for key in keys:
        r=next(r for r in study['rows'] if r['key']==key)
        text.append(f"| {key} | {r['traction_grid_kwh']:.5f} | {r['annual_grid_kwh_base']/1000:.2f} | {r['installed_capital_usd_base']/1e6:.4f} | {r['whole_life_NPV_usd_base']/1e6:.4f} |")
    text+=['', 'Every store retains five capture stages over 250 m and a 200 m release window at each station. Force/power ceilings, slew 10,000 N/s, reserve factor 2, empty initial banks, reset duty, losses, cooling, interface mass, stock, supports and renewals are unchanged. Only technology/capacity is physical; release shares 0.2/0.5/0.8 are evaluation controls. No raw bank energy is credited as free traction or removed by an invented dump.',
        '', f"The cheapest tested storage case adds ${cheapest['delta_capital_usd_base_vs_no_store']/1e6:.4f}m capital and ${cheapest['delta_NPV_usd_base_vs_no_store']/1e6:.4f}m NPV to no-store. For identical hydraulic 4 MJ hardware, enabling recovery changes traction by {delta['traction_grid_kwh']:+.5f} kWh over 16 journeys and reset consumption by {delta['reset_grid_kwh']:+.5f} kWh, changes annual total grid consumption by {delta['annual_grid_kwh_base']:+,.2f} kWh and changes NPV by ${delta['whole_life_NPV_usd_base']:+,.2f}. Finite-run traction savings alone therefore do not establish complete-service savings.",
        '', f"The hydraulic 4 MJ state ends with {occupancy['final_store_j']/1e6:.6f} MJ retained across the two stations; {occupancy['release_bypassed_departures']} releases and {occupancy['capture_bypassed_departures']} captures are bypassed. The sealed finding contains final per-bank energy and exact ownership event times. {f['diagnosis']} Capacity/share changes do not remove that ownership conflict.",
        '', 'The next experiments are ranked independently of any integrated selection: first explicitly model capture/release dispatch priority and continuous force handover using the same hardware; second price and model separate transfer paths or split banks; third obtain detailed interface/machinery evidence before changing fixed mass or package prices. Each must retain lost-capture accounting, independent stopping, passenger service, reset duty and cost. None was executed in this cycle.',
        '', 'All fourteen capital/lifecycle scopes are present. Low/base/high figures are calculated outline rates and allowances, not supplier quotations. Actual force-speed-duty curves, spring fatigue, hydraulic flow, cooling, installed mounts, ground conditions and reliability remain unverified. Nominal zero-grade results do not establish grade/fault capability or physical acceptance. Finance, taxes, customs and exchange-rate policy remain separate excluded layers.',
        '', 'Files: [comparison.csv](comparison.csv),[sealed study](study.json),[ownership and next-experiment finding](finding.json),[run usage](usage.json),[sealed evidence archive](evidence.tar.gz),[packet manifest](manifest.json). The archive retains exact requests,outputs,receipts,logs,full case ledgers,body and civil packets. Rebuildable native target files and duplicate stdout are omitted; their original hashes remain in the untouched original run manifest.',
        '', f"Validation: the original source change passed 23 focused/new and existing closure tests; this run retained {study['numerical_cases']} native cases in {usage['native_batches']} resource-bounded batches. The complete run used {usage['wall_s']:.2f} s wall, {usage['coordinator_peak_rss_KiB']/1024:.2f} MiB coordinator peak RSS and {usage['run_bytes_before_manifest']/1024**2:.2f} MiB disk. These are software/model checks, not physical validation.",
        '', 'Reproduce from the frozen source with `.venv/bin/python -m engineering.recovery_search run --output <new-private-directory>`. Recorded-run verification: `.venv/bin/python -m engineering.recovery_search verify --output <directory>`. Public packet verification from this repository: `.venv/bin/python tools/publish_recovery_economics.py verify --packet docs/design-engine/recovery-economics`. The actual original invocation also applied `prlimit --as=2147483648 --cpu=900 --`; each native two-case batch imposed1GiB address space,60CPU seconds and75wall seconds.',
        '', 'Content hashes verify recorded integrity. This is not an OS-enforced read-only environment, an independent solver rerun or a safety approval.','']
    return '\n'.join(text).encode()


def publish(run,output,source_commit=None):
    from engineering.recovery_search.search import verify
    run=Path(run).resolve();out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    proof=verify(run);study=sealed(read(run/'study.json'));f=finding(run)
    reference=study['source_commit'] if source_commit is None else source_commit
    for name in ('study.json','comparison.csv','usage.json','contract.json'):
        (out/name).write_bytes((run/name).read_bytes())
    (out/'finding.json').write_bytes(encoded(f));(out/'README.md').write_bytes(markdown(study,f,read(run/'usage.json')))
    origin=read(run/'manifest.json');include=[]
    for name in origin['files_sha256']:
        if name.startswith('native/native-target/') or name=='native/native-build.lock' or name.endswith('/stdout.json.gz'):continue
        include.append(name)
    include.append('manifest.json')
    snapshots={}
    for name,want in origin['source_sha256'].items():
        raw=(ROOT/name).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=want:raise ValueError('Exact source snapshot required: '+name)
        if source_commit is not None:
            declared=subprocess.check_output(['git','show',source_commit+':'+name],cwd=ROOT)
            if hashlib.sha256(declared).hexdigest()!=want:raise ValueError('Supplied source commit differs: '+name)
        snapshots['_source_snapshot/'+name]=raw
    with (out/'evidence.tar.gz').open('xb') as stream:
        with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0,filename='') as compressed:
            with tarfile.open(fileobj=compressed,mode='w') as tar:
                for name in sorted(include):
                    raw=(run/name).read_bytes();info=tarfile.TarInfo(name);info.size=len(raw)
                    info.mode=0o644;info.mtime=0;tar.addfile(info,io.BytesIO(raw))
                for name,raw in sorted(snapshots.items()):
                    info=tarfile.TarInfo(name);info.size=len(raw);info.mode=0o644;info.mtime=0
                    tar.addfile(info,io.BytesIO(raw))
    packet=dict(schema='osr-recovery-economics-publication/1',study_id=proof['study_id'],
        original_run_manifest_id=proof['manifest_id'],source_commit=study['source_commit'],source_reference_commit=reference,
        source_snapshots_self_contained=True,
        archive_members_sha256={**{name:digest(run/name) for name in sorted(include)},
            **{name:hashlib.sha256(raw).hexdigest() for name,raw in snapshots.items()}},
        omitted_original_members={name:h for name,h in origin['files_sha256'].items() if name not in include},
        files_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()},
        generator_sha256=digest(__file__),original_numeric_case_count=32,new_numerical_executions=0,
        automatic_selection=None,physical_accepted=False,selected_reference_changed=False)
    packet['manifest_id']=identity(packet);(out/'manifest.json').write_bytes(encoded(packet))
    return verify_packet(out)


def verify_packet(output):
    out=Path(output).resolve();packet=sealed(read(out/'manifest.json'),'manifest_id')
    if {p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='manifest.json'}!=packet['files_sha256']:raise ValueError('Publication file changed')
    if digest(__file__)!=packet['generator_sha256']:raise ValueError('Publication generator changed')
    members={}
    with tarfile.open(out/'evidence.tar.gz','r:gz') as tar:
        for m in tar.getmembers():
            if not m.isfile() or m.name in members or Path(m.name).is_absolute() or '..' in Path(m.name).parts:raise ValueError('Invalid archive member')
            members[m.name]=tar.extractfile(m).read()
    if {n:hashlib.sha256(b).hexdigest() for n,b in members.items()}!=packet['archive_members_sha256']:raise ValueError('Archive changed')
    origin=sealed(json.loads(members['manifest.json']),'manifest_id')
    if origin['manifest_id']!=packet['original_run_manifest_id']:raise ValueError('Origin differs')
    for name,raw in members.items():
        if name!='manifest.json' and not name.startswith('_source_snapshot/') and hashlib.sha256(raw).hexdigest()!=origin['files_sha256'][name]:raise ValueError('Original artifact changed')
    if {n:h for n,h in origin['files_sha256'].items() if n not in members}!=packet['omitted_original_members']:raise ValueError('Omitted artifacts differ')
    if json.loads(members['source-before.json'])!=json.loads(members['source-after.json']):raise ValueError('Original source drift')
    if {n[len('_source_snapshot/'):] for n in members if n.startswith('_source_snapshot/')}!=set(origin['source_sha256']):raise ValueError('Source snapshot coverage differs')
    for name,want in origin['source_sha256'].items():
        raw=members['_source_snapshot/'+name]
        if hashlib.sha256(raw).hexdigest()!=want:raise ValueError('Frozen source snapshot differs: '+name)
    study=sealed(read(out/'study.json'));f=sealed(read(out/'finding.json'))
    if study['evaluation_id']!=packet['study_id'] or f['study_id']!=study['evaluation_id'] or (out/'study.json').read_bytes()!=members['study.json']:raise ValueError('Study/finding differs')
    if (out/'comparison.csv').read_bytes()!=members['comparison.csv']:raise ValueError('Comparison differs')
    q=json.loads(gzip.decompress(members['cases/hydraulic-4MJ-share0.8.json.gz']))
    if f['case_evaluation_id']!=sealed(q)['evaluation_id'] or f['residual_occupancy']!=q['residual_occupancy']:raise ValueError('Occupancy differs')
    return dict(verified=True,study_id=packet['study_id'],manifest_id=packet['manifest_id'],source_commit=packet['source_commit'],
        archive_bytes=(out/'evidence.tar.gz').stat().st_size,new_numerical_executions=0,physical_accepted=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('publish','verify'));p.add_argument('--run-dir');p.add_argument('--packet',required=True);p.add_argument('--source-commit')
    a=p.parse_args()
    if a.command=='publish' and not a.run_dir:p.error('--run-dir required')
    print(json.dumps(publish(a.run_dir,a.packet,a.source_commit) if a.command=='publish' else verify_packet(a.packet),sort_keys=True))
