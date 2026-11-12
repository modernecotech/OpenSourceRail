"""Parameterized wheel-candidate native fixture; retained v1 input is untouched.

Only the source compiler reads an original engineering proposal. The disposable
site receives its sealed context, real controlled artifact bytes and one exact
documented component. Fixture transactions cannot accept a railway physically.
"""
from copy import deepcopy
from hashlib import sha256
import gzip
from io import BytesIO
import json
from pathlib import Path
import sys

from contracts import FLAGS, REQUIRED, digest

REQUIRED = REQUIRED | {'controlled-drawing-review', 'source-price-quantity-parity',
    'wrong-revision-no-issue', 'wrong-serial-no-issue', 'latest-inspection-hold',
    'counted-occurrence-binding'}


def load_input(root, review_pack, proposal, component_id):
    root=Path(root);sys.path.insert(0,str(root))
    from engineering.pilot_delivery import review
    folder=Path(review_pack).absolute()
    pack=json.loads(review.ordinary(folder,'review-pack.json',maximum=review.contract.MAX_PACK_BYTES).read_bytes())
    review.verify_artifacts(pack,folder)
    proposal=Path(proposal)
    if proposal.is_symlink() or not proposal.is_file():raise ValueError('Ordinary sealed source proposal required')
    raw=proposal.read_bytes()
    if not 0<len(raw)<=review.contract.MAX_PACK_BYTES:raise ValueError('Bounded sealed proposal required')
    expanded=gzip.GzipFile(fileobj=BytesIO(raw)).read(64*1024**2+1) if proposal.suffix=='.gz' else raw
    if len(expanded)>64*1024**2:raise ValueError('Source proposal exceeds the 64 MiB native fixture budget')
    source=json.loads(expanded)
    for name,want in source['source_sha256'].items():
        if sha256(review.ordinary(root,name,maximum=64*1024**2).read_bytes()).hexdigest()!=want:raise ValueError('Current proposal source changed: '+name)
    context=review.source_context(source,city=pack['city'],project='UNPROVISIONED-SIM-PROJECT',company='UNPROVISIONED-SIM-COMPANY')
    review.contract.bind_pack(pack,context)
    component=next((c for c in pack['components'] if c['source_part']['id']==component_id),None)
    if component is None:raise ValueError('Explicit documented source component required')
    if not component['source_part']['serial_plan']['occurrence_pattern_ids']:raise ValueError('Explicit counted source installation pattern required')
    if review.contract.UNIT_MAP[component['source_part']['unit']]!='Nos':
        raise ValueError('Serial lifecycle fixture requires one discrete source workpiece, not an inferred length or mass')
    value=dict(schema='osr-v06-platform-fixture/2',environment='simulation',city=pack['city'],
        identities=pack['identities'],review_pack=pack,source_context=context,component_id=component_id,
        source_occurrence=component['source_part'],source_occurrence_sha256=component['source_part_sha256'],
        artifact_inventory=pack['artifacts'],proposal_file_sha256=sha256(raw).hexdigest(),
        scope='One source component lifecycle; whole-train coverage remains the exact controlled document coverage',**FLAGS)
    value['input_id']=digest(value)
    return validate_input(value)


def contract_module():
    # The module is installed in the disposable native app. Unit/preflight runs
    # use the same repository implementation without importing Frappe.
    try:
        from osr_erpnext import candidate_delivery_contract
        return candidate_delivery_contract
    except ModuleNotFoundError:
        import importlib.util
        root=Path(__file__).resolve().parents[3]
        path=root/'deployment/erpnext/apps/osr_erpnext/osr_erpnext/candidate_delivery_contract.py'
        spec=importlib.util.spec_from_file_location('candidate_fixture_contract',path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def validate_input(value):
    c=contract_module()
    if value.get('source_kind','part')!='part':raise ValueError('Native v2 fixture admits one documented part only; assembly lifecycle is not native-qualified')
    if value.get('schema')!='osr-v06-platform-fixture/2' or value.get('environment')!='simulation':raise ValueError('Explicit wheel simulation fixture required')
    if value.get('input_id')!=digest({k:v for k,v in value.items() if k!='input_id'}):raise ValueError('Fixture input changed')
    c.flags(value);pack=c.validate_pack(value['review_pack'])
    if len(pack['components'])>12 or sum(r['bytes'] for r in pack['artifacts'])>64*1024**2:raise ValueError('Native fixture bounded to twelve documented components and 64 MiB artifacts; retain whole-source coverage')
    context=c.validate_context(value['source_context']);c.bind_pack(pack,context)
    component=next((p for p in pack['components'] if p['source_part']['id']==value['component_id']),None)
    if (component is None or value['identities']!=pack['identities'] or value['city']!=pack['city'] or
            value['source_occurrence']!=component['source_part'] or value['source_occurrence_sha256']!=component['source_part_sha256'] or
            value['artifact_inventory']!=pack['artifacts']):raise ValueError('Exact candidate, component and artifact inventory required')
    return value


def project_context(value, *, project, company):
    validate_input(value);c=contract_module();context=deepcopy(value['source_context'])
    context.update(project=project,company=company);context.pop('sha256')
    return c.validate_context(c.seal(context))


def verify_result(result,current_input,sources):
    validate_input(current_input);c=contract_module()
    if (result.get('schema')!='osr-v06-native-platform-result/2' or result.get('execution')!='executed' or
            result.get('input_id')!=current_input['input_id'] or result.get('source_sha256')!=sources or
            result.get('identities')!=current_input['identities']):raise ValueError('Exact executed candidate/source receipt required')
    c.flags(result)
    if result.get('checks')!={key:True for key in sorted(REQUIRED)} or result.get('uncovered'):
        raise ValueError('Incomplete native acceptance checks')
    if result.get('cleanup',{}).get('verified') is not True:raise ValueError('Verified owned-resource teardown required')
    if result.get('document_coverage')!=current_input['review_pack']['coverage']:raise ValueError('Partial document scope cannot become whole-train coverage')
    status=result.get('candidate_mapping',{});lifecycle=result.get('candidate_lifecycle',{})
    c.flags(status);c.flags(lifecycle)
    if status.get('pack_sha256')!=current_input['review_pack']['sha256'] or status.get('state')!='reviewed-native-business-mapping':
        raise ValueError('Source-bound native mapping required')
    if lifecycle.get('state')!='simulation-business-reviewed' or lifecycle.get('physical_handback_required') is not True:
        raise ValueError('Reviewed software handback and retained physical hold required')
    handback=result.get('business_review',{});c.sealed(handback);c.flags(handback)
    observed=handback['native_readback'];actor=handback['authenticated_actor']
    context=project_context(current_input,project=lifecycle['project'],company=status['applied']['company'])
    applied=c.sealed(status['applied']);c.flags(applied)
    if applied['context_sha256']!=context['sha256'] or applied['pack_sha256']!=current_input['review_pack']['sha256']:
        raise ValueError('Applied native source binding differs')
    parts={r['source_part']['id']:r for r in current_input['review_pack']['components']}
    if {r['part_id'] for r in applied['components']}!=set(parts):raise ValueError('Native mapped component coverage differs')
    for row in applied['components']:
        source=parts[row['part_id']];part=source['source_part'];unit_price=part['counted_direct_parts_process_usd_per_train']['base']/part['quantity_per_train']
        if (row['quantity_per_train']!=part['quantity_per_train'] or row['quantity_project']!=part['quantity_project'] or
                row['source_unit']!=part['unit'] or row['source_direct_usd_per_unit']!=unit_price or row['documents']!=source['documents'] or
                row['native_direct_process_allowance_usd_per_unit']!=(source['conversion']['direct_process_allowance_usd'] or 0.) or
                row['native_stock_usd_per_unit']!=sum(s['quantity']*s['rate'] for s in source['stock_lines'])):
            raise ValueError('Native quantity, source price or controlled document differs')
    c.business_handback(context,observed,actor=actor)
    records=result.get('native_records',[]);by={(r['doctype'],r['name']):r for r in records}
    required={'BOM','Item','Routing','Workstation','Operation','Purchase Order','Purchase Receipt','Quality Inspection','Asset','Issue','Asset Repair','Task','Training Program','Work Order','Stock Entry','Serial No','File','Serial and Batch Bundle'}
    if not required<={r['doctype'] for r in records}:raise ValueError('Native component document chain incomplete')
    task=by.get(('Task',observed['review_task']),{});qa=by.get(('Quality Inspection',observed['latest_qa']),{})
    if (task.get('owner')!=actor or task.get('modified_by')!=actor or task.get('values',{}).get('status')!='Completed' or
            qa.get('docstatus')!=1 or qa.get('values',{}).get('status')!='Accepted' or
            qa.get('values',{}).get('inspected_by')!=observed['inspector']):raise ValueError('Authenticated task/latest inspection readback differs')
    mapped=next((r for r in status['applied']['components'] if r['part_id']==current_input['component_id']),None)
    if mapped is None or lifecycle['installation'].get('source_kind','part')!='part' or lifecycle['installation'].get('part_id')!=current_input['component_id']:raise ValueError('Native lifecycle component differs')
    if observed['installed_serial']!=lifecycle['installation']['installed_serial']:raise ValueError('Native installed serial differs')
    work=[r for r in records if r['doctype']=='Work Order'];serials=[r['name'] for r in records if r['doctype']=='Serial No']
    if (len(work)!=2 or len(set(serials))!=2 or observed['installed_serial'] not in serials or
            any(r['docstatus']!=1 or r['values'].get('produced_qty')!=1 or r['values'].get('bom_no')!=mapped['bom'] or
                r['values'].get('production_item')!=mapped['finished_item'] for r in work)):
        raise ValueError('Two actually manufactured source serials required')
    repair=by.get(('Asset Repair',observed['repair']),{})
    if repair.get('docstatus')!=1 or repair.get('values',{}).get('repair_status')!='Completed' or not repair['values'].get('custom_osr_handback_required'):
        raise ValueError('Native completed repair must retain physical handback')
    bom=by.get(('BOM',mapped['bom']),{});items=bom.get('values',{}).get('items',[])
    stock=parts[current_input['component_id']]['stock_lines']
    expected=[dict(item_code=code,qty=line['quantity'],rate=line['rate'],uom=line['uom']) for code,line in zip(mapped['raw_items'],stock)]
    if bom.get('docstatus')!=1 or items!=expected:raise ValueError('Native submitted BOM price, gross quantity or UOM differs')
    return result
