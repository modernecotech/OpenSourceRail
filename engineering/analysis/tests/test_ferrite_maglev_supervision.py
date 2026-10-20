"""Current process plans remain provisional at the generic supervisory boundary."""
from copy import deepcopy
from hashlib import sha256
import json

import pytest

from services.integration.osr_integration import embedded,manufacturing


def plan():
    return dict(schema='osr-maglev-city-manufacturing/1',process_routes=[dict(
        id='guidebeam-precast',operations=['Cast and cure to approved procedure'],
        plant=['Repeatable mould'],acceptance_holds=['Concrete strength and geometry'],
        qualified=False,production_instruction_released=False)])


def test_planning_routes_remain_unqualified_without_invented_factory_methods():
    source=plan()
    result=manufacturing.planning_process_status(source)
    assert result['deployable_factory_methods']==[]
    assert result['manufacturing_release'] is False and result['physical_release'] is False
    assert 'planning_cycle_minutes' not in json.dumps(result)
    result['process_routes'][0]['operations'].append('External mutation')
    assert len(source['process_routes'][0]['operations'])==1
    with pytest.raises(ValueError,match='schema'):
        manufacturing.factory_templates(source)


@pytest.mark.parametrize('field,value',[
    ('qualified',True),('production_instruction_released',True),
    ('operations',[]),('plant',[]),('acceptance_holds',[]),
])
def test_incomplete_or_falsely_released_process_plan_is_rejected(field,value):
    source=plan()
    source['process_routes'][0][field]=value
    with pytest.raises(ValueError):manufacturing.planning_process_status(source)


def production_document(tmp_path):
    source=tmp_path/'process.json';source.write_text('{"revision":"controlled-process-1"}')
    product=tmp_path/'products.json';product.write_text('{"product_items":[{"id":"GUIDEBEAM-01"}]}')
    return dict(schema=manufacturing.METHOD_SCHEMA,family=manufacturing.METHOD_FAMILY,
        qualified=True,production_instruction_released=True,
        qualification_record=dict(evidence_sha256='a'*64,review_reference='external-review-1'),
        method=[dict(id='GUIDEBEAM-PROCESS-01',title='Manufacture one guidebeam',
            work_center='precast-cell',release_gate='external-QA-review',crew_size=2,
            planning_cycle_minutes=30,product_ids=['GUIDEBEAM-01'],tooling_ids=['MOULD-01'],
            source_ids=['controlled-process-1'],steps=[dict(sequence=1,planning_minutes=30,
                name='Bound production operation',instruction='Use the externally released instruction',hold_point=True)])],
        coverage=dict(method_count=1,product_rows=1,covered_product_rows=1,
            tooling_count=1,uncovered_product_ids=[]),revision='process-1',status='external-claims',
        release_boundary='Metadata consistency only; claims require external authentication',
        source_file='process.json',source_sha256=sha256(source.read_bytes()).hexdigest(),
        product_manifest='products.json',product_manifest_sha256=sha256(product.read_bytes()).hexdigest())


def test_factory_document_requires_bound_products_sources_and_explicit_qualification(tmp_path):
    document=production_document(tmp_path)
    manufacturing.validate_method_sources(document,tmp_path)
    views=manufacturing.factory_templates(document)
    assert len(views)==1 and next(iter(views.values()))['commands']=={}
    (tmp_path/'process.json').write_text('{"revision":"different"}')
    with pytest.raises(ValueError,match='changed'):
        manufacturing.validate_method_sources(document,tmp_path)
    unqualified=deepcopy(document);unqualified['qualified']=False
    with pytest.raises(ValueError,match='qualified production'):
        manufacturing.factory_templates(unqualified)


def test_factory_simulation_requires_an_explicit_method_instead_of_a_hidden_default():
    with pytest.raises(ValueError,match='explicitly deployed'):
        manufacturing.factory_control_state({},['GUIDEBEAM-PROCESS-01'])
    state=manufacturing.factory_control_state({'factory_method':'GUIDEBEAM-PROCESS-01'},['GUIDEBEAM-PROCESS-01'])
    assert state['factory_cycle_progress_pct']==0


def test_removed_wheel_specific_observations_are_not_accepted_as_current_frames():
    frame=dict(schema='osr-supervisory-observations/1',environment='simulation',
        authority='observation-only',key='baghdad|factory',source_time_ns=1,
        observations=[dict(equipment_type='removed-equipment',measurement='state',
            value=0,unit='state',source_crates=['removed-source'])])
    with pytest.raises(ValueError,match='missing or excess'):
        embedded.operating_measurements(frame)
