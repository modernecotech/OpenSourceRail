"""Portable ERP characteristic identity and revision mismatch regression checks."""
from copy import deepcopy
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src'),str(ROOT/'deployment/erpnext/apps/osr_erpnext')]
sys.path.insert(0,str(ROOT/'services/integration'))
from osr_mech.engineering_definition import engineering_identity
from engineering.civil_exploration.shared_demo import demonstration
from osr_erpnext.engineering_identity import validate_identity,bind_quality_result,digest


def fixture():
    model=demonstration();model['state']='as-built';model['asset_id']='train-serial-001'
    for i,r in enumerate(model['instances']):r['serial']=f'part-{i}';r['batch']='material-test-batch'
    identity=engineering_identity(model)
    characteristic=identity['characteristics'][0]
    measurement={k:characteristic[k] for k in ('inspection_id','part_revision','serial','batch','unit')}
    measurement.update(configuration_sha256=identity['configuration_sha256'],value=2500.)
    native=dict(project='test-project',company='test-company',work_order='test-work-order',quality_inspection='test-quality-inspection',
        material_batch='material-test-batch',nonconformance=None,calibration_record='test-calibration')
    return identity,native,measurement


def test_native_qa_identity_contains_actual_joint_and_revision_mapping():
    identity,native,measurement=fixture();validate_identity(identity)
    result=bind_quality_result(identity,native,measurement)
    assert result['asset_id']=='train-serial-001' and result['instance_id']=='car-1/battery'
    assert result['joint_ids']==['car-1/battery-retention']
    assert result['within_defined_limits'] and not result['engineering_accepted']
    assert not result['native_record_status_changed']


@pytest.mark.parametrize('field,value',[('configuration_sha256','old'),('part_revision','other'),('serial','other'),('batch','other'),('unit','g'),('value',True)])
def test_native_characteristic_rejects_stale_or_wrong_build_identity(field,value):
    identity,native,measurement=fixture();measurement[field]=value
    with pytest.raises(ValueError):bind_quality_result(identity,native,measurement)


def test_unknown_characteristic_or_changed_mapping_never_reuses_result():
    identity,native,measurement=fixture();changed=deepcopy(identity);changed['characteristics'][0]['maximum']=3000.
    with pytest.raises(ValueError,match='checksum'):validate_identity(changed)
    with pytest.raises(ValueError):bind_quality_result(identity,native,dict(measurement,inspection_id='unknown'))


def test_execution_proposal_retains_map_bound_to_actual_engineering_artifact(tmp_path):
    import json
    from osr_integration.engineering import package,execution_proposal
    model=demonstration();model['state']='as-built';model['asset_id']='build-001'
    for i,r in enumerate(model['instances']):r['serial']=f'serial-{i}'
    identity=engineering_identity(model);(tmp_path/'instances.json').write_text(json.dumps(model))
    manifest=dict(city='test-city',asset_id='build-001',engineering_revision=model['revision'],assumptions=['synthetic test only'],
        artifacts=[dict(path='instances.json',tool='verification',tool_version='test')],engineering_identity=identity)
    engineering=package(tmp_path,manifest)
    mapping=dict(review_reference='test-review',engineering_sha256=engineering['sha256'],items=[
        dict(component_type_id='LM3-TRC-P040',erp_item_code='battery-test-item',uom='ea',
             inspection_reference='battery-mass-car-1',drawing_reference='unissued-test-drawing')])
    proposal=execution_proposal(engineering,mapping)
    assert proposal['engineering_identity']==identity and proposal['automatic_order_release'] is False
    changed=deepcopy(manifest);changed['asset_id']='another-build'
    with pytest.raises(ValueError,match='revision/asset'):package(tmp_path,changed)
    model['instances'][0]['revision']='other-revision';(tmp_path/'instances.json').write_text(json.dumps(model))
    with pytest.raises(ValueError,match='exact retained'):package(tmp_path,manifest)
