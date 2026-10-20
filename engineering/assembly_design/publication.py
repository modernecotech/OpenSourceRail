"""Portable assembly evidence; displayed data must match sealed original results."""
from hashlib import sha256
from html import escape
from pathlib import Path
import gzip
import io
import json
import shutil
import tarfile

from engineering.twin_workflow import core
from engineering.design_delivery.pipeline import safe,archive_members
from . import workflow

# Six additional native section exhibits and their raw numerical evidence are
# retained alongside the14-route desktop source bundle. Keep the complete
# portable package below48MiB rather than discarding evidence to fit32MiB.
MAX_BYTES=64*1024**2


def exhibits(data):
    """One copying/verification path; diagnostic exhibits never imply selection."""
    return [('models',entry) for entry in data['selected']]+[('diagnostics',entry) for entry in data.get('diagnostics',[])]


def report(data,policy):
    h=lambda value:escape(str(value),quote=True)
    counts=data['counts'];lines=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Baghdad assembly design programme</title>',
        '<style>body{font:16px system-ui;max-width:1200px;margin:2rem auto;padding:1rem;color:#18384c}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd;padding:.4rem;text-align:left}img{max-width:100%}code{overflow-wrap:anywhere}</style>',
        '<h1>Baghdad — sourced requirements and automatic assembly design</h1>',
        '<p>Provisional engineering development. No complete train, civil system, manufacturing qualification or physical release is claimed.</p>',
        '<p>'+h(counts['requirement_records'])+' scoped requirement records: '+h(counts['baghdad_records'])+' Baghdad reference parts plus '+h(counts['legacy_or_unreconciled_records'])+' legacy/unreconciled records. '+h(counts['facts'])+' sourced facts. '+h(counts['completed_trials'])+' completed trials; '+h(counts['qualified_components'])+' qualified components.</p>',
        '<p>'+h(data['controller_scope'])+'</p><p><a href="baseline.json.gz">Baseline and requirement inventory</a> | <a href="progress.json">Full progress and open work</a> | <a href="qualification.json">Executed test receipt</a> | <a href="tests.log">Test log</a> | <a href="evidence.tar.gz">Original evidence</a> | <a href="manifest.json">Checksums</a></p>']
    if 'closure' in data:
        c=data['closure']
        lines+=['<h2>Full design closure plan — execution and open exits</h2>',
            '<p>'+h(c['task_count'])+' deliverables across 13 work packages. '+h(c['engineering_closed_tasks'])+' engineering exits closed; '+h(c.get('digital_completed_tasks',0))+' digital specifications with complete reviewed records. Digital coverage, physical validation and manufacturing release are separate. Partial implementation and executed research checks do not constitute completed designs.</p>',
            '<p><a href="closure-progress.json">All task statuses, pilot contracts and RFQ/test requests</a> | <a href="prototype.json">Named prototype and conflicts</a> | <a href="family-crosswalk.json">414-record architecture/family crosswalk</a> | <a href="registers.json">Source, standards and family registers</a> | <a href="integration.json">Exact revision integration and open passage gates</a></p>',
            '<div lang="ar" dir="rtl"><h2>بغداد — متابعة استكمال التصميم</h2><p>هذه تصاميم ودراسات أولية. لم يكتمل تصميم القطار أو المنشآت، ولا يوجد تصريح للتصنيع أو التشغيل. يتضمن السجل '+h(c['task_count'])+' مهمة؛ لا توجد مهام ذات قبول هندسي نهائي. الفحوص البرمجية والهندسية المنفذة منفصلة عن الاختبارات الميدانية والقبول المستقل. تبقى بيانات التربة والموردين والاختبارات الفعلية مطلوبة.</p><p>توضح الروابط أعلاه المتطلبات والمكونات والواجهات والأدلة والمهمة التالية لكل حزمة عمل. لم تُرسل طلبات البيانات أو عروض الأسعار إلى أي جهة.</p></div>',
            '<details><summary>Every plan task and its remaining work</summary><table><tr><th>Task / PDF page</th><th>Deliverable</th><th>Implementation evidence / limit</th><th>Engineering exit</th></tr>']
        for task in c['tasks']:
            lines+=['<tr><td>'+h(task['id'])+' / '+h(task['page'])+'</td><td>'+h(task['title'])+'</td><td>'+h(task['implementation'])+'; '+h(task.get('implementation_scope',task['next_action']))+'</td><td>'+h(task['engineering_exit'])+'</td></tr>']
        lines+=['</table></details>']
        if data.get('additional_design_studies'):
            lines+=['<h2>Additional PDF design work executed</h2><p><a href="studies/index.html">Detailed cassette, civil reinforcement/handling, part handoff, electrical architecture and '+h(data['additional_design_studies']['duty_cases'])+' coupled HVAC/battery/control duty cases</a>. Native results, failures, unissued drawings, images and trace video are retained with the exact source epoch. Full engineering exits remain open.</p>']
        if c.get('site_screening_revision'):
            s=data['site_summary']
            lines+=['<h2>Baghdad — usable desktop site estimates</h2><p><a href="site/summary.json">Source dates, resolution, coverage, uncertainty, per-route estimates and investigation quantities</a> | <a href="site/map.geojson.gz">Detailed map layers (compressed GeoJSON)</a> | <a href="site/evidence.tar.gz">Portable source samples</a></p>',
                '<table><tr><th>Estimate</th><th>Result</th><th>Scope / uncertainty</th></tr>',
                '<tr><td>WorldPop 2026 context population</td><td>'+h(f'{s["modelled_population"]:,.0f}')+'</td><td>Modelled residents in 44.1–44.6°E, 33.1–33.5°N; not census or rail demand</td></tr>',
                '<tr><td>SRTM-derived elevation</td><td>Median '+h(s['median_elevation_m'])+' m; 5th–95th '+h(s['elevation_percentiles_m']['5'])+'–'+h(s['elevation_percentiles_m']['95'])+' m</td><td>Unsure local vertical accuracy and datum; surface/outlier effects; no survey, flood stage or groundwater level</td></tr>',
                '<tr><td>WorldCover 2021 classes</td><td>Built-up '+h(f'{100*s["built_up_fraction"]:.2f}')+'%; permanent water '+h(f'{100*s["permanent_water_fraction"]:.2f}')+'%</td><td>'+h(f'{s["classified_area_km2"]:,.1f}')+' km² approximate sampled area. Western 44.1–44.2°E land-cover gap; unknown is not dry/vacant land</td></tr>',
                '<tr><td>Clipped concept corridors</td><td>'+h(s['concept_route_count'])+' lines; '+h(f'{s["concept_route_length_km"]:,.1f}')+' route-km; '+h(s['river_centreline_crossings'])+' river-centreline intersections</td><td>Repository alternatives, not surveyed or adopted alignments; crossings are screening events, not designed bridges</td></tr>',
                '<tr><td>Provisional investigation quantities</td><td>'+h(s['investigation_locations']['250'])+' locations at 250 m; '+h(s['investigation_locations']['500'])+' at 500 m</td><td>Chainage scenarios; shared corridors can duplicate locations. Not a specified borehole programme</td></tr>',
                '<tr><td>Land-use investigation candidates</td><td>'+h(s['landuse_investigation_candidates'])+'</td><td>Mapped parcels for investigation only; ownership, availability, services and soil capacity unconfirmed</td></tr>']
            for row in s['network_corridor_population']:
                bounds=row['algorithm_bounds']
                lines+=['<tr><td>Unique population within '+h(row['radius_m'])+' m of concept lines</td><td>'+h(f'{row["nominal"]["persons"]:,.0f}')+'; distance-sampling range '+h(f'{bounds["lower"]["persons"]:,.0f}')+'–'+h(f'{bounds["upper"]["persons"]:,.0f}')+'</td><td>WorldPop 2026 retained extent 44.2–44.75°E, 33.05–33.5°N; ±25 m algorithm bound plus separate pixel/route/model uncertainty. Not station access or ridership</td></tr>']
            lines+=['</table>',
                '<img alt="Actual open water, infrastructure, land use and population with proposed Baghdad corridors" src="site/map.svg">',
                '<p>Terrain, population and mapped infrastructure support investigation planning. River proximity supplies no design flood level, groundwater depth or soil bearing capacity. Corridor proximity estimates are separate from station access and ridership; overlapping routes are counted once in the population union. Missing map coverage remains unknown.</p>',
                '<p lang="ar" dir="rtl">تقديرات مكتبية مبنية على بيانات مفتوحة فعلية للسكان والتضاريس والمياه والبنية التحتية. تساعد في تحديد أولويات المسح والتحريات؛ ولا تثبت قدرة تحمل التربة أو منسوب المياه الجوفية أو الفيضان أو ملكية الأراضي. أعداد السكان قرب المسارات ليست توقعات لعدد الركاب.</p>']
    for category,c in exhibits(data):
        base=category+'/'+c['kind']+'/'
        if category=='diagnostics':lines+=['<h2>Excluded diagnostic exhibit</h2><p>This candidate failed mandatory checks and is excluded from research and integration selection. Geometry and harness data are retained to diagnose and repair it.</p>']
        lines+=['<h2>'+h(c['kind'])+'</h2><p>Exact candidate <code>'+h(c['key'])+'</code>. Native state: '+h(c['native'])+'. '+h(c['scope'])+'</p>',
            '<p><a href="'+base+'candidate.json.gz">Part/joint definition</a> | <a href="'+base+'result.json">Checks and unresolved requirements</a> | <a href="'+base+'manufacturing-bom.csv">Manufacturing BOM and dimensions</a> | <a href="'+base+'qa-plan.json">Unexecuted QA plan</a></p>',
            '<img alt="Unissued inspection layout from generated definitions" src="'+base+'inspection.svg">']
        if c['native']=='completed':
            lines+=['<img alt="Retained native model, with purchased coordination envelopes" src="'+base+'overview.png"><p><a href="'+base+'model.FCStd">Native FreeCAD</a> | <a href="'+base+'model.step.gz">Compressed STEP</a> — correspondence/static overlap checks only; bought-out items may be coordination envelopes.</p>']
            if 'closure' in data:lines+=['<p><a href="'+base+'assembly.ifc.gz">Native-derived IFC</a> | <a href="'+base+'requirements.ids">Required information (IDS)</a> | <a href="'+base+'ids-report.json">Executed IFC information checks</a>. Information exchange preserves identities; it does not grant engineering acceptance.</p>']
        if 'closure' in data and c['kind']=='service-cassette':
            lines+=['<p><a href="'+base+'cassette-system.json">Electrical/HVAC, solder harness, process/removal graph, tolerance failures and open qualification</a>. This supplemental chain has known failed fit screens and unresolved supplier/physical gates; the retained geometry representative is not system eligible.</p>']
    lines+=['<h2>Evaluated alternatives</h2><table><tr><th>Family</th><th>Variables</th><th>State</th><th>Represented mass kg</th><th>Failed / held checks</th></tr>']
    for trial in data['trials']:lines+=['<tr><td>'+h(trial['kind'])+'</td><td>'+h(json.dumps(trial['variables'],sort_keys=True))+'</td><td>'+h(trial.get('state',trial['status']))+'</td><td>'+h(trial.get('mass_kg'))+'</td><td>'+h(', '.join(trial.get('failed_checks',[])+trial.get('held_checks',[])))+'</td></tr>']
    lines+=['</table><h2>Reference facts and applicability</h2><table><tr><th>Fact</th><th>Value / unit</th><th>Source and scope</th></tr>']
    for fact in policy['facts']:
        source=policy['sources'].get(fact['source']);reference='<a href="'+h(source['url'])+'">'+h(fact['source'])+'</a>' if source else h(fact['source'])
        lines+=['<tr><td>'+h(fact['id'])+'</td><td>'+h(json.dumps(fact['value']))+' '+h(fact['unit'])+'</td><td>'+reference+'; '+h(fact['locator'])+'; '+h(fact['applicability'])+'</td></tr>']
    lines+=['</table><h2>Open design work</h2>']
    for kind,needs in data['pilot_open_requirements'].items():lines+=['<h3>'+h(kind)+'</h3><ul>']+['<li>'+h(n)+'</li>' for n in needs]+['</ul>']
    lines+=['<p>'+h(counts['component_records_needing_adapter'])+' scoped component records still need component-specific generators/evaluators. Work orders retain all seven design/acceptance stages as open.</p></html>']
    return '\n'.join(lines)


def export(workspace,output):
    output=Path(output).resolve()
    if output.exists():raise ValueError('new export directory required')
    with workflow.locked(workspace) as (workspace,db):
        epoch=core.read(workspace/'active.json')['epoch'];epoch_path=workspace/'epochs'/epoch;prepared=core.read(epoch_path/'baseline.json',maximum=30_000_000)
        data=workflow.summary(workspace,db,epoch,prepared);output.mkdir(parents=True)
        (output/'baseline.json.gz').write_bytes(gzip.compress((epoch_path/'baseline.json').read_bytes(),mtime=0))
        for name in ('qualification.json','tests.log','work-orders.json'):shutil.copyfile(epoch_path/name,output/name)
        if 'closure' in data:
            from . import closure_evidence
            closure_evidence.export_raw(prepared,output/'closure-records')
            for name,value in [('closure-progress.json',data['closure']),('prototype.json',prepared['prototype']),
                ('family-crosswalk.json',prepared['family_crosswalk']),('registers.json',prepared['registers']),('integration.json',prepared['integration'])]:core.write(output/name,value)
        if prepared.get('site'):
            from . import site_bundle
            site_bundle.export(prepared['site'],output/'site')
        companion=epoch_path/'closure-studies'
        if companion.exists():
            from . import design_studies
            design_studies.verify(companion,prepared)
            shutil.copytree(companion,output/'studies')
        folders={}
        for row in db.execute("SELECT * FROM jobs WHERE epoch=? AND status='completed'",(epoch,)):
            workflow.verify_folder(row['folder']);folders[row['key']]=Path(row['folder'])
        for row in db.execute('SELECT n.* FROM native n JOIN jobs j ON j.key=n.child WHERE j.epoch=?',(epoch,)):
            if (Path(row['folder'])/'receipt.json').exists():workflow.verify_folder(row['folder']);folders[row['child']+'-native']=Path(row['folder'])
        raw=0;index={}
        with (output/'evidence.tar.gz').open('wb') as stream,gzip.GzipFile(fileobj=stream,mode='wb',mtime=0,filename='') as zipped,tarfile.open(fileobj=zipped,mode='w|') as archive:
            for key,folder in sorted(folders.items()):
                receipt=workflow.verify_folder(folder);index[key]=core.sha(folder/'receipt.json')
                for name in ('receipt.json',*sorted(receipt['files_sha256'])):
                    content=(folder/name).read_bytes();raw+=len(content)
                    if raw>128*1024**2:raise ValueError('assembly raw evidence budget exceeded')
                    info=tarfile.TarInfo(key+'/'+name);info.size=len(content);info.mtime=0;archive.addfile(info,io.BytesIO(content))
        for category,entry in exhibits(data):
            row=db.execute('SELECT * FROM jobs WHERE key=?',(entry['key'],)).fetchone();destination=output/category/entry['kind'];destination.mkdir(parents=True)
            folder=Path(row['folder'])
            for name in ('candidate.json.gz','result.json','manufacturing-bom.csv','qa-plan.json','inspection.svg','netlist.json','controller.py','software-tests.json','cassette-system.json'):
                if (folder/name).exists():shutil.copyfile(folder/name,destination/name)
            if entry['native']=='completed':
                native=db.execute('SELECT * FROM native WHERE child=?',(entry['key'],)).fetchone();nf=Path(native['folder']);workflow.verify_folder(nf)
                shutil.copyfile(nf/'cad/candidate.FCStd',destination/'model.FCStd')
                (destination/'model.step.gz').write_bytes(gzip.compress((nf/'cad/candidate.step').read_bytes(),mtime=0))
                shutil.copyfile(nf/'result.json',destination/'native-result.json');shutil.copyfile(nf/'overview.png',destination/'overview.png')
                if (nf/'bim/assembly.ifc').exists():
                    (destination/'assembly.ifc.gz').write_bytes(gzip.compress((nf/'bim/assembly.ifc').read_bytes(),mtime=0))
                    for name in ('requirements.ids','ids-report.json','receipt.json'):shutil.copyfile(nf/'bim'/name,destination/('bim-receipt.json' if name=='receipt.json' else name))
        for row in db.execute("SELECT * FROM jobs WHERE epoch=? AND kind='cassette-control' AND status='completed'",(epoch,)):
            destination=output/'software'/json.loads(row['variables'])['variant'];destination.mkdir(parents=True)
            for name in ('controller.py','result.json'):shutil.copyfile(Path(row['folder'])/name,destination/name)
        core.write(output/'progress.json',data);(output/'index.html').write_text(report(data,prepared['policy']))
        manifest=dict(schema='osr-assembly-publication/1',epoch=epoch,progress_digest=core.digest(data),evidence_receipts=index,
            files_sha256={p.relative_to(output).as_posix():core.sha(p) for p in output.rglob('*') if p.is_file()},**core.FLAGS)
        core.write(output/'manifest.json',manifest);verify(output)
        return manifest


def verify(output):
    output=Path(output).resolve();m=core.read(output/'manifest.json',maximum=20_000_000)
    if m['schema']!='osr-assembly-publication/1' or any(m.get(k) is not False for k in core.FLAGS):raise ValueError('assembly publication scope changed')
    actual={p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}
    if actual!={'manifest.json',*m['files_sha256']}:raise ValueError('unsealed assembly export')
    total=0
    for name,digest in m['files_sha256'].items():
        path=output/safe(name);total+=path.stat().st_size
        if path.is_symlink() or not path.resolve().is_relative_to(output) or core.sha(path)!=digest:raise ValueError('assembly export bytes changed')
    if total>MAX_BYTES:raise ValueError('assembly export budget exceeded')
    raw=gzip.decompress((output/'baseline.json.gz').read_bytes());prepared=json.loads(raw)
    if core.digest(prepared)!=m['epoch']:raise ValueError('assembly source epoch differs')
    q=core.read(output/'qualification.json',maximum=20_000_000)
    if not q['passed'] or q['sources']!=prepared['source_sha256'] or q['runtime_identity']!=prepared['runtime_identity'] or q['log_sha256']!=core.sha(output/'tests.log'):raise ValueError('assembly qualification differs')
    members=archive_members(output/'evidence.tar.gz');expected=set()
    for key,digest in m['evidence_receipts'].items():
        receipt_bytes=members[key+'/receipt.json'];receipt=json.loads(receipt_bytes)
        if sha256(receipt_bytes).hexdigest()!=digest or receipt['key']!=key or receipt['epoch']!=m['epoch']:raise ValueError('assembly receipt identity differs')
        expected.add(key+'/receipt.json')
        for name,digest in receipt['files_sha256'].items():
            path=key+'/'+safe(name);expected.add(path)
            if sha256(members[path]).hexdigest()!=digest:raise ValueError('archived assembly evidence changed')
        if any(receipt.get(k) is not False for k in core.FLAGS):raise ValueError('assembly receipt cannot grant release')
        if key.endswith('-native'):
            if receipt['child']+'-native'!=key:raise ValueError('native confirmation child differs')
        else:
            if receipt['baseline_sha256']!=sha256(raw).hexdigest() or core.digest(dict(epoch=m['epoch'],kind=receipt['kind'],variables=receipt['variables']))!=key:raise ValueError('assembly task identity differs')
    if set(members)!=expected:raise ValueError('unreceipted assembly evidence')
    data=core.read(output/'progress.json',maximum=20_000_000)
    if data['epoch']!=m['epoch'] or any(data.get(k) is not False for k in core.FLAGS) or data['counts']['qualified_components']!=0:raise ValueError('assembly progress scope differs')
    if data['source_sha256']!=prepared['source_sha256'] or core.read(output/'work-orders.json',maximum=20_000_000)!=workflow.work_orders(prepared):raise ValueError('requirement/work-order allocation differs')
    if prepared.get('closure_plan'):
        from . import closure,families
        subjects=None
        if data.get('additional_design_studies'):
            from . import design_studies
            design_studies.verify(output/'studies',prepared)
            subjects=design_studies.completion_subjects(output/'studies')
            if data.get('closure_subjects')!=subjects:raise ValueError('closure component subjects differ')
        from . import closure_evidence
        closure_evidence.verify_raw(output/'closure-records')
        if data.get('closure')!=closure.snapshot(prepared,subjects=subjects,evidence_root=output/'closure-records') or data.get('families')!=families.registry(prepared['policy']):raise ValueError('closure status or family allocation differs')
        for name,value in [('closure-progress.json',data['closure']),('prototype.json',prepared['prototype']),
            ('family-crosswalk.json',prepared['family_crosswalk']),('registers.json',prepared['registers']),('integration.json',prepared['integration'])]:
            if core.read(output/name,maximum=20_000_000)!=value:raise ValueError('exported closure, source or integration copy differs')
    if prepared.get('site'):
        from . import site_bundle
        if data.get('site_summary')!=site_bundle.metrics(prepared['site']):raise ValueError('displayed site estimates differ from source samples')
        site_bundle.verify(prepared['site'],output/'site')
    if data.get('additional_design_studies'):
        from . import design_studies
        executed=design_studies.verify(output/'studies',prepared)
        expected_studies=dict(revision=core.digest(executed),models=executed['models'],duty_cases=len(executed['duty_cases']),
            scope='Additional provisional detail and coupled duty; full PDF engineering exits remain open')
        if data['additional_design_studies']!=expected_studies:raise ValueError('displayed additional design studies differ')
    elif (output/'studies').exists():raise ValueError('undisclosed additional design studies')
    inv=prepared['inventory']
    expected_counts=dict(requirement_records=len(inv['items']),baghdad_records=inv['baghdad_reference_items'],legacy_or_unreconciled_records=inv['existing_items'],component_records_with_pilot=sum(i['pilot'] is not None for i in inv['items']),component_records_needing_adapter=sum(i['pilot'] is None for i in inv['items']),facts=len(prepared['policy']['facts']),completed_trials=sum(not k.endswith('-native') for k in m['evidence_receipts']),qualified_components=0)
    if data['counts']!=expected_counts:raise ValueError('displayed assembly counts differ from evidence')
    if {t['key'] for t in data['trials'] if t['status']=='completed'}!={k for k in m['evidence_receipts'] if not k.endswith('-native')}:raise ValueError('trial membership differs from evidence')
    for trial in data['trials']:
        if trial['status']!='completed':continue
        r=json.loads(members[trial['key']+'/result.json']);receipt=json.loads(members[trial['key']+'/receipt.json'])
        if trial['kind']!=receipt['kind'] or trial['variables']!=receipt['variables']:raise ValueError('exported trial differs from original')
        if trial['kind']!='cassette-control':
            failed=[name for name,value in r['checks'].items() if value is False];held=[name for name,value in r['checks'].items() if value is None]
            if set(failed)!=set(r['failed_checks']) or set(held)!=set(r['held_checks']):raise ValueError('mandatory check classification differs')
            if r['screen_pass']!=(not failed and not held) or r['implemented_checks_pass']!=(not failed):raise ValueError('mandatory check eligibility differs')
        expected_fields=dict(state=r.get('state','offline-tests'),mass_kg=r.get('measurements',{}).get('mass_kg'),failed_checks=r.get('failed_checks',[]),held_checks=r.get('held_checks',[]))
        if any(trial.get(k)!=v for k,v in expected_fields.items()):raise ValueError('displayed trial differs from original')
        if trial['kind']=='service-cassette' and r.get('supplemental_evidence'):
            chain=r['supplemental_evidence']['cassette-system']
            if chain!=json.loads(members[trial['key']+'/cassette-system.json']) or chain['unit_revision']!=r['candidate_revision']:raise ValueError('supplemental cassette evidence differs')
            if chain['revision']!=core.digest({name:value for name,value in chain.items() if name!='revision'}):raise ValueError('supplemental cassette revision differs')
            if any('cassette-system/'+name not in r['checks'] or r['checks']['cassette-system/'+name]!=value for name,value in chain['checks'].items()):raise ValueError('mandatory cassette checks not propagated')
        if trial['kind']=='cassette-control':
            folder=output/'software'/receipt['variables']['variant']
            for name in ('controller.py','result.json'):
                if (folder/name).read_bytes()!=members[trial['key']+'/'+name]:raise ValueError('exported software differs from original')
    if {r['key'] for r in data['selected']}&{r['key'] for r in data.get('diagnostics',[])}:raise ValueError('diagnostic candidate promoted to selection')
    for category,entry in exhibits(data):
        key=entry['key'];folder=output/category/safe(entry['kind'])
        receipt=json.loads(members[key+'/receipt.json']);result=json.loads(members[key+'/result.json'])
        if entry['kind']!=receipt['kind'] or entry.get('design_complete') is not False:raise ValueError('assembly exhibit identity or scope differs')
        if category=='models' and (result['failed_checks'] or entry['scope']!='Provisional research representative; all assembly closure and qualification holds remain applicable'):raise ValueError('selected assembly scope or eligibility differs')
        if category=='diagnostics' and (entry.get('selection_eligible') is not False or entry['scope']!=workflow.DIAGNOSTIC_SCOPE):raise ValueError('diagnostic scope or exclusion differs')
        native_key=key+'-native/result.json'
        state=json.loads(members[native_key])['state'] if native_key in members else 'not-run'
        if (category=='models' and state=='failed') or entry['native']!=('completed' if state=='passed' else state):raise ValueError('selected native eligibility differs')
        if category=='diagnostics' and not result['failed_checks'] and state!='failed':raise ValueError('diagnostic lacks recorded failure')

        for name in ('candidate.json.gz','result.json','manufacturing-bom.csv','qa-plan.json','inspection.svg','netlist.json','controller.py','software-tests.json','cassette-system.json'):
            original=members.get(key+'/'+name)
            if original is not None and (folder/name).read_bytes()!=original:raise ValueError('exported assembly copy differs from original')
        if entry['native']=='completed':
            for name in ('native-result.json','overview.png'):
                original='result.json' if name=='native-result.json' else name
                if (folder/name).read_bytes()!=members[key+'-native/'+original]:raise ValueError('exported native record/picture differs from original')
            nr=json.loads(members[key+'-native/result.json'])
            if nr['child']!=key or nr['state']!='passed':raise ValueError('failed native evidence cannot support a selected confirmation')
            if (folder/'model.FCStd').read_bytes()!=members[key+'-native/cad/candidate.FCStd'] or gzip.decompress((folder/'model.step.gz').read_bytes())!=members[key+'-native/cad/candidate.step']:raise ValueError('exported native geometry differs from original')
            if key+'-native/bim/assembly.ifc' in members:
                if gzip.decompress((folder/'assembly.ifc.gz').read_bytes())!=members[key+'-native/bim/assembly.ifc']:raise ValueError('exported IFC differs from native exchange evidence')
                for name in ('requirements.ids','ids-report.json','receipt.json'):
                    destination='bim-receipt.json' if name=='receipt.json' else name
                    if (folder/destination).read_bytes()!=members[key+'-native/bim/'+name]:raise ValueError('exported IDS evidence differs')
    if core.digest(data)!=m['progress_digest']:raise ValueError('assembly progress digest differs')
    if (output/'index.html').read_text()!=report(data,prepared['policy']):raise ValueError('displayed assembly report differs from originals')
    return dict(verified=True,files=len(m['files_sha256']),evidence_jobs=len(m['evidence_receipts']),bytes=total,**core.FLAGS)
