"""Exact dimensioned candidate in the retained native delivery contract.

Explicit native execution is separate; a read never starts Docker. Native
quantities and valuation are planning hypotheses, never supplier quotes.
"""
from hashlib import sha256
from pathlib import Path
import gzip
import json
from . import model,pilot_lifecycle as base,candidate_manufacturing as manufacturing,delivery_platform as platform
ROOT=model.ROOT
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/candidate-lifecycle'
RAW=ROOT/'engineering/assurance/v053-candidate-lifecycle-native'
FLAGS=base.FLAGS
encoded=base.encoded
planning_bundle=base.planning_bundle
supervisory_package=base.supervisory_package
fuxa_project=base.fuxa_project
lifecycle_package=manufacturing.lifecycle_package
SCHEMA='osr-candidate-native-lifecycle/1'


def source_paths():return sorted({Path(__file__),ROOT/'engineering/analysis/tests/test_ferrite_maglev_candidate_lifecycle.py',*manufacturing.source_paths(),*base.source_paths()})
def native_sources():return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in source_paths()}
def sources():return native_sources()


def verify_native(raw=RAW):
    package=lifecycle_package();m=base.verify_native(raw,package=package,source_sha256=native_sources());value=json.loads((Path(raw)/'native-result.json').read_bytes());records={(r['doctype'],r['name']):r for r in value['native_documents']}
    from osr_erpnext.maglev_manufacturing import stock_lines
    for product,row in zip(package['products'],value['products']):
        wanted=stock_lines(product);actual=row.get('quantified_materials')
        if actual is None or row['manufacturing_mode']!='quantified-candidate' or [{k:v for k,v in a.items() if k!='item_code'} for a in actual]!=wanted:raise ValueError('native quantified material definition differs')
        for dt,key,quantity_key in [('BOM','bom','quantity'),('Purchase Order','purchase_order','purchase_quantity'),('Purchase Receipt','receipt','purchase_quantity')]:
            doc=records.get((dt,row[key]),{});items=doc.get('values',{}).get('items',[])
            if doc.get('docstatus')!=1 or len(items)!=len(actual):raise ValueError('native quantitative document coverage differs')
            by={x['item_code']:x for x in items}
            for material in actual:
                item=by.get(material['item_code'],{})
                if not __import__('math').isclose(item.get('qty',-1),material[quantity_key],rel_tol=1e-6) or not __import__('math').isclose(item.get('rate',-1),material['rate'],rel_tol=1e-6):raise ValueError('native quantity or rate differs from source BOM')
                if item.get('uom')!=material['uom']:raise ValueError('native stock unit differs')
        amount=records[('Asset',row['asset'])]['values']['gross_purchase_amount'];expected=sum(x['quantity']*x['rate'] for x in actual)
        if not __import__('math').isclose(amount,expected,rel_tol=1e-6,abs_tol=.011):raise ValueError('native simulated asset valuation differs')
    return m


def study():
    package=lifecycle_package();simulation=base.scenario(package)
    try:verify_native();state='executed-current';receipt=sha256((RAW/'manifest.json').read_bytes()).hexdigest()
    except (ValueError,KeyError,OSError) as error:state='hold';receipt=None;reason=str(error)
    return dict(schema=SCHEMA,configuration_sha256=package['configuration_sha256'],package_sha256=package['sha256'],products=[dict(product_id=p['product_id'],product_revision_sha256=p['product_revision_sha256'],cost_usd=p['estimated_material_process_cost_usd']) for p in package['products']],
        native=dict(state=state,receipt_sha256=receipt,reason=None if state=='executed-current' else reason),business_simulation=dict(events=len(simulation['snapshot']['events']),controls=simulation['controls']),scope='Same exact candidate and quantitative BOM through software-native delivery; physical fabrication/field acceptance remain open.',**FLAGS)


def publish(output=OUTPUT):
    before=sources();value=study();output=Path(output);output.mkdir(parents=True,exist_ok=True)
    files={'study.json.gz':gzip.compress(encoded(value),mtime=0),'README.md':('\n'.join(['# Quantified candidate native lifecycle','',f'Candidate `{value["configuration_sha256"]}`; native evidence **{value["native"]["state"]}**.','',
        'The explicit runner uses the retained authenticated ERPNext/FUXA lifecycle for the three new candidate products. Native BOM/purchase/receipt quantities, stock units, unquoted rates and simulated asset valuation must match the engineering cut-yield schedule. Original/replacement serials, failed QA/rework, independent business review, process-loss recovery and scoped permissions remain required.','',
        'Run `tools/automation/osr-python tools/automation/pilot-lifecycle-native.py run --candidate`. Verification does not contact services. The earlier base-product campaign remains separate. Neither simulated dimensional measurements nor submitted business records approve the engineering design or physical railway.',''])).encode()}
    if before!=sources():raise ValueError('candidate lifecycle sources changed')
    for n,b in files.items():(output/n).write_bytes(b)
    receipt=dict(schema=SCHEMA,source_sha256=before,files_sha256={n:sha256(b).hexdigest() for n,b in files.items()},**FLAGS);(output/'manifest.json').write_bytes(encoded(receipt));return receipt


def verify(output=OUTPUT):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes())
    if m['source_sha256']!=sources():raise ValueError('candidate lifecycle inputs stale')
    if set(p.name for p in output.iterdir())!=set(m['files_sha256'])|{'manifest.json'}:raise ValueError('candidate lifecycle inventory differs')
    for n,h in m['files_sha256'].items():
        if (output/n).is_symlink() or sha256((output/n).read_bytes()).hexdigest()!=h:raise ValueError('candidate lifecycle bytes changed')
    if encoded(json.loads(gzip.decompress((output/'study.json.gz').read_bytes())))!=encoded(study()):raise ValueError('candidate lifecycle derived state differs')
    return dict(verified=True,**FLAGS)
