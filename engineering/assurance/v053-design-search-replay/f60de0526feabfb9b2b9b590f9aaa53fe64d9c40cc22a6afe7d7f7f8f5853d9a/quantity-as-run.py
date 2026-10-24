"""Independent primitive/scope audit of retained data, not an export-helper replay."""
import sys
sys.dont_write_bytecode=True
from collections import Counter
from hashlib import sha256
import argparse
import gzip
import json
import math
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path('/home/hayder/Documents/OpenSourceRail')
BASELINE='ed05b47c9216df1819f745bef9597812a9d1ef009501cc399ae1da78904b5798'


def read(path,maximum=64*1024**2):
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size>maximum:raise ValueError('bounded ordinary data required: '+str(path))
    return json.loads(path.read_bytes())


def digest(path):
    value=sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024**2),b''):value.update(block)
    return value.hexdigest()


def same(a,b,label):
    if not math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-8):raise ValueError(label+' differs')


def identity(value):return sha256((json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()


def overlap_volume(a,b):
    return math.prod(max(0.,min(a['at_m'][i]+a['size_m'][i],b['at_m'][i]+b['size_m'][i])-max(a['at_m'][i],b['at_m'][i])) for i in range(3))


def audit_candidate(candidate):
    expected=identity(dict(units=candidate['units'],**{key:candidate[key] for key in ('architecture','frames','materials','geometry','interfaces','installed_inventory')}))
    if expected!=candidate['candidate_id']:raise ValueError('physical bundle identity differs')
    geometry={row['id']:row for row in candidate['geometry']};materials={row['id']:row for row in candidate['materials']}
    inventory=candidate['installed_inventory'];carrier=[];concrete=[]
    if len(geometry)!=len(candidate['geometry']):raise ValueError('duplicate authority geometry IDs')
    for item in inventory:
        part=geometry.get(item.get('geometry_id'))
        if not part or part.get('kind')!='box':continue
        if item['status']=='known' and item['scope']=='vehicle-per-car' and part['material_id']=='carrier-steel':
            if item['frame_id']!='vehicle' or part['frame_id']!='vehicle' or item['quantity']!=1:raise ValueError('carrier stock is outside one vehicle-frame instance')
            density=materials['carrier-steel']['density_kg_m3'];same(item['unit_mass_kg'],math.prod(part['size_m'])*density,'carrier material mass')
            carrier.append(part['id'])
        if part['material_id']=='concrete' or part['id'].startswith('guidebeam/concrete/'):
            if (part['material_id']!='concrete' or part['frame_id']!='guidebeam' or item['frame_id']!='guidebeam' or
                item['scope']!='guideway-per-span' or item['status']!='known' or item['quantity']!=1):raise ValueError('concrete has vehicle/carrier/unknown scope')
            same(item['unit_mass_kg'],math.prod(part['size_m'])*materials['concrete']['density_kg_m3'],'concrete material mass')
            if part.get('role')!='guidebeam-concrete-stock':raise ValueError('concrete role differs from guidebeam stock')
            concrete.append(part)
    labelled={part['id'] for part in geometry.values() if part.get('role')=='added-carrier-stock'}
    if labelled!=set(carrier) or len(carrier)!=len(set(carrier)):raise ValueError('added-carrier role differs from actual vehicle steel inventory')
    mode=candidate['architecture']['carrier']['mode'];count=candidate['architecture']['carrier']['count_per_car']
    expected_carrier=0 if mode=='rigid-existing-hardpoints' else 16*count
    if len(carrier)!=expected_carrier:raise ValueError('repeated carrier wall count differs')
    if len(concrete)!=6 or len({p['id'] for p in concrete})!=6:raise ValueError('exact six concrete solids required')
    if any(overlap_volume(a,b)>1e-10 for i,a in enumerate(concrete) for b in concrete[i+1:]):raise ValueError('authority concrete solids overlap in volume')
    section=geometry['guidebeam/section-definition']['definition'];span=candidate['architecture']['guidebeam']['span_m']
    b,h,tw,tf=[section[key] for key in ('width_m','depth_m','web_m','flange_m')]
    ends=[part for part in concrete if part['size_m'][0]<span]
    if len(ends)!=2:raise ValueError('two finite end blocks required')
    same(ends[0]['size_m'][0],ends[1]['size_m'][0],'end block length')
    end=ends[0]['size_m'][0]
    expected_volume=(b*h-(b-2*tw)*(h-2*tf))*span+2*end*(b-2*tw)*(h-2*tf)
    volume=sum(math.prod(part['size_m']) for part in concrete);same(volume,expected_volume,'hollow beam and end infill volume')
    return dict(candidate_id=candidate['candidate_id'],label=candidate.get('label'),carrier_mode=mode,
        carrier_count_per_car=count,known_vehicle_carrier_solids=len(carrier),carrier_ids=sorted(carrier),
        guideway_concrete_solids=len(concrete),concrete_ids=sorted(p['id'] for p in concrete),
        concrete_volume_m3=volume,concrete_mass_kg=volume*materials['concrete']['density_kg_m3'],
        carrier_and_concrete_ids_disjoint=not bool(set(carrier)&{p['id'] for p in concrete}),
        concrete_sizes=sorted([p['size_m'] for p in concrete]),section_id=section['id'],span_m=span,
        authority_scope_checks_passed=True)


def fcstd_design_ids(path):
    with zipfile.ZipFile(path) as archive:
        info=archive.getinfo('Document.xml')
        if info.file_size>32*1024**2:raise ValueError('bounded FCStd metadata required')
        raw=archive.read(info)
    if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():raise ValueError('external XML entities forbidden')
    root=ET.fromstring(raw);objects=[]
    for obj in root.findall('.//ObjectData/Object'):
        values={}
        for prop in obj.findall('./Properties/Property'):
            if prop.get('name') in {'DesignId','Role','ProductionReleased'}:
                values[prop.get('name')]=list(prop)[0].get('value') if len(prop) else None
        if 'DesignId' in values:values['object_name']=obj.get('name');objects.append(values)
        elif obj.find("./Properties/Property[@name='Shape']") is not None:raise ValueError('actual CAD has unaccounted shape object without design identity')
    feature_names={obj.get('name') for obj in root.findall('./Objects/Object') if obj.get('type','').startswith('Part::')}
    if feature_names!={obj['object_name'] for obj in objects}:raise ValueError('actual CAD feature inventory differs from identified stock')
    if not objects or len({obj['DesignId'] for obj in objects})!=len(objects):raise ValueError('actual serialized CAD IDs missing/duplicated')
    return objects


def audit_twin(folder,candidate,authority):
    folder=Path(folder);manifest=read(folder/'manifest.json')
    for name,expected in manifest['files_sha256'].items():
        path=Path(name)
        if path.is_absolute() or '..' in path.parts or digest(folder/path)!=expected:raise ValueError('twin payload binding differs')
    retained=read(folder/'candidate.json')
    if retained!=candidate:raise ValueError('twin authority differs from campaign physical bundle')
    native=read(folder/'native-definition.json');materialized=read(folder/'materialized-candidate.json');bom=read(folder/'manufacturing-bom.json');summary=read(folder/'twin.json')
    if native['candidate_id']!=BASELINE or summary['candidate_id']!=BASELINE or bom['configuration_sha256']!=BASELINE:raise ValueError('mixed baseline export identity')
    parts=native['parts'];ids={p['id'] for p in parts}
    if len(parts)!=len(ids):raise ValueError('duplicate native stock IDs')
    carriers=[p for p in parts if p['id'].startswith('carrier/') or p.get('role')=='added-carrier-stock' or p.get('material') in {'carrier-steel','declared-carrier-steel'}]
    if carriers or materialized.get('additional_stock') or bom['additional_known_stock_lines']:raise ValueError('baseline exports additional carrier stock')
    if any(p['id'].startswith('guidebeam/concrete/') for p in parts):raise ValueError('untranslated duplicate concrete stock exported as added carrier')
    concrete=[p for p in parts if p.get('material')=='concrete']
    if len(concrete)!=6 or any(not p['id'].startswith('civil/girder/') for p in concrete):raise ValueError('exact six civil concrete native solids required')
    if sorted(p['size_m'] for p in concrete)!=authority['concrete_sizes']:raise ValueError('native concrete sizes differ from authoritative bundle')
    volume=sum(math.prod(p['size_m']) for p in concrete);same(volume,authority['concrete_volume_m3'],'native concrete volume')
    products=bom['bounded_products']['products'];cuts=[line for product in products for line in product['cut_schedule'] if line['component_scope']=='precast-concrete']
    grouped=[row['source'] for product in products for row in product['bom'] if row['source']['component_scope']=='precast-concrete']
    if len(cuts)!=1 or len(grouped)!=1:raise ValueError('concrete MBOM appears in multiple bounded products')
    concrete_ids={p['id'] for p in concrete}
    for line in cuts+grouped:
        if set(line['geometry_part_ids'])!=concrete_ids or len(line['geometry_part_ids'])!=6:raise ValueError('concrete MBOM source coverage duplicated')
        same(line['net_quantity'],volume,'one-span MBOM concrete volume');same(line['mass_kg'],authority['concrete_mass_kg'],'one-span MBOM concrete mass')
    assembly=read(folder/'assembly.json')
    if any(p['product_id']=='COUNTED-CARRIER-STOCK' for p in assembly['bounded_products']):raise ValueError('baseline assembly invents carrier product')
    native_dir=folder/summary['native']['relative_directory'];cad=fcstd_design_ids(native_dir/'model.FCStd')
    if {obj['DesignId'] for obj in cad}!=ids:raise ValueError('serialized FCStd objects differ from retained native stock')
    if any(obj['DesignId'].startswith('carrier/') or obj.get('Role')=='added-carrier-stock' for obj in cad):raise ValueError('actual FCStd has extra carrier parts')
    if len([obj for obj in cad if obj['DesignId'] in concrete_ids])!=6:raise ValueError('actual FCStd duplicates/misses concrete objects')
    # Read the real IFC entity names without creating shapes or calling exports.
    import ifcopenshell
    with gzip.open(folder/'bim/candidate.ifc.gz','rb') as stream:raw=stream.read(64*1024**2+1)
    if len(raw)>64*1024**2:raise ValueError('bounded IFC required')
    model=ifcopenshell.file.from_string(raw.decode());ifc_ids=[obj.Name for obj in model.by_type('IfcBuildingElementProxy')]
    if len(ifc_ids)!=len(set(ifc_ids)) or set(ifc_ids)!=ids:raise ValueError('actual IFC stock IDs differ or duplicate')
    return dict(candidate_id=BASELINE,native_part_count=len(parts),actual_fcstd_objects=len(cad),actual_ifc_objects=len(ifc_ids),
        additional_carrier_native_parts=0,additional_carrier_fcstd_objects=0,additional_carrier_mbom_rows=0,
        concrete_native_parts=6,concrete_fcstd_objects=6,concrete_ifc_objects=sum(name in concrete_ids for name in ifc_ids),
        native_concrete_volume_m3=volume,mbom_cut_concrete_rows=1,mbom_grouped_concrete_rows=1,
        mbom_concrete_net_m3=cuts[0]['net_quantity'],mbom_concrete_mass_kg=cuts[0]['mass_kg'],
        concrete_sizes_match_authority=True,duplicate_quantity_found=False,helper_exports_called=False,
        complete_installed_twin=summary['complete_installed_twin'],integrated_baseline_ready=summary['integrated_baseline_ready'])


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--replay-report',required=True,type=Path);args=parser.parse_args()
    replay=read(args.replay_report);state=Path(replay['extracted_state']);campaign_id=replay['campaign_id']
    definition=read(state/'campaigns'/campaign_id/'definition.json');journal=read(state/'campaigns'/campaign_id/'journal.json')
    candidates=[read(state/'campaigns'/campaign_id/'candidates'/(context+'.json')) for context in journal['candidate_context_ids']]
    audits=[audit_candidate(value) for value in candidates]
    initial=[row for row,context in zip(audits,journal['candidate_context_ids']) if context in definition['candidate_context_ids']]
    if [row['known_vehicle_carrier_solids'] for row in initial]!=[0,64,80]:raise ValueError('initial independent carrier count is not0/64/80')
    baseline=next(value for value in candidates if value['candidate_id']==BASELINE);authority=next(row for row in audits if row['candidate_id']==BASELINE)
    twin=ROOT/'docs/design-engine/design-search-twins'/BASELINE
    report=dict(schema='osr-independent-design-scope-quantity-audit/1',campaign_id=campaign_id,archive_sha256=replay['archive_sha256'],
        audit_scope='Independent authority/serialized CAD/IFC/MBOM quantity checks; separate from numerical replay and physical qualification.',
        candidate_quantity_checks=audits,initial_carrier_counts=[row['known_vehicle_carrier_solids'] for row in initial],
        every_candidate_has_six_guideway_only_concrete_boxes=True,baseline_twin=audit_twin(twin,baseline,authority),
        solver_execution=False,source_edit=False,export_helpers_called=False,physical_acceptance_established=False)
    output=Path(tempfile.mkdtemp(prefix='osr-independent-design-quantities-'))/'quantity-audit.json'
    output.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(report_path=str(output),**report),sort_keys=True,indent=2))


if __name__=='__main__':main()
