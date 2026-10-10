"""Pure revision/instance/characteristic binding for native ERP QA transactions."""
import hashlib
import json
import math


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def validate_identity(identity):
    fields={'schema','configuration_sha256','design_revision','state','asset_id','characteristics','sha256'}
    if not isinstance(identity,dict) or set(identity)!=fields or identity['schema']!='osr-engineering-qa-map/1':
        raise ValueError('engineering QA identity contract invalid')
    if identity['sha256']!=digest({k:v for k,v in identity.items() if k!='sha256'}):
        raise ValueError('engineering QA map checksum changed')
    if identity['state'] not in ('as-designed','as-built','as-maintained') or not identity['design_revision']:
        raise ValueError('engineering QA revision/state missing')
    if len(identity['configuration_sha256'])!=64 or any(c not in '0123456789abcdef' for c in identity['configuration_sha256']):
        raise ValueError('exact engineering configuration checksum required')
    seen=set()
    for row in identity['characteristics']:
        if set(row)!={'inspection_id','instance_id','part_id','part_revision','serial','batch','characteristic','unit','minimum','maximum','joint_ids'}:
            raise ValueError('engineering characteristic fields missing or unknown')
        if row['inspection_id'] in seen or not all(row[k] for k in ('inspection_id','instance_id','part_id','part_revision','characteristic','unit')):
            raise ValueError('duplicate/incomplete engineering characteristic')
        seen.add(row['inspection_id'])
        for key in ('minimum','maximum'):
            v=row[key]
            if v is not None and (type(v) not in (int,float) or not math.isfinite(v)):
                raise ValueError('finite engineering inspection bounds required')
        if row['minimum'] is not None and row['maximum'] is not None and row['minimum']>row['maximum']:
            raise ValueError('ordered engineering inspection bounds required')
    return identity


def bind_quality_result(identity, native_record, measurement):
    """Bind an already-read native Work Order/Quality Inspection to one build.

    The caller retains native permissions/project scope. This pure adapter
    performs no writes, releases, ERP submissions or railway acceptance.
    """
    validate_identity(identity)
    if identity['state']=='as-designed' or not identity['asset_id']:
        raise ValueError('quality results require an individual built/maintained configuration')
    if set(native_record)!={'project','company','work_order','quality_inspection','material_batch','nonconformance','calibration_record'}:
        raise ValueError('native QA transaction references incomplete')
    if not all(native_record[k] for k in ('project','company','work_order','quality_inspection','calibration_record')):
        raise ValueError('work order, inspection and calibration references required')
    if set(measurement)!={'inspection_id','configuration_sha256','part_revision','serial','batch','unit','value'}:
        raise ValueError('measured characteristic contract invalid')
    row=next((r for r in identity['characteristics'] if r['inspection_id']==measurement['inspection_id']),None)
    if row is None or measurement['configuration_sha256']!=identity['configuration_sha256']:
        raise ValueError('measurement requires exact engineering revision and characteristic')
    if any(measurement[k]!=row[k] for k in ('part_revision','serial','batch','unit')):
        raise ValueError('measurement part revision, serial/batch or units differ')
    if not (row['serial'] or row['batch']) or native_record['material_batch']!=row['batch']:
        raise ValueError('measurement needs the identified physical part/material batch')
    value=measurement['value']
    if type(value) not in (int,float) or not math.isfinite(value):raise ValueError('finite native measured value required')
    lower,upper=row['minimum'],row['maximum']
    within=None if lower is None and upper is None else ((lower is None or value>=lower) and (upper is None or value<=upper))
    return dict(schema='osr-engineering-qa-binding/1',**native_record,measurement=measurement,
        asset_id=identity['asset_id'],instance_id=row['instance_id'],part_id=row['part_id'],joint_ids=row['joint_ids'],
        engineering_map_sha256=identity['sha256'],within_defined_limits=within,
        engineering_accepted=False,native_record_status_changed=False)
