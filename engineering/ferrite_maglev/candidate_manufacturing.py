"""Quantified candidate procurement, cut schedules and provisional process plans.

Rates are disclosed planning inputs. Drawings, supplier selections and physical
qualification remain open; an ERP transaction cannot close an engineering hold.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import json
import math
from . import model,candidate_magnetics as magnetics,candidate_structures as structures,pilot_lifecycle as lifecycle,delivery_platform as platform

ROOT=model.ROOT
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/candidate-manufacturing'
SCHEMA='osr-candidate-manufacturing/1'
UOM={'metre':'Meter','kg allocation':'Kg','kg':'Kg','kg-processed':'Kg','coil':'Nos','m3':'Cubic Meter','unit':'Nos','m':'Meter'}
_PRODUCT_CACHE={}


def source_paths():return sorted({Path(__file__),ROOT/'engineering/analysis/tests/test_ferrite_maglev_candidate_manufacturing.py',*magnetics.source_paths(),*structures.source_paths()})
def sources():return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in source_paths()}


def validate_line(row):
    for k in ('net_quantity','purchase_quantity','waste_fraction','unit_rate_usd','extended_cost_usd'):
        if type(row[k]) not in (int,float) or not math.isfinite(row[k]) or row[k]<0:raise ValueError('nonnegative finite procurement quantity/rate required')
    if row['purchase_quantity']<=0 or row['waste_fraction']>=1 or row['uom'] not in set(UOM.values()) or not row['geometry_part_ids']:raise ValueError('positive dimensioned procurement scope required')
    if not math.isclose(row['purchase_quantity']*(1-row['waste_fraction']),row['net_quantity'],rel_tol=1e-9,abs_tol=1e-8):raise ValueError('cut yield/mass balance differs')
    if not math.isclose(row['purchase_quantity']*row['unit_rate_usd'],row['extended_cost_usd'],rel_tol=1e-9):raise ValueError('quantity/rate valuation differs')
    if row['supplier_quote'] is not None or row['purchase_release'] is not False:raise ValueError('unquoted draft procurement required')
    return row


def aggregate(rows):
    """Stock aggregation preserves all constituent net/gross/cost quantities."""
    groups={}
    for row in rows:
        validate_line(row);key=(row['component_scope'],row['uom'],row['unit_rate_usd'],row['waste_fraction'],row['process'])
        if key not in groups:groups[key]=dict(row,id='material-'+str(len(groups)+1),geometry_part_ids=[],source_lines=[],net_quantity=0.,purchase_quantity=0.,extended_cost_usd=0.,mass_kg=0.)
        g=groups[key]
        for k in ('net_quantity','purchase_quantity','extended_cost_usd','mass_kg'):g[k]+=row[k]
        g['geometry_part_ids'].extend(row['geometry_part_ids']);g['source_lines'].append(row['id'])
    return [validate_line(row) for row in groups.values()]


def _line(uid,scope,unit,net,rate,parts,process,*,waste=0.,mass=0.,lead=60,origin='Manufacturing country/supplier not confirmed',qa=None):
    gross=net/(1-waste)
    return validate_line(dict(id=uid,component_scope=scope,uom=UOM[unit],net_quantity=net,purchase_quantity=gross,waste_fraction=waste,unit_rate_usd=rate,extended_cost_usd=gross*rate,mass_kg=mass,geometry_part_ids=parts,process=process,
        lead_time_days=lead,origin_basis=origin,supplier_quote=None,purchase_release=False,qa_requirements=qa or ['material certificate','dimensional acceptance','independent review'],approved_tolerance=None))


def module_materials(candidate):
    ids={p['id'] for p in candidate['module']['parts']};rows=[]
    for row in candidate['manufacturing_bom']:
        if not set(row['geometry_part_ids'])<=ids:continue
        rows.append(_line(row['id'],row['component_scope'],row['unit'],row['net_material_quantity'],row['unit_rate_usd'],row['geometry_part_ids'],row['process'],waste=row['waste_fraction'],mass=row['mass_kg'],lead=row['lead_time_days'],origin=row['origin_basis'],qa=row['qa_requirements']))
    if not math.isclose(math.fsum(r['mass_kg'] for r in rows),candidate['module']['mass_kg'],rel_tol=1e-9):raise ValueError('module procurement net mass does not match candidate')
    return rows


def civil_materials(candidate):
    a=structures.load();rail=structures.return_rail_and_attachments(candidate);loads=structures.load_cases(candidate,structures.mass_properties(candidate));beams=structures.beam_design(candidate,loads,rail)
    beam=beams[0];rates=a['rates'];prefix=beam['id']
    rows=[_line(prefix+'/concrete','precast-concrete','m3',beam['concrete_volume_m3'],rates['concrete_usd_m3'],['civil/box','civil/end-blocks'],'mix,cast,vibrate,strength-test,controlled-cure',waste=.03,mass=beam['concrete_volume_m3']*a['concrete']['density_kg_m3'],origin='Iraqi manufacture hypothesis; mix/material sources and plant qualification open'),
        _line(prefix+'/reaction-rails','reaction-steel','kg',beam['reaction_rail_and_attachment_steel_mass_kg'],rates['fabricated_structural_steel_usd_kg'],['civil/L-rails','civil/transverse-supports'],'fabricate,coat,align,bolt; magnetic joints and anchors unqualified',waste=.08,mass=beam['reaction_rail_and_attachment_steel_mass_kg']),
        _line(prefix+'/reinforcement','reinforcement','kg',beam['reinforcement_mass_kg'],rates['fabricated_rebar_usd_kg'],['civil/rebar-cage'],'cut,bend,fix; development/end-zone approval hold',waste=.05,mass=beam['reinforcement_mass_kg']),
        _line(prefix+'/prestress','prestress','kg',beam['strand_mass_kg'],rates['prestress_strand_usd_kg'],['civil/strands'],'calibrated pretension,elongation,transfer/debond hold',waste=.04,mass=beam['strand_mass_kg']),
        _line(prefix+'/bearings','bearings','unit',4,rates['bearing_usd_unit'],['civil/bearings'],'supplier pressure,rotation,movement/fatigue qualification hold')]
    return rows,beam


def launch_materials(candidate):
    """Dimensioned coil coupon; force acceptance is a separate field-map hold."""
    a=magnetics.load();p=a['propulsion_band'];coil=magnetics.propulsion_group_definition(5.);mass=coil['copper_mass_kg']
    rows=[]
    for row in coil['manufacturing_bom']:
        parts=row['geometry_part_ids'] or ['allocated/'+row['id']]
        rows.append(_line(row['id'],row['component_scope'],row['unit'],row['net_material_quantity'],row['unit_rate_usd'],parts,row['process'],waste=row['waste_fraction'],mass=row['mass_kg'],lead=row['lead_time_days'],origin=row['origin_basis'],qa=row['qa_requirements']))
    if not math.isclose(sum(row['mass_kg'] for row in rows),coil['total_mass_kg'],rel_tol=1e-9):raise ValueError('complete source wayside-group mass differs')
    return rows,coil


def product_definition(candidate=None):
    candidate=candidate or magnetics.definition();key=platform.digest(dict(candidate=candidate,source_sha256=sources()))
    if key in _PRODUCT_CACHE:return deepcopy(_PRODUCT_CACHE[key])
    cfg=candidate['configuration_sha256'];module=module_materials(candidate);civil,beam=civil_materials(candidate);launch,coil=launch_materials(candidate)
    definitions=[('OSR-PILOT-MAGNETIC-BAY',module,candidate['module']['parts'],'magnetic bay'),('OSR-PILOT-GUIDEBEAM-25M',civil,beam,'25m guidebeam'),('OSR-PILOT-LAUNCH-GROUP-5M',launch,coil,'5m wayside winding group')];products=[]
    for uid,rows,geometry,label in definitions:
        grouped=aggregate(rows);geometry_hash=platform.digest(geometry);revision=platform.digest(dict(configuration_sha256=cfg,product_id=uid,geometry_sha256=geometry_hash,cut_schedule=rows))
        products.append(dict(product_id=uid,product_revision_sha256=revision,geometry_sha256=geometry_hash,geometry_source_ids=sorted({i for r in rows for i in r['geometry_part_ids']}),
            bom=[dict(id=r['id'],state='allocated' if 'allocated' in r['component_scope'] or 'allocation' in r['process'] else 'defined',source=r,source_sha256=lifecycle.contract.digest(r)) for r in grouped],cut_schedule=rows,
            release='draft-unqualified',cost_state='unquoted-quantitative-estimate',label=label,estimated_material_process_cost_usd=math.fsum(r['extended_cost_usd'] for r in rows),
            complete_product_cost=False,excluded_costs=['qualified detailed electronics, tooling, labour not explicitly priced, factory overhead, freight/tax, validation and warranty'],
            manufacturing_mode='quantified-candidate',physical_test_executed=False))
    value=dict(schema=SCHEMA,configuration_sha256=cfg,products=products,beam=beam,launch_coil=coil,**platform.FLAGS)
    if len(_PRODUCT_CACHE)>=4:_PRODUCT_CACHE.pop(next(iter(_PRODUCT_CACHE)))
    _PRODUCT_CACHE[key]=deepcopy(value)
    return value


def lifecycle_package():
    value=product_definition();base=deepcopy(lifecycle.load());products=value['products'];positions=base['positions']
    for pos,product in zip(positions,products):pos['product_id']=product['product_id']
    package=dict(schema=lifecycle.SCHEMA,revision='candidate-dimensioned-lifecycle-1',environment='simulation',city='baghdad',railway_family='fixed-zone-ferrite-maglev',
        configuration_id=magnetics.definition()['id'],configuration_sha256=value['configuration_sha256'],products=products,positions=positions,manufacturing_mode='quantified-candidate',**lifecycle.contract.FLAGS)
    package['sha256']=lifecycle.contract.digest(package);return lifecycle.contract.validate_package(package)


def procedures(product):
    return dict(product_id=product['product_id'],product_revision_sha256=product['product_revision_sha256'],manufacturing_release=False,
        steps=[dict(sequence=i+1,operation=op,state='unexecuted',required_evidence=evidence) for i,(op,evidence) in enumerate([
            ('Verify exact drawing/BOM revision and quarantine unapproved stock','revision,material certificates and lot identities'),('Prepare dimensioned stock from retained cut schedule','cut dimensions,kerf/waste and traceable remnants'),
            ('Manufacture subassemblies with restrained jigs and defined datum features','fixture calibration,alignment,fit-up and tool settings'),('Inspect hidden interfaces before closure','polarity/connection/embedding inspection and recorded photographs'),
            ('Complete winding/structural connections and accessible terminations','torque,polarity,resistance,insulation or strength/curing as applicable'),('Test completed unit against approved criteria','calibrated measurements; proposed tolerances remain unapproved'),
            ('Record serial,batch,mass,revision and packing/handling instructions','serial traveller,weight/CG and lifting plan'),('Install,survey and independently inspect exact interfaces','field results,independent acceptance; no automatic handback')])],
        tolerance_status='Provisional numeric study limits only; material/temperature/stack-up and process capability approval required',
        interface_study_limits=[dict(characteristic='magnetic nominal working gap',nominal=8.,plus_minus=.5,unit='mm',approved=False),dict(characteristic='removable service-path clearance',minimum=5.,unit='mm',approved=False)],
        tooling=[dict(id='restrained-magnet-assembly-jig',qualified=False),dict(id='winding-and-polarity-test-fixture',qualified=False),dict(id='dimensional-datum-and-load-test-fixture',qualified=False)],
        connector_status='Counted connector/cooling envelopes; exact current,voltage,creepage,EMC,IP,quick-disconnect and cable-bend approval open')


def study():
    value=product_definition();package=lifecycle_package();value.update(lifecycle_package=package,planning_bundle=lifecycle.planning_bundle(package),procedures=[procedures(p) for p in value['products']],
        source_consistent=True,whole_system_manufacturable=False,scope='Quantified engineering stock and native lifecycle input for three bounded units. Geometry/process proposals have unresolved structural, magnetic, electrical and physical qualification gates.')
    return value


def publish(output=OUTPUT):
    before=sources();value=study();output=Path(output);output.mkdir(parents=True,exist_ok=True)
    files={'study.json.gz':gzip.compress(platform.encoded(value),mtime=0),'lifecycle-package.json':platform.encoded(value['lifecycle_package']),'planning-bundle.json':platform.encoded(value['planning_bundle']),
        'README.md':('\n'.join(['# Quantified candidate manufacturing','',f'Exact candidate `{value["configuration_sha256"]}`. Three bounded products: magnetic module,25m guidebeam and5m wayside winding group.','',
        'Net material, purchase quantities, cut yield, waste, units, unquoted rates, valuation, lead-time hypotheses, source part IDs and process/inspection holds are preserved. Native BOM grouping sums constituent quantities; explicit native stock/currency quantisation preserves the exact engineering schedule separately; it does not substitute one USD1 kit for each part.','',
        'The launch coil is a dimensioned hypothesis. Failed or unresolved propulsion maps do not become qualified by purchasing it. Connector/cooling envelopes, fixture/tooling details, qualified tolerances, full factory labour and physical tests remain open. These are draft software-business inputs, not purchase instructions.',''])).encode()}
    if sources()!=before:raise ValueError('manufacturing sources changed during generation')
    for n,b in files.items():(output/n).write_bytes(b)
    m=dict(schema=SCHEMA,source_sha256=before,files_sha256={n:sha256(b).hexdigest() for n,b in files.items()},**platform.FLAGS);(output/'manifest.json').write_bytes(platform.encoded(m));return m


def verify(output=OUTPUT):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes())
    if m['source_sha256']!=sources():raise ValueError('candidate manufacturing inputs stale')
    if set(p.name for p in output.iterdir())!=set(m['files_sha256'])|{'manifest.json'}:raise ValueError('manufacturing inventory differs')
    for n,h in m['files_sha256'].items():
        if (output/n).is_symlink() or sha256((output/n).read_bytes()).hexdigest()!=h:raise ValueError('manufacturing bytes altered')
    value=json.loads(gzip.decompress((output/'study.json.gz').read_bytes()))
    if platform.encoded(value)!=platform.encoded(study()):raise ValueError('candidate manufacturing derived data differs')
    return dict(verified=True,products=len(value['products']),configuration_sha256=value['configuration_sha256'],**platform.FLAGS)
