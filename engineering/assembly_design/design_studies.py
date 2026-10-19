"""Additional PDF work-package executions in the existing source-bound epoch.

Not a second queue: assembly_design.run builds this bounded companion once the
registered search domain finishes. Failed native/detail results are retained,
never turned into selected or accepted designs.
"""
from html import escape
from pathlib import Path
import csv
import gzip
import io
import itertools
import json
import shutil
import subprocess
import tempfile

from engineering.twin_workflow import core
from engineering.continuous_design import study_confirmation,civil_kit
from . import baseline, models, system_design

MAX_BYTES=20*1024**2


def verify_exchange_mesh(candidate,folder):
    """IFC coordinates/topology/placement must match the retained native mesh."""
    import numpy as np
    import ifcopenshell
    import ifcopenshell.util.placement
    folder=Path(folder);mesh=core.read(folder/'native-mesh.json',maximum=60_000_000)
    model=ifcopenshell.open(str(folder/'assembly.ifc'));products={p.Name:p for p in model.by_type('IfcBuildingElementProxy')}
    if set(products)!={p['id'] for p in candidate['contract']['parts']} or {p['id'] for p in mesh['parts']}!=set(products):
        raise ValueError('exchange mesh part identities differ')
    for part in mesh['parts']:
        product=products[part['id']];items=[item for representation in product.Representation.Representations for item in representation.Items]
        if len(items)!=1 or not items[0].is_a('IfcTriangulatedFaceSet'):raise ValueError('unexpected exchange geometry representation')
        item=items[0];vertices=np.asarray(item.Coordinates.CoordList);faces=np.asarray(item.CoordIndex)-1
        if vertices.shape!=np.asarray(part['vertices']).shape or not np.allclose(vertices,part['vertices'],rtol=1e-12,atol=1e-12) or not np.array_equal(faces,part['faces']):
            raise ValueError('IFC geometry differs from native triangles')
        if not np.allclose(ifcopenshell.util.placement.get_local_placement(product.ObjectPlacement),np.eye(4),atol=1e-12):
            raise ValueError('IFC native geometry placement differs')


def _candidate(policy,kind):
    choices={k:v[0] for k,v in policy['pilots'][kind]['domains'].items()}
    if kind=='service-cassette':
        # Respect the original owned tray/cover envelope; a larger airflow area
        # cannot be obtained by silently letting a duct pass through the cover.
        choices['duct_area_m2']=max(area for area in policy['pilots'][kind]['domains']['duct_area_m2']
            if .04+area/.2+.002<=policy['pilots'][kind]['assumptions']['height_m'])
    return models.build(policy,kind,choices)


def _choose(variants):
    """Failed variants may be diagnostic exhibits only, never eligible leaders."""
    def rank(pair):
        candidate,assessment=pair
        return (bool(assessment['failed_checks']),len(assessment['failed_checks']),len(assessment['held_checks']),
                sum(p['properties']['mass_kg'] for p in candidate['contract']['parts']),candidate['revision'])
    return min(variants,key=rank)


def handoff(pairs):
    stream=io.StringIO();fields=('family','part','revision','joint_ids','process','material','mass_kg','definition','analysis','qa')
    writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
    for candidate,assessment in pairs:
        kind=candidate['kind']
        for part in candidate['contract']['parts']:
            writer.writerow(dict(family=kind,part=part['id'],revision=part['revision'],joint_ids=';'.join(part['joints']),
                process=part['process_route'],material=part['material'],mass_kg=part['properties']['mass_kg'],
                definition=kind+'/candidate.json.gz',analysis=kind+'/assessment.json',qa=kind+'/qa-plan.json'))
    return stream.getvalue()


def requests(prototype,pairs):
    from . import closure
    rows=closure.requests(prototype)
    by_pilot={'service-cassette':pairs[0],'structural-bay':pairs[2],'viaduct-bay':pairs[1]}
    for request in rows:
        candidate,assessment=by_pilot[request['pilot']];kind=candidate['kind']
        request.update(component_revision=candidate['revision'],
            included_component_scope=candidate['source_scope'],full_pilot_complete=False,
            remaining_full_pilot_characteristics='All open characteristics in the 88-task ledger and the pilot completion contract; this request covers the included component only',
            definition=kind+'/candidate.json.gz',analysis=kind+'/assessment.json',qa=kind+'/qa-plan.json',
            included_part_ids=[part['id'] for part in candidate['contract']['parts']],
            known_digital_failures=assessment['failed_checks'],known_digital_holds=assessment['held_checks'],
            build_authorised=False,samples_manufactured=0,
            sample_matrix=[dict(purpose=purpose,sample_count=None,agreed=False) for purpose in ('parameter identification','calibration','untouched holdout','destructive/adverse testing')])
    return rows


def installed_context(policy,candidate,kit):
    """Actual owned-part gross addition through existing mass/reaction adapters."""
    from osr_mech.family_definition import family_definition
    from . import integration,reactions
    parts=[p for p in candidate['contract']['parts'] if p['id'] in candidate['metadata']['cassette_installed_part_ids']]
    cars=family_definition('metro-6car')['cars']
    allocations=[dict(id=car['id']+'/cassette',translation_m=[car['centre_x_m'],0.,0.],rotation=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]) for car in cars]
    mass=integration.mass_properties(parts,allocations);facts=baseline.facts(policy);a=policy['pilots']['bearing-seat']['assumptions']
    train=reactions.revisioned(dict(architecture=policy['architecture'],mass_cases_kg=[v+mass['mass_kg'] for v in facts['train.mass_cases']],
        cars=a['train_cars'],car_length_m=facts['train.car_length'],tracks=a['tracks'],span_m=a['span_m'],gravity_m_s2=a['gravity_m_s2'],
        permanent_factor=a['vertical_factor'],variable_factor=a['vertical_factor']))
    variables={k:v[0] for k,v in policy['pilots']['bearing-seat']['domains'].items()};variables['bearing_family']='uk-spherical-candidate'
    bearing=models.build(policy,'bearing-seat',variables)
    seat=reactions.revisioned(dict(candidate_revision=bearing['revision'],mass_kg=sum(p['properties']['mass_kg'] for p in bearing['contract']['parts'])))
    envelope=reactions.envelope(kit,train,seat,expected_kit_revision=core.digest(kit),expected_train_revision=train['revision'])
    value=dict(schema='osr-detailed-cassette-installed-context/1',candidate_revision=candidate['revision'],
        allocations=allocations,installed_part_ids=[p['id'] for p in parts],gross_added_properties=mass,train=train,seat=seat,
        force_ledger=envelope,removal_credit_kg=0.,admitted_for_system_simulation=False,
        scope='Six identical cassette gross additions at provisional car origins; complete vehicle baseline/net CG, actual mounts, host and vehicle-side services remain unallocated. No removal credit or dynamic validation.',**core.FLAGS)
    value['revision']=core.digest(value);return value


def _model(candidate,assessment,folder):
    from . import workflow,bim,presentation
    folder.mkdir();core.write(folder/'definition.json',candidate['contract'])
    (folder/'candidate.json.gz').write_bytes(gzip.compress(core.encoded(candidate),mtime=0))
    core.write(folder/'assessment.json',assessment);core.write(folder/'qa-plan.json',candidate['qa_plan'])
    if 'structural-detail' in assessment.get('supplemental_evidence',{}):
        detail=assessment['supplemental_evidence']['structural-detail'];core.write(folder/'structural-detail.json',detail)
        core.write(folder/'manufacturing-pack.json',detail['manufacturing_pack'])
    workflow.tables(candidate,folder)
    proof,state,error=study_confirmation.native(folder/'definition.json',folder/'native')
    if state=='passed':
        bim.export(candidate,folder/'native/candidate.FCStd',folder/'bim')
        presentation.preview(folder/'native/candidate.FCStd',folder/'overview.png',candidate['kind'])
        # Compressed exchange keeps the portable companion within a fixed budget.
        step=folder/'native/candidate.step';(folder/'model.step.gz').write_bytes(gzip.compress(step.read_bytes(),mtime=0))
    result=dict(kind=candidate['kind'],candidate_revision=candidate['revision'],
        native_state=state,native_error=error,native_proof=proof,parts=len(candidate['contract']['parts']),
        failed_checks=assessment.get('failed_checks',[]),held_checks=assessment.get('held_checks',[]),
        scope=candidate.get('source_scope','Provisional manufactured detail; complete pilot and physical exits remain open'),
        eligible_for_research=state=='passed' and not assessment.get('failed_checks'),**core.FLAGS)
    # Preserve the exact STEP bytes compressed, together with their raw hash.
    if state=='passed':
        (folder/'native/candidate.step').unlink()
        result['native_step_compressed_sha256']=core.sha(folder/'model.step.gz')
        if candidate['kind']=='service-cassette-detail':
            from . import motion_media
            result['motion_preview']=motion_media.cassette(candidate,folder/'bim/native-mesh.json',folder)
    core.write(folder/'result.json',result)
    return result


def confirm_alternatives(variants,folder,*,budget=3):
    """A failed native favourite cannot block the next bounded alternative.

    Unavailable/interrupted tools hold this evidence level immediately; cycling
    recipes cannot fix a missing tool. All failed-native attempts are retained.
    """
    remaining=list(variants);diagnostics=[]
    for attempt in range(min(budget,len(remaining))):
        pair=_choose(remaining);candidate,assessment=pair
        root=folder/candidate['kind'];result=_model(candidate,assessment,root)
        if result['native_state']!='failed' or assessment['failed_checks'] or attempt+1==min(budget,len(variants)):
            return pair,result,diagnostics
        destination=folder/'failed-native'/(candidate['kind']+'-'+candidate['revision'][:16])
        destination.parent.mkdir(exist_ok=True);root.rename(destination)
        diagnostics.append(dict(path=destination.relative_to(folder).as_posix(),result=result))
        remaining.remove(pair)
    raise ValueError('nonempty controlled variation set required')


def _duty_media(report,folder):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    cases=report['duty_cases'];fig,axes=plt.subplots(3,1,figsize=(10,8),sharex=True)
    for case in cases:
        rows=case['trace'];times=[r['time_s']/60 for r in rows]
        for axis,key in zip(axes,('cabin_c','soc','terminal_power_w')):
            axis.plot(times,[r[key] for r in rows],label=case['fault'],linewidth=1.)
    for axis,label in zip(axes,('Cabin °C','SOC','Terminal W / car')):axis.set_ylabel(label);axis.grid(alpha=.2)
    axes[0].legend(ncol=3,fontsize=7);axes[-1].set_xlabel('Elapsed minutes')
    fig.suptitle('Synthetic coupled duty — executed traces; uncalibrated equipment maps')
    fig.tight_layout();fig.savefig(folder/'coupled-duty.png',dpi=110);plt.close(fig)
    # A real trace animation, clearly labelled as a plot, not physical train motion.
    binary=shutil.which('ffmpeg')
    if not binary:return dict(state='hold',reason='ffmpeg unavailable')
    nominal=cases[0]['trace'];adverse=next(c for c in cases if c['fault']=='cooling-loss')['trace']
    with tempfile.TemporaryDirectory(prefix='.trace-',dir=folder) as tmp:
        tmp=Path(tmp)
        for frame in range(24):
            end=max(1,round(len(nominal)*(frame+1)/24));fig,ax=plt.subplots(figsize=(8,4.5),dpi=80)
            for trace,label in ((nominal,'Nominal cooling'),(adverse,'Cooling loss')):
                ax.plot([r['time_s']/60 for r in trace[:end]],[r['cabin_c'] for r in trace[:end]],label=label)
            ax.set(xlim=(0,20),ylim=(20,65),xlabel='Minutes',ylabel='Cabin °C',title='Executed synthetic thermal trace — no physical correlation')
            ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(tmp/f'{frame:03d}.png');plt.close(fig)
        command=[binary,'-loglevel','error','-y','-framerate','6','-i',str(tmp/'%03d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(folder/'coupled-duty.mp4')]
        subprocess.run(command,check=True,timeout=60,capture_output=True)
    return dict(state='executed',frames=24,frames_per_second=6,ffmpeg_sha256=core.sha(Path(binary).resolve()),
        scope='Animation of retained numerical traces; no geometric movement or physical simulation')


def report_html(value):
    h=lambda x:escape(str(x));lines=['<!doctype html><html lang="en"><meta charset="utf-8"><title>PDF closure work-package executions</title>',
        '<style>body{font:16px system-ui;max-width:1100px;margin:2rem auto;padding:1rem}table{border-collapse:collapse;width:100%}td,th{border:1px solid #bbb;padding:.5rem;text-align:left}img,video{max-width:100%}code{overflow-wrap:anywhere}</style>',
        '<h1>Full design closure plan — additional executed work</h1><p>Provisional digital design and numerical evidence. Complete railway design, manufacturing and physical acceptance remain open.</p>',
        '<p lang="ar" dir="rtl">تنفيذ إضافي لمهام خطة استكمال التصميم: نماذج تفصيلية ودراسات رقمية أولية. لا تمثل هذه النتائج قبولاً هندسياً نهائياً أو إذناً للتصنيع. تبقى اختبارات النماذج الأولية وتحريات التربة ومراجعة الجهات المختصة مطلوبة.</p>',
        '<p><a href="../index.html">All 88 plan tasks, requirements, source registers and external requests</a> | <a href="system-design.json">Electrical architecture and full coupled duty data</a> | <a href="parts.csv">Part-to-analysis/QA handoff</a></p>',
        '<h2>New manufactured detail</h2><table><tr><th>Family</th><th>Native state</th><th>Parts</th><th>Failed / held checks</th></tr>']
    for model in value['models']:
        kind=model['kind'];lines.append('<tr><td><a href="'+h(kind)+'/assessment.json">'+h(kind)+'</a></td><td>'+h(model['native_state'])+'</td><td>'+h(model['parts'])+'</td><td>'+h(', '.join(model['failed_checks']+model['held_checks']))+'</td></tr>')
    lines+=['</table>']
    for model in value['models']:
        kind=model['kind'];lines+=['<h3>'+h(kind)+'</h3><p>Revision <code>'+h(model['candidate_revision'])+'</code></p>',
            '<p><a href="'+h(kind)+'/candidate.json.gz">Detailed definition</a> | <a href="'+h(kind)+'/manufacturing-bom.csv">Cut/part schedule</a> | <a href="'+h(kind)+'/qa-plan.json">Unexecuted QA</a> | <a href="'+h(kind)+'/inspection.svg">Unissued inspection drawing</a></p>']
        if model['native_state']=='passed':lines+=['<img src="'+h(kind)+'/overview.png" alt="Native detail geometry"><p><a href="'+h(kind)+'/native/candidate.FCStd">Editable FreeCAD</a> | <a href="'+h(kind)+'/model.step.gz">STEP</a> | <a href="'+h(kind)+'/bim/assembly.ifc">Native-derived IFC</a></p>']
        if model.get('motion_preview',{}).get('state')=='executed':
            lines+=['<video controls preload="metadata" src="'+h(kind)+'/fixture-motion.mp4"></video><p>Native triangles move through the proposed fixture path. This is a rigid kinematic illustration with declared groups detached; contact forces, flexible services and actual vehicle access remain unverified.</p>']
    lines+=['<h2>Coupled electrical, HVAC and battery duty</h2><p>'+h(len(value['duty_cases']))+' executed cases, with an independent RC control and time refinement. Synthetic battery/HVAC parameters test numerical behaviour; no supplier performance or comfort qualification is claimed.</p>',
        '<img src="coupled-duty.png" alt="Executed temperature, SOC and power traces">']
    if value['media']['state']=='executed':lines+=['<video controls preload="metadata" src="coupled-duty.mp4"></video>']
    lines+=['<table><tr><th>Case</th><th>Final cabin °C</th><th>Final SOC</th><th>Executed horizon</th><th>Numerical failures</th></tr>']
    for case in value['duty_cases']:lines+=['<tr><td>'+h(case['fault'])+'</td><td>'+h(round(case['final']['cabin_c'],3))+'</td><td>'+h(round(case['final']['soc'],5))+'</td><td>'+h(case['elapsed_s'])+' s</td><td>'+h(', '.join(case['failed_checks']))+'</td></tr>']
    lines+=['</table><p>Conservation passing does not establish passenger comfort or equipment fitness. Cooling-loss and hot-start temperatures remain visible in the retained results.</p></html>']
    return '\n'.join(lines)


def build(prepared,folder):
    from . import cassette_detail,cassette_duty,civil_detail,structural_bay,workflow
    folder=Path(folder);folder.mkdir(parents=True)
    if list(folder.iterdir()):raise ValueError('new companion study directory required')
    policy=prepared['policy'];system=system_design.report();core.write(folder/'system-design.json',system)
    base=_candidate(policy,'service-cassette')
    cassette_variants=[]
    for gap,float_m,compression in itertools.product((.003,.006,.009),(.001,.006),(.15,.25)):
        item=cassette_detail.build(policy,base,guide_clearance_m=gap,connector_float_m=float_m,seal_compression=compression)
        cassette_variants.append((item,cassette_detail.evaluate(policy,item)))
    kit=civil_kit.build(civil_kit.defaults())
    cassette_pair,cassette_model,cassette_diagnostics=confirm_alternatives(cassette_variants,folder)
    # Pass actual detailed mass into the shared reaction ledger before civil
    # variants are assessed; the original planning train definition is retained.
    provisional_context=installed_context(policy,cassette_pair[0],kit)
    envelope=provisional_context['force_ledger']
    civil_variants=[]
    for variables in civil_detail.candidates():
        item=civil_detail.build(policy,kit,variables=variables)
        civil_variants.append((item,civil_detail.evaluate(item,envelope)))
    structural_variants=[]
    for variables in models.candidates(policy,'structural-bay'):
        item=structural_bay.build(policy,variables)
        structural_variants.append((item,structural_bay.evaluate(policy,item)))
    pairs=[cassette_pair,_choose(civil_variants),_choose(structural_variants)]
    variants=[dict(candidate=candidate,assessment=assessment) for candidate,assessment in cassette_variants+civil_variants+structural_variants]
    (folder/'variant-evidence.json.gz').write_bytes(gzip.compress(core.encoded(variants),mtime=0))
    search=dict(schema='osr-bounded-detail-variation/1',
        variant_count=len(variants),seed=None,policy='Finite controlled grammar; reject known failures, minimise held-count then represented detail mass; no unknown-cost credit',
        variants=[dict(kind=v['candidate']['kind'],revision=v['candidate']['revision'],variables=v['candidate']['variables'],
            mass_kg=sum(p['properties']['mass_kg'] for p in v['candidate']['contract']['parts']),
            failed_checks=v['assessment']['failed_checks'],held_checks=v['assessment']['held_checks']) for v in variants],
        scope='Final exhibits retain explicit native states; research eligibility requires passed confirmation and no implemented failure. Other variants have analytical/geometry-definition checks only. The 24 structural variants repeat the regular campaign domain and are not additional unique designs. Detail mass is not complete installed civil mass.',**core.FLAGS)
    models_out=[cassette_model];native_diagnostics=list(cassette_diagnostics)
    for index,choices in enumerate((civil_variants,structural_variants),start=1):
        pair,result,failed=confirm_alternatives(choices,folder)
        pairs[index]=pair;models_out.append(result);native_diagnostics.extend(failed)
    final_context=provisional_context
    core.write(folder/'installed-context.json',final_context)
    core.write(folder/'civil-context.json',dict(reaction_envelope=envelope,kit_revision=core.digest(kit)))
    search['exhibit_revisions']=[candidate['revision'] for candidate,_ in pairs]
    search['eligible_research_revisions']=[m['candidate_revision'] for m in models_out if m['eligible_for_research']]
    core.write(folder/'search.json',search)
    core.write(folder/'cassette-transient-duty.json',cassette_duty.campaign(candidate=pairs[0][0]))
    # Cross-discipline handoff is generated from the same exact part definitions.
    (folder/'parts.csv').write_text(handoff(pairs))
    core.write(folder/'prototype-test-requests.json',requests(prepared['prototype'],pairs))
    media=_duty_media(system,folder)
    value=dict(schema='osr-closure-companion-studies/1',epoch=core.digest(prepared),sources_sha256=prepared['source_sha256'],
        system_revision=system['revision'],models=models_out,native_diagnostics=native_diagnostics,media=media,detail_variants=search['variant_count'],
        duty_cases=[{k:c[k] for k in ('fault','elapsed_s','final','failed_checks','held_checks','revision')} for c in system['duty_cases']],
        circuit=system['circuit'],refinement=system['refinement'],engineering_closed_tasks=0,**core.FLAGS)
    core.write(folder/'summary.json',value);(folder/'index.html').write_text(report_html(value))
    if prepared['source_sha256']!=baseline.sources():raise ValueError('sources changed during companion studies')
    if core._size(folder)>MAX_BYTES:raise ValueError('companion evidence size budget exceeded')
    workflow.seal(folder,dict(schema='osr-closure-studies-receipt/1',epoch=core.digest(prepared),system_revision=system['revision']))
    verify(folder,prepared);return value


def verify(folder,prepared):
    from . import workflow
    folder=Path(folder);receipt=workflow.verify_folder(folder,dict(schema='osr-closure-studies-receipt/1',epoch=core.digest(prepared)))
    if core._size(folder)>MAX_BYTES:raise ValueError('companion evidence size budget exceeded')
    value=core.read(folder/'summary.json',maximum=20_000_000)
    if value['epoch']!=receipt['epoch'] or value['sources_sha256']!=prepared['source_sha256']:
        raise ValueError('companion source epoch differs')
    if any(value.get(k) is not False for k in core.FLAGS) or value['engineering_closed_tasks']!=0:
        raise ValueError('companion studies cannot assert engineering acceptance')
    system=core.read(folder/'system-design.json',maximum=20_000_000)
    if system['revision']!=core.digest({k:v for k,v in system.items() if k!='revision'}) or system['revision']!=value['system_revision']:
        raise ValueError('coupled study revision differs')
    if any(system.get(k) is not False for k in core.FLAGS):raise ValueError('coupled studies cannot assert release')
    system_design.validate_architecture(system['electrical'])
    expected_cases=[]
    for case in system['duty_cases']:
        if any(case.get(k) is not False for k in core.FLAGS):raise ValueError('duty case cannot assert release')
        if case['revision']!=core.digest({k:v for k,v in case.items() if k!='revision'}):raise ValueError('duty case revision differs')
        if set(case['failed_checks'])!={k for k,v in case['checks'].items() if v is False} or set(case['held_checks'])!={k for k,v in case['checks'].items() if v is None}:
            raise ValueError('coupled mandatory checks differ')
        expected_cases.append({k:case[k] for k in ('fault','elapsed_s','final','failed_checks','held_checks','revision')})
    if value['duty_cases']!=expected_cases or value['refinement']!=system['refinement'] or value['circuit']!=system['circuit']:
        raise ValueError('displayed coupled duty differs')
    variants=json.loads(gzip.decompress((folder/'variant-evidence.json.gz').read_bytes()))
    search=core.read(folder/'search.json',maximum=20_000_000)
    if any(search.get(k) is not False for k in core.FLAGS):raise ValueError('search cannot assert release')
    expected_variants=[]
    for variant in variants:
        candidate=variant['candidate'];assessment=variant['assessment']
        if any(item.get(k) is not False for item in (candidate,assessment) for k in core.FLAGS):raise ValueError('retained variant asserts unsupported release')
        if candidate['revision']!=assessment['candidate_revision']:raise ValueError('variant assessment revision differs')
        if set(assessment['failed_checks'])!={k for k,v in assessment['checks'].items() if v is False} or set(assessment['held_checks'])!={k for k,v in assessment['checks'].items() if v is None}:
            raise ValueError('variant failure/hold classification differs')
        expected_variants.append(dict(kind=candidate['kind'],revision=candidate['revision'],variables=candidate['variables'],
            mass_kg=sum(p['properties']['mass_kg'] for p in candidate['contract']['parts']),
            failed_checks=assessment['failed_checks'],held_checks=assessment['held_checks']))
    if search['variants']!=expected_variants or search['variant_count']!=len(variants) or value['detail_variants']!=len(variants):
        raise ValueError('displayed variant search differs')
    if search['exhibit_revisions']!=[m['candidate_revision'] for m in value['models']]:raise ValueError('exhibit variant revisions differ')
    if search['eligible_research_revisions']!=[m['candidate_revision'] for m in value['models'] if m['eligible_for_research']]:
        raise ValueError('native-confirmed eligible variants differ')
    for diagnostic in value['native_diagnostics']:
        path=diagnostic['path']
        if Path(path).is_absolute() or '..' in Path(path).parts or not path.startswith('failed-native/'):
            raise ValueError('unsafe native diagnostic path')
        result=diagnostic['result'];retained=core.read(folder/path/'result.json')
        if result!=retained or result['native_state']!='failed' or result['eligible_for_research'] is not False:
            raise ValueError('failed native attempt promoted or changed')
        if any(result.get(k) is not False for k in core.FLAGS):raise ValueError('native diagnostic asserts release')
        candidate=json.loads(gzip.decompress((folder/path/'candidate.json.gz').read_bytes()));assessment=core.read(folder/path/'assessment.json')
        if not any(v['candidate']==candidate and v['assessment']==assessment for v in variants):raise ValueError('native diagnostic differs from archived variant')
        if core.read(folder/path/'definition.json')!=candidate['contract']:raise ValueError('native diagnostic definition differs')
        if result['candidate_revision']!=candidate['revision'] or result['kind']!=candidate['kind'] or result['parts']!=len(candidate['contract']['parts']):
            raise ValueError('native diagnostic identity/count differs')
    pairs=[]
    for model in value['models']:
        if Path(model['kind']).name!=model['kind']:raise ValueError('unsafe family path')
        root=folder/model['kind'];candidate=json.loads(gzip.decompress((root/'candidate.json.gz').read_bytes()))
        result=core.read(root/'result.json');assessment=core.read(root/'assessment.json',maximum=20_000_000)
        if not any(v['candidate']==candidate and v['assessment']==assessment for v in variants):raise ValueError('exhibit differs from archived variant')
        pairs.append((candidate,assessment))
        if any(item.get(k) is not False for item in (candidate,assessment,model) for k in core.FLAGS):
            raise ValueError('detail cannot assert physical/design release')
        if candidate['revision']!=model['candidate_revision'] or result!=model or core.read(root/'definition.json')!=candidate['contract']:
            raise ValueError('manufactured detail identity differs')
        if model['kind']!=candidate['kind'] or model['parts']!=len(candidate['contract']['parts']) or model['scope']!=candidate['source_scope']:
            raise ValueError('displayed detail scope or count differs')
        if assessment['candidate_revision']!=candidate['revision']:raise ValueError('detail assessment revision differs')
        checks=assessment['checks'];failed=[k for k,v in checks.items() if v is False];held=[k for k,v in checks.items() if v is None]
        if set(model['failed_checks'])!=set(failed) or set(model['held_checks'])!=set(held):raise ValueError('detail mandatory failures/holds differ')
        if model['eligible_for_research']!=(model['native_state']=='passed' and not failed):raise ValueError('failed detail promoted')
        if core.read(root/'qa-plan.json')!=candidate['qa_plan']:raise ValueError('QA handoff differs')
        with tempfile.TemporaryDirectory(prefix='osr-study-handoff-') as temporary:
            workflow.tables(candidate,Path(temporary))
            for name in ('manufacturing-bom.csv','inspection.svg'):
                if (Path(temporary)/name).read_bytes()!=(root/name).read_bytes():raise ValueError('manufacturing BOM/drawing differs')
        if 'structural-detail' in assessment.get('supplemental_evidence',{}):
            detail=assessment['supplemental_evidence']['structural-detail']
            if core.read(root/'structural-detail.json')!=detail or core.read(root/'manufacturing-pack.json')!=detail['manufacturing_pack']:
                raise ValueError('structural manufacturing handoff differs')
        if model['native_state']=='passed':
            proof=core.read(root/'native/native-cad.json',maximum=10_000_000)
            if proof!=model['native_proof'] or proof['input_sha256']!=core.digest(candidate['contract']):raise ValueError('detail native proof differs')
            if any(proof.get(k) is not True for k in ('physical_ids_preserved','native_reopened','step_volume_reconciled','manufacturing_unit_ids_preserved')):
                raise ValueError('failed native correspondence cannot support a research exhibit')
            from hashlib import sha256
            if proof['files_sha256']['candidate.FCStd']!=core.sha(root/'native/candidate.FCStd') or proof['files_sha256']['candidate.step']!=sha256(gzip.decompress((root/'model.step.gz').read_bytes())).hexdigest():
                raise ValueError('detail native/STEP bytes differ')
            from . import bim
            check=bim.verify(candidate,root/'bim/assembly.ifc',ids_path=root/'bim/requirements.ids')
            if check['state']!='information-pass' or core.read(root/'bim/ids-report.json')!=check:
                raise ValueError('detail IFC/IDS differs from candidate')
            verify_exchange_mesh(candidate,root/'bim')
            motion=model.get('motion_preview',{})
            if motion.get('state')=='executed' and (motion['candidate_revision']!=candidate['revision'] or motion['native_mesh_sha256']!=core.sha(root/'bim/native-mesh.json')):
                raise ValueError('fixture motion source differs')
    if (folder/'parts.csv').read_bytes()!=handoff(pairs).encode():raise ValueError('part handoff differs')
    civil_context=core.read(folder/'civil-context.json',maximum=20_000_000);envelope=civil_context['reaction_envelope']
    civil_candidate,civil_assessment=pairs[1]
    if envelope['revision']!=core.digest({k:v for k,v in envelope.items() if k!='revision'}) or civil_context['kit_revision']!=envelope['kit_revision']:
        raise ValueError('civil reaction context revision differs')
    if civil_candidate['source_kit_revision']!=envelope['kit_revision'] or civil_assessment['reaction_revision']!=envelope['revision'] or civil_candidate['source_unit']['revision']!=envelope['unit_revisions'].get(civil_candidate['source_unit']['id']):
        raise ValueError('civil manufactured detail/reaction binding differs')
    installed=core.read(folder/'installed-context.json',maximum=20_000_000)
    if installed['revision']!=core.digest({k:v for k,v in installed.items() if k!='revision'}) or installed['candidate_revision']!=pairs[0][0]['revision'] or installed['force_ledger']!=envelope:
        raise ValueError('installed mass/reaction context differs')
    from . import integration
    candidate=pairs[0][0];parts=[p for p in candidate['contract']['parts'] if p['id'] in candidate['metadata']['cassette_installed_part_ids']]
    mass=integration.mass_properties(parts,installed['allocations'])
    if mass!=installed['gross_added_properties'] or len(installed['allocations'])!=6 or installed['installed_part_ids']!=[p['id'] for p in parts]:
        raise ValueError('installed part mass/CG/inertia differs')
    expected_masses=[v+mass['mass_kg'] for v in baseline.facts(prepared['policy'])['train.mass_cases']]
    if installed['train']['mass_cases_kg']!=expected_masses or envelope['train_revision']!=installed['train']['revision'] or envelope['seat_revision']!=installed['seat']['revision']:
        raise ValueError('installed load source revisions differ')
    if installed['removal_credit_kg']!=0. or installed['admitted_for_system_simulation'] is not False or any(installed.get(k) is not False for k in core.FLAGS):
        raise ValueError('installed gross sensitivity asserts unsupported release/admission')
    if core.read(folder/'prototype-test-requests.json',maximum=20_000_000)!=requests(prepared['prototype'],pairs):
        raise ValueError('prototype request identity or scope differs')
    transient=core.read(folder/'cassette-transient-duty.json',maximum=20_000_000)
    if transient['candidate_revision']!=pairs[0][0]['revision'] or any(transient.get(k) is not False for k in core.FLAGS):
        raise ValueError('cassette transient duty identity/scope differs')
    if set(transient['failed_checks'])!={k for k,v in transient['checks'].items() if v is False} or set(transient['held_checks'])!={k for k,v in transient['checks'].items() if v is None}:
        raise ValueError('cassette transient duty classification differs')
    if (folder/'index.html').read_text()!=report_html(value):raise ValueError('companion presentation differs')
    return value


def run(workspace,epoch,prepared):
    """Single owned epoch product; interrupted attempts preserved for inspection."""
    destination=Path(workspace)/'epochs'/epoch/'closure-studies'
    if destination.exists():return verify(destination,prepared)
    attempt=destination.with_name('closure-studies-attempt')
    if attempt.exists():
        previous=attempt.with_name('closure-studies-interrupted')
        if previous.exists():raise ValueError('companion studies interrupted twice; retained attempts require review')
        attempt.rename(previous)
    value=build(prepared,attempt);attempt.rename(destination);return value
