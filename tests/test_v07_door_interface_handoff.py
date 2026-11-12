"""Door handoff preserves candidate, purchase counts and missing mating evidence."""
from copy import deepcopy

import pytest

from engineering.station_rail.common import identity
from engineering.vehicle_installation import model
from engineering.vehicle_parts import door_module
from tools.automation.door_interface_handoff import compile_handoff


@pytest.fixture(scope='module')
def source():
    module=door_module.build()
    installation=dict(schema='osr-vehicle-installation/1',
        physical_definition=dict(parent_candidate_id=module['candidate_id'],test_case='one-opening'),
        parent_candidate_id=module['candidate_id'],source_sha256=model.sources())
    installation['candidate_id']=identity(installation['physical_definition'])
    installation['evaluation_id']=identity(installation)
    attachment=dict(schema='osr-door-opening-proposed-layout-attachment/1',
        opening='car-0/door-0',candidate_id=installation['candidate_id'],
        evaluation_id=installation['evaluation_id'],
        parent_candidate_id=module['candidate_id'],source_bundle_id=module['source_bundle_id'],
        source_bundle_evaluation_id=module['source_evaluation_id'],
        source_door_module_sha256=module['source_sha256'][door_module.PRODUCER],
        accepted_installed_transform_m=None,source_sha256=installation['source_sha256'],
        component_audit=[dict(part_id=p['id'],component_definition_matches=True,
                              expanded_count=p['quantity_per_train']) for p in module['parts']])
    attachment['attachment_id']=identity(attachment)
    return module,attachment,installation


def test_real_counted_module_exposes_purchase_and_mating_holds(source):
    module,attachment,installation=source
    result=compile_handoff(module,attachment,installation,model.policy())
    assert result['physical_candidate_id']==module['candidate_id']
    assert result['type_counts']=={'buy-qualified':15,'buy-standard':20,'local-fabricate':39}
    assert result['piece_counts']=={'buy-qualified':29,'buy-standard':568,'local-fabricate':97}
    assert sum(p['quantity_per_opening'] for p in result['parts'])==694
    assert result['purchased_piece_count']==597
    assert result['opening_frame']['accepted_installation_datum'] is None
    assert all(p['installed_transform_m'] is None and p['approved_inspection_limits'] is None for p in result['parts'])
    assert result['handoff_id']==identity({k:v for k,v in result.items() if k!='handoff_id'})


@pytest.mark.parametrize('tamper', ['candidate','installed_candidate','evaluation','source','count','accepted_pose','installation_source'])
def test_mixed_or_promoted_door_attachment_refused(source,tamper):
    module,original,installation=source;attachment=deepcopy(original);installation=deepcopy(installation)
    if tamper=='candidate':attachment['parent_candidate_id']='0'*64
    elif tamper=='installed_candidate':attachment['candidate_id']='f'*64
    elif tamper=='evaluation':attachment['evaluation_id']='e'*64
    elif tamper=='source':attachment['source_sha256']={}
    elif tamper=='count':attachment['component_audit'][0]['expanded_count']+=1
    elif tamper=='accepted_pose':attachment['accepted_installed_transform_m']=[0.,0.,0.]
    else:
        name='engineering/vehicle_installation/model.py'
        installation['source_sha256'][name]='f'*64
        installation['evaluation_id']=identity({k:v for k,v in installation.items() if k!='evaluation_id'})
        attachment['source_sha256']=installation['source_sha256']
        attachment['evaluation_id']=installation['evaluation_id']
    attachment['attachment_id']=identity({k:v for k,v in attachment.items() if k!='attachment_id'})
    with pytest.raises(ValueError):compile_handoff(module,attachment,installation,model.policy())
