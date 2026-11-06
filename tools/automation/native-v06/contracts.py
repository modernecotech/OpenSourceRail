"""Pure input/receipt boundaries for the explicit v0.6 native software campaign."""
from hashlib import sha256
from pathlib import Path
import gzip
import json

IDS = ('candidate_id', 'body_candidate_id', 'evaluation_id', 'selection_id',
       'support_component_id', 'propulsion_component_id')
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             movement_authority=False, physical_evidence=False)
REQUIRED = {'native-manufacture', 'incoming-qa-rework', 'serial-installation',
            'gateway-native-defect', 'native-repair-consumption', 'independent-business-review',
            'native-hr-training', 'permission-refusal', 'outage-replay',
            'fuxa-observation', 'no-movement-authority', 'cross-candidate-refusal'}


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def load_input(root):
    folder = Path(root) / 'docs/design-engine/current/exports'
    manifest = json.loads((folder / 'manifest.json').read_bytes())
    native_identity=sha256((json.dumps({k:v for k,v in manifest.items() if k!='manifest_id'},sort_keys=True,separators=(',', ':'),allow_nan=False)+'\n').encode()).hexdigest()
    if manifest.get('manifest_id') != native_identity:
        raise ValueError('Current export manifest identity changed')
    for name, expected in manifest['files_sha256'].items():
        path = folder / name
        if path.is_symlink() or not path.resolve().is_relative_to(folder.resolve()) or sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Current export bytes differ: ' + name)
    bom = json.loads(gzip.decompress((folder / 'engineering-bom.json.gz').read_bytes()))
    for key in IDS:
        if bom[key] != manifest[key]:
            raise ValueError('Mixed current identities: ' + key)
    if any(manifest.get(k) is not False for k in ('physical_accepted', 'engineering_accepted', 'manufacturing_release', 'operating_release')):
        raise ValueError('Only explicitly unreleased current development input is supported')
    # A source occurrence is retained whole. One Nos is a business fixture kit,
    # never an inferred purchased quantity or complete manufactured assembly.
    row = next(r for r in bom['stock_inventory_per_car'] if r.get('id') == 'retained-comfort/HVAC')
    value = dict(schema='osr-v06-platform-fixture/1', environment='simulation', city='baghdad',
                 identities={k: manifest[k] for k in IDS}, export_manifest_sha256=sha256((folder/'manifest.json').read_bytes()).hexdigest(),
                 source_bom_sha256=manifest['files_sha256']['engineering-bom.json.gz'],
                 source_occurrence=row, source_occurrence_sha256=digest(row),
                 conversion=dict(quantity=1, uom='Nos', rate=1,
                     basis='One synthetic software kit per exact retained source occurrence; USD 1 fixture rate. No purchased-stock, yield, physical manufacture or price inference.'), **FLAGS)
    value['input_id'] = digest(value)
    return value


def validate_input(value):
    if value.get('schema') != 'osr-v06-platform-fixture/1' or value.get('environment') != 'simulation':
        raise ValueError('Simulation fixture required')
    if value.get('input_id') != digest({k: v for k, v in value.items() if k != 'input_id'}):
        raise ValueError('Fixture input changed')
    if value.get('source_occurrence_sha256') != digest(value['source_occurrence']):
        raise ValueError('Source occurrence changed')
    if any(value.get(k) is not False for k in FLAGS):
        raise ValueError('Software fixture cannot grant physical authority')
    for key in IDS:
        v = value['identities'][key]
        if not isinstance(v, str) or len(v) != 64 or any(c not in '0123456789abcdef' for c in v):
            raise ValueError('Exact current identity required')
    return value


def handback_guard(expected, observed):
    """Campaign review guard, not an installed production release workflow."""
    if observed['identities'] != expected['identities'] or observed['serial'] != expected['serial']:
        raise ValueError('Exact candidate and installed serial required')
    if observed['latest_test'] != expected['latest_test'] or observed['test_status'] != 'Accepted':
        raise ValueError('Latest passing native inspection required')
    if observed['reviewer'] == observed['inspector'] or observed['reviewer'] != expected['reviewer']:
        raise ValueError('Independent named reviewer required')
    if observed['repair_status'] != 'Completed' or not observed['handback_required']:
        raise ValueError('Native repair and retained physical handback hold required')
    return dict(business_review='simulation-business-reviewed', **FLAGS)


def verify_result(result, current_input, sources):
    validate_input(current_input)
    if result.get('schema') != 'osr-v06-native-platform-result/1' or result.get('input_id') != current_input['input_id']:
        raise ValueError('Native result belongs to another input')
    if result.get('source_sha256') != sources or result.get('identities') != current_input['identities']:
        raise ValueError('Native result source/candidate differs')
    if any(result.get(k) is not False for k in FLAGS):
        raise ValueError('Native business result cannot release hardware')
    checks = result.get('checks', {})
    if set(checks) != REQUIRED or any(v is not True for v in checks.values()):
        raise ValueError('Incomplete native acceptance checks')
    if result.get('cleanup',{}).get('verified') is not True:
        raise ValueError('Native resource cleanup not verified')
    if result.get('uncovered'):
        raise ValueError('Native acceptance has uncovered checks')
    if not result.get('native_records') or result.get('execution') != 'executed':
        raise ValueError('Actual native execution and readback required')
    records=result['native_records']
    required_types={'BOM','Purchase Order','Purchase Receipt','Quality Inspection','Asset','Issue','Asset Repair','Task','Training Program','Work Order','Stock Entry','Serial No'}
    if not required_types.issubset({r.get('doctype') for r in records}):
        raise ValueError('Native document chain incomplete')
    by={(r['doctype'],r['name']):r for r in records}
    context=result['review_context'];binding=result['qa_binding']
    if context.get('mapping_identities')!=current_input['identities'] or context.get('native_inspection_order')!='creation desc, name desc':
        raise ValueError('Native candidate mapping/latest-inspection readback differs')
    task=by.get(('Task',context['task']),{});qa=by.get(('Quality Inspection',context['quality_inspection']),{})
    if task.get('modified_by')!=context['reviewer'] or context['reviewer']==context['inspector'] or task.get('values',{}).get('status')!='Completed':
        raise ValueError('Native independent reviewer readback differs')
    if qa.get('docstatus')!=1 or qa.get('values',{}).get('status')!='Accepted' or qa['values'].get('inspected_by')!=context['inspector']:
        raise ValueError('Native passing inspection readback differs')
    if binding.get('quality_inspection')!=context['quality_inspection'] or binding.get('measurement',{}).get('serial')!=context['current_serial']:
        raise ValueError('Native serial and inspection binding differs')
    repairs=[r for r in records if r['doctype']=='Asset Repair']
    work=[r for r in records if r['doctype']=='Work Order']
    serials=[r['name'] for r in records if r['doctype']=='Serial No']
    if not repairs or any(r['docstatus']!=1 or r['values'].get('repair_status')!='Completed' or not r['values'].get('custom_osr_handback_required') for r in repairs):
        raise ValueError('Native repair/physical handback hold differs')
    if len(work)!=2 or any(r['docstatus']!=1 or r['values'].get('produced_qty')!=1 for r in work) or len(set(serials))!=2 or context['current_serial'] not in serials:
        raise ValueError('Native manufacture/serial history differs')
    return result
