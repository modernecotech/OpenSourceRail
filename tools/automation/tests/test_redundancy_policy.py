"""A weakened permission/loss rule or fabricated physical coverage must fail."""
import copy
import json
import pytest
from tools.automation import redundancy_policy as policy


def baseline():
    return json.loads((policy.ROOT/policy.POLICY).read_text())


def test_default_covers_all_functions_without_physical_acceptance():
    assert not policy.check_policy()
    data = baseline()
    assert all(f['physical_state'] == 'open' for f in data['functions'])


@pytest.mark.parametrize(('field','value'), [
    ('logical_channels',['A']), ('permission','one-out-of-two'), ('trip','both-channels'),
    ('channel_loss','continue'), ('single_channel_operation',True), ('automatic_takeover',True),
    ('raft_is_safety_redundancy',True), ('physical_independence_qualified',True),
    ('operational_release_ready',True), ('single_channel_operation',0)])
def test_weakening_or_qualification_claim_is_rejected(field, value):
    data = baseline(); data[field] = value
    assert policy.validate_policy(data)


def test_missing_function_common_cause_and_false_local_pair_are_rejected():
    for field in ('functions','common_causes'):
        data=baseline();data[field].pop()
        assert policy.validate_policy(data)
    data=copy.deepcopy(baseline());data['functions'][1]['reference_state']='logical-pair-executed'
    assert policy.validate_policy(data)
