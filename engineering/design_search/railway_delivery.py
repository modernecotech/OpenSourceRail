"""Candidate-specific research delivery drafts, never ERP posting or release."""
from pathlib import Path
from hashlib import sha256
import gzip,json
from copy import deepcopy
from engineering.station_rail.common import encoded,identity,digest
from . import design_grammar,railway_bundle,wheel_twin

PRODUCER='engineering/design_search/railway_delivery.py'
FLAGS=design_grammar.FLAGS


def compile(bundle,body,inventory):
    railway_bundle.validate(bundle);design_grammar.validate(body)
    if inventory['candidate_id']!=bundle['candidate_id'] or inventory['body_candidate_id']!=body['candidate_id'] or bundle['body_candidate_id']!=body['candidate_id']:raise ValueError('Delivery cannot combine different bundle/body/inventory identities')
    if inventory['evaluation_id']!=identity({k:v for k,v in inventory.items() if k!='evaluation_id'}):raise ValueError('Inventory receipt differs')
    common=dict(candidate_id=bundle['candidate_id'],body_candidate_id=body['candidate_id'],inventory_evaluation_id=inventory['evaluation_id'],
        purpose='Unreleased research draft; request evidence before purchasing or manufacture',**FLAGS)
    items=[];lines=[]
    for row in inventory['manufacturing_BOM']:
        key=identity(dict(body_id=body['candidate_id'],manufacturing_occurrence=row['id'],stock_ids=row['engineering_stock_ids']))
        items.append(dict(doctype='Item',item_code='OSR-RESEARCH-'+key,item_name=row['id'],stock_uom='Nos',
            is_stock_item=0,disabled=1,candidate_id=bundle['candidate_id'],body_candidate_id=body['candidate_id'],
            known_stock_mass_kg=row['known_gross_stock_mass_kg'],material_ids=row['material_ids'],source_stock_ids=row['engineering_stock_ids'],
            drawing_released=False,purchased_stock_and_yield=None,unit_price=None,supplier=None))
        lines.append(dict(item_code='OSR-RESEARCH-'+key,qty=1.,uom='Nos',rate=None,source_manufacturing_occurrence=row['id']))
    erp=dict(schema='osr-coupled-ERPNext-draft/1',**common,items=items,
        BOM=dict(doctype='BOM',item='OSR-RESEARCH-BODY-'+body['candidate_id'],quantity=1.,is_active=0,is_default=0,
            docstatus=0,items=lines,operations=None,total_cost=None),
        posted=False,ready_for_import=False,
        unresolved_occurrences=[r['id'] for r in inventory['engineering_BOM'] if r.get('geometry') is None],
        holds=['ERP custom-field/schema validation','Actual purchased stock, units/yield, tooling and inspection','Installed hardware and supplier evidence','Independent release and procurement authorization'])
    value=dict(schema='osr-coupled-research-delivery/1',**common,engineering_BOM=deepcopy(inventory['engineering_BOM']),manufacturing_BOM=deepcopy(inventory['manufacturing_BOM']),
        assembly=deepcopy(inventory['assembly_operation_graph']),procurement=deepcopy(inventory['supply_coverage']),
        component_tasks=deepcopy(inventory['component_tasks']),ERPNext=erp,complete_installed_BOM=False,complete_installed_cost_USD=None,
        source_sha256={PRODUCER:digest(__file__),wheel_twin.PRODUCER:digest(wheel_twin.__file__)})
    value['delivery_id']=identity(value);return value


def _box_mesh(part,volume):
    x,y,z=part['at_m'];dx,dy,dz=part['size_m']
    vertices=[[x,y,z],[x+dx,y,z],[x+dx,y+dy,z],[x,y+dy,z],[x,y,z+dz],[x+dx,y,z+dz],[x+dx,y+dy,z+dz],[x,y+dy,z+dz]]
    quads=((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))
    triangles=[f for a,b,c,d in quads for f in ((a,b,c),(a,c,d))]
    return dict(id=part['id'],vertices_m=vertices,triangles=triangles,native_volume_m3=volume)


def write(folder,bundle,body,inventory,*,CAD=None):
    folder=Path(folder)
    if folder.exists():raise ValueError('Fresh research delivery directory required')
    folder.mkdir(parents=True);value=compile(bundle,body,inventory)
    (folder/'delivery.json.gz').write_bytes(gzip.compress(encoded(value),mtime=0));(folder/'ERPNext-draft.json.gz').write_bytes(gzip.compress(encoded(value['ERPNext']),mtime=0))
    bim=dict(execution='not-run',candidate_id=bundle['candidate_id'],body_candidate_id=body['candidate_id'],complete_installed_geometry=False,**FLAGS)
    if CAD is not None:
        if CAD['candidate_id']!=body['candidate_id'] or any(p['kind']!='box' for p in body['parts']):raise ValueError('Exact box-stock native CAD/body correspondence required')
        volumes={r['id']:r['volume_m3'] for r in CAD['occurrences']}
        if set(volumes)!={p['id'] for p in body['parts']}:raise ValueError('CAD occurrence inventory differs')
        for p in body['parts']:
            if abs(volumes[p['id']]-p['volume_m3'])>max(1e-10,p['volume_m3']*1e-7):raise ValueError('CAD and delivery geometry volumes differ')
        parts=[dict(p,twin_frame='vehicle') for p in body['parts']]
        mesh=dict(rows=[_box_mesh(p,volumes[p['id']]) for p in parts])
        actual=wheel_twin._ifc(folder,bundle,parts,mesh)
        bim.update(actual,source_native_CAD_candidate_id=CAD['candidate_id'],
            representation='Exact box corners with native FreeCAD occurrence-volume correspondence and reopened IFC geometry checks; body stock only')
        raw=(folder/'wheel-stock.ifc').read_bytes();(folder/'body-stock.ifc.gz').write_bytes(gzip.compress(raw,mtime=0));bim['uncompressed_IFC_sha256']=sha256(raw).hexdigest()
    (folder/'bim.json').write_bytes(encoded(bim));m=dict(source_sha256=value['source_sha256'],candidate_id=bundle['candidate_id'],body_candidate_id=body['candidate_id'],
        files_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()},**FLAGS);m['manifest_id']=identity(m);(folder/'manifest.json').write_bytes(encoded(m));return m
