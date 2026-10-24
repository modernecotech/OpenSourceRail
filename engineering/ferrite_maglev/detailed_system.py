"""One candidate across detailed engineering, manufacturing and digital delivery.

A complete publication can contain failed designs. No mandatory failure is
promoted by a successful drawing, transaction, image or unrelated simulation.
"""
from hashlib import sha256
from pathlib import Path
import gzip
import importlib
import json
from . import model,candidate_magnetics as magnetics,candidate_economics as economics,delivery_platform as platform
ROOT=model.ROOT
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/system-detailed'
SCHEMA='osr-detailed-system-development/1'
MAX_RAW=32*1024*1024
MODULES=('candidate_native','candidate_magnetics','candidate_structures','full_dynamics','candidate_manufacturing','candidate_lifecycle','bim_field','operations_crosscheck','platform_publication','planning_ui')


def modules():return [importlib.import_module('.'+name,__package__) for name in MODULES]
def sources():
    paths={Path(__file__),ROOT/'engineering/analysis/tests/test_ferrite_maglev_detailed_system.py',*economics.source_paths()}
    for module in modules():
        paths.add(module.OUTPUT/'manifest.json')
        paths.update(module.source_paths())
    return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def reconcile(candidate,components):
    identity=candidate['configuration_sha256'];seen=[]
    for name,value in sorted(components.items()):
        if 'configuration_sha256' in value:
            if value['configuration_sha256']!=identity:raise ValueError('mixed candidate identity: '+name)
            seen.append(name)
        if any(value.get(k) is True for k in ('design_complete','physical_validation','manufacturing_release','physical_release','engineering_accepted')):raise ValueError('unaccepted development component asserted release: '+name)
    required={'candidate_native','candidate_magnetics','candidate_structures','full_dynamics','candidate_manufacturing','candidate_lifecycle','bim_field','operations_crosscheck'}
    if not required<=set(seen):raise ValueError('candidate chain lacks exact revision coverage')
    magnetic=components['candidate_magnetics'];structural=components['candidate_structures'];dynamic=components['full_dynamics'];lifecycle=components['candidate_lifecycle']
    gates=[dict(id='magnetic-static-support',passed=magnetic.get('static_comparison_pass') is True,evidence='Actual thin return-rail flux cross-section and saturation; target AW3 support must be achievable within current/material limits'),
        dict(id='magnetic-propulsion',passed=magnetic.get('propulsion_accepted_for_simulation') is True,evidence='Independent applicable field/convergence/demagnetisation evidence, not the parent model'),
        dict(id='structural-and-interface',passed=structural.get('all_implemented_screens_pass') is True,evidence='Actual body,attachment,guideway,handling and provisionalground screens'),
        dict(id='coupled-motion-and-faults',passed=dynamic.get('study_pass') is True,evidence='Actual currents,continued fault states,guidance and authority; no detection-only pass'),
        dict(id='native-candidate-delivery',passed=lifecycle.get('native',{}).get('state')=='executed-current',evidence='Exact quantitative products through source-bound native ERP/FUXA lifecycle'),
        dict(id='physical-and-manufacturing-acceptance',passed=False,evidence='Measurements,approved drawings,materials,hardware timing and independent acceptance remain required')]
    return dict(configuration_sha256=identity,identity_consistent=True,exact_revision_components=seen,gates=gates,all_required_pass=all(g['passed'] for g in gates),eligible_for_adoption=False,**platform.FLAGS)


def _json(path):
    """Bound every retained child read, including gzip expansion."""
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size>MAX_RAW:raise ValueError('bounded ordinary child payload required')
    if path.suffix=='.gz':
        with gzip.open(path,'rb') as stream:raw=stream.read(MAX_RAW+1)
    else:raw=path.read_bytes()
    if len(raw)>MAX_RAW:raise ValueError('bounded child expansion required')
    return json.loads(raw)


def _planning_summary(module):
    """Validate the retained plans without regenerating all GIS payloads."""
    module.verify(recompute=False)
    index=_json(module.OUTPUT/'index.json');rows=index['cities']
    expected={json.loads((folder/'city.json').read_bytes())['city']['slug']:folder for folder in module.folders()}
    if len(rows)!=len(expected) or {r['city'] for r in rows}!=set(expected) or index['layer_count']!=len(platform.LAYERS) or any(index.get(k) is not False for k in platform.FLAGS):raise ValueError('current planning catalogue/flags differ')
    for row in rows:
        slug=row['city'];folder=expected[slug]
        if row['plan']!='cities/'+slug+'.json.gz' or row['layers']!='layers/'+slug+'.json.gz':raise ValueError('owned city planning paths required')
        plan=platform.validate(_json(module.OUTPUT/row['plan']))
        if plan['city']!=slug or plan['revision']!=1 or plan['parent_revision_sha256'] is not None or plan['actor']!='catalogue-import' or plan['changes'] or plan['od']:raise ValueError('current unedited catalogue plan required')
        network=next(iter(sorted(folder.glob('*.corridor.geojson'))),None)
        if network is None:raise ValueError('current planning alignment required')
        expected_sources={p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in (folder/'city.json',network,folder/'engineering/maglev/summary.json')}
        if plan['source_sha256']!=expected_sources or row['revision_sha256']!=plan['revision_sha256'] or row['lines']!=len(plan['lines']) or row['stops']!=sum(len(line['stops']) for line in plan['lines']):raise ValueError('retained planning revision/source/count differs')
    return dict(cities=len(rows),layers=len(platform.LAYERS),interactive_proposals=True,generic_delivery_adapter=True,complete_cost_known=False,**platform.FLAGS)


def verified_components():
    """Use real child verifiers; never promote a self-consistent summary alone.

    The four engineering read_summary APIs validate their payloads internally.
    Other summaries are derived only after their actual verifier succeeds.
    No reader executes a simulation, browser, Docker or full GIS regeneration.
    """
    values={};receipts={}
    for name,module in zip(MODULES,modules()):
        receipt_path=module.OUTPUT/'manifest.json';_json(receipt_path);before=sha256(receipt_path.read_bytes()).hexdigest()
        if name=='platform_publication':value=_planning_summary(module)
        elif hasattr(module,'read_summary'):value=module.read_summary()
        else:
            checked=module.verify()
            if name=='candidate_lifecycle':value=_json(module.OUTPUT/'study.json.gz')
            elif name=='candidate_manufacturing':
                p=_json(module.OUTPUT/'study.json.gz')['lifecycle_package'];value=dict(configuration_sha256=p['configuration_sha256'],products=[dict(product_id=r['product_id'],revision_sha256=r['product_revision_sha256'],rows=len(r['bom']),cost_usd=r['estimated_material_process_cost_usd']) for r in p['products']],**platform.FLAGS)
            elif name=='bim_field':
                r=_json(module.OUTPUT/'study.json.gz');value=dict(configuration_sha256=r['configuration_sha256'],ifc_parts=len(r['exchange']['parts']),ids_pass=r['exchange']['ids_pass'],bcf_version=r['bcf']['version'],field_state=r['field_result']['state'],study_pass=r['study_pass'],**platform.FLAGS)
            elif name=='operations_crosscheck':
                r=_json(module.OUTPUT/'study.json.gz');value=dict(configuration_sha256=r['configuration_sha256'],scenarios=len(r['scenarios']),study_pass=r['study_pass'],scope=r['scenarios'][0]['scope'],**platform.FLAGS)
            else:value=checked
        if sha256(receipt_path.read_bytes()).hexdigest()!=before:raise ValueError('child receipt changed during verification')
        receipts[name]=before
        values[name]=value
    if set(values)!=set(MODULES):raise ValueError('complete verified component chain required')
    return values,receipts


def _finance_invariant(value,identity):
    if value.get('configuration_sha256')!=identity or any(value.get(k) is not False for k in platform.FLAGS):raise ValueError('economics candidate/release differs')
    finance=value.get('whole_pilot_finance',{})
    if any(finance.get(k,'missing') is not None for k in ('capex_usd','annual_opex_usd','dscr')) or finance.get('financial_close') is not False:raise ValueError('unqualified candidate finance must remain null and unclosed')


def study():
    values,receipts=verified_components()
    candidate=magnetics.definition();chain=reconcile(candidate,values)
    costs=economics.study();_finance_invariant(costs,candidate['configuration_sha256'])
    return dict(schema=SCHEMA,configuration_sha256=candidate['configuration_sha256'],parent_configuration_sha256=candidate['parent_configuration_sha256'],
        controlled_tare_kg_per_car=candidate['controlled_tare_kg'],controlled_aw3_kg_per_car=candidate['controlled_aw3_kg'],cars=candidate['cars'],
        components=values,component_receipt_sha256=receipts,chain=chain,economics=costs,
        scope='Completed bounded digital development and simulation publication, including rejected designs. A complete physically qualified train/civil/software system has NOT been reached.',
        unresolved_system_designs=['Static lift: actual25mm return-rail flux area saturates before required AW3 support','Propulsion topology and refined demagnetisation/convergence','Joined carbody/splices,braking/capture interfaces and fatigue/crash','Rigid magnetic array versus terminal curvature and route recovery','Full four-stop motion/dwell/charging and fleet dispatch with qualified useful-field maps','Detailed electrical protection/PCB/insulation/thermal/hardware timing','Geotechnical foundation,station/depot/fire/evacuation and physical construction stages','Complete installed cost,local origin,verified demand and financing commitments'],**platform.FLAGS)


def readme(value):
    lines=['# Detailed candidate and system simulation','',value['scope'],'',
        f'Exact candidate `{value["configuration_sha256"]}`: **{value["controlled_tare_kg_per_car"]/1000:.3f}t tare and {value["controlled_aw3_kg_per_car"]/1000:.3f}t AW3 per car**, six cars. Geometry-derived equipment is counted; the old94ad actuator pass is a separate configuration.',
        '', '| Development chain | Result |','|---|---|']
    for gate in value['chain']['gates']:lines.append(f'| {gate["id"]} | {"Implemented screens passed" if gate["passed"] else "OPEN / FAILED"}: {gate["evidence"]} |')
    lines+=['','## Engineering and delivery packets','']
    for module in modules():lines.append(f'- [{module.OUTPUT.name}](../{module.OUTPUT.name}/README.md) — exact source receipt and retained results.')
    lines+=['','The candidate has a complete traced publication chain, not a completed engineering design. Failed field, structural or dynamic evidence blocks adoption even when BIM, purchasing or independent operations tests pass. No file or software-business result grants manufacturing or physical release.','',
        'The economics packet separates counted material/process subtotals from complete installed price. It compares identical passenger-services assumptions on a common kinematic trajectory. The new candidate has no adopted CAPEX/OPEX/debt forecast while mandatory propulsion and full-service duty evidence fail; the earlier configuration’s finance is not relabelled.','',
        'The owner/builder [planning workspace](../../../workbench/planning/index.html) can be used for controlled proposals independently of train physical qualification. Its generic workfront schedule and native navigation do not imply whole-city BIM or full OCC/HR deployment.','',
        'Remaining engineering work:','',*[f'- {r}.' for r in value['unresolved_system_designs']], '',
        'Reproduce: `./osr design detailed-system` after the component packets. `./osr build` regenerates stale implemented studies; it does not autonomously produce physical qualification.','']
    return '\n'.join(lines)


def publish(output=OUTPUT):
    before=sources();value=study();output=Path(output);output.mkdir(parents=True,exist_ok=True)
    files={'study.json.gz':gzip.compress(platform.encoded(value),mtime=0),'economics.json':platform.encoded(value['economics']),'README.md':readme(value).encode()}
    if before!=sources():raise ValueError('detailed candidate source changed during integration')
    for n,b in files.items():(output/n).write_bytes(b)
    m=dict(schema=SCHEMA,configuration_sha256=value['configuration_sha256'],source_sha256=before,files_sha256={n:sha256(b).hexdigest() for n,b in files.items()},**platform.FLAGS);(output/'manifest.json').write_bytes(platform.encoded(m));return m


def _retained(output):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes())
    if m.get('schema')!=SCHEMA or m['source_sha256']!=sources() or any(m.get(k) is not False for k in platform.FLAGS):raise ValueError('detailed system source/release differs')
    if {p.name for p in output.iterdir()}!=set(m['files_sha256'])|{'manifest.json'}:raise ValueError('detailed system inventory differs')
    for n,h in m['files_sha256'].items():
        if (output/n).is_symlink() or not (output/n).is_file() or (output/n).stat().st_size>32*1024*1024 or sha256((output/n).read_bytes()).hexdigest()!=h:raise ValueError('detailed system bytes differ')
    with gzip.open(output/'study.json.gz','rb') as stream:raw=stream.read(32*1024*1024+1)
    if len(raw)>32*1024*1024:raise ValueError('detailed system raw bound exceeded')
    value=json.loads(raw);chain=reconcile(magnetics.definition(),value['components'])
    if value['chain']!=chain or value['configuration_sha256']!=chain['configuration_sha256'] or m.get('configuration_sha256')!=chain['configuration_sha256'] or any(value.get(k) is not False for k in platform.FLAGS):raise ValueError('detailed system candidate eligibility differs')
    _finance_invariant(value['economics'],chain['configuration_sha256'])
    # Recompute the integrated report from actual verified child payloads and
    # current economics, not from its own rehashed summaries/presentation.
    if platform.encoded(value)!=platform.encoded(study()):raise ValueError('detailed system differs from verified current child evidence/economics')
    if m['source_sha256']!=sources():raise ValueError('detailed system sources changed during verification')
    if (output/'README.md').read_text()!=readme(value) or json.loads((output/'economics.json').read_bytes())!=value['economics']:raise ValueError('detailed system presentation differs')
    return m,value


def verify(output=OUTPUT):return _retained(output)[0]
def read_summary(output=OUTPUT):
    m,value=_retained(output)
    return {k:value[k] for k in ('schema','configuration_sha256','controlled_tare_kg_per_car','controlled_aw3_kg_per_car','cars','chain','scope','unresolved_system_designs')}
