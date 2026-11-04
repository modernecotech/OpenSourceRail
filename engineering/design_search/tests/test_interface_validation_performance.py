"""Interface copy isolation and physical-projection regression controls.

The topology baselines were captured at commit 32263d93, before this validator
change. They are digital graph/quantity controls, not engineering acceptance.
"""
from copy import deepcopy
import json

import pytest

from engineering.design_search import design_grammar as grammar, interface_graph as g
from engineering.design_search import topology_mutation as mutation, topology_revision as revision
from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity


def graph():
    shared = {'unresolved': [None, {'evidence': 'unknown'}]}
    components = [
        {'occurrence_id': 'source', 'part_id': 'source-part', 'component_definition_id': 'b'*64,
         'functions': ['feed'], 'stock': {'mass_kg': None},
         'ports': [{'id': 'out', 'kind': 'electrical', 'direction': 'source', 'metadata': shared}]},
        {'occurrence_id': 'sink', 'part_id': 'sink-part', 'component_definition_id': 'c'*64,
         'functions': ['receive'], 'stock': {'mass_kg': 2.0},
         'ports': [{'id': 'in', 'kind': 'electrical', 'direction': 'sink', 'metadata': shared}]},
    ]
    return {'schema': g.SCHEMA, 'candidate_id': 'a'*64, 'requirement_revision': 'fixture-1',
            'components': components, 'connections': [{'id': 'wire', 'from': ['source', 'out'],
                                                         'to': ['sink', 'in']}],
            'required_functions': ['feed', 'receive'], 'unknown_metadata': shared}


def test_public_validation_preserves_shared_aliases_but_isolates_all_mutable_input():
    value = graph(); before = deepcopy(value)
    result = g.validate_identity(value)
    assert result == value and result is not value
    assert result['components'][0]['ports'][0]['metadata'] is result['unknown_metadata']
    assert result['components'][1]['ports'][0]['metadata'] is result['unknown_metadata']
    assert result['unknown_metadata'] is not value['unknown_metadata']
    result['unknown_metadata']['unresolved'][1]['evidence'] = 'modified'
    result['components'][0]['stock']['mass_kg'] = 0
    assert value == before and value['components'][0]['stock']['mass_kg'] is None


def test_private_checker_returns_original_without_mutating_unknowns_or_aliases():
    value = graph(); before = deepcopy(value); shared = value['unknown_metadata']
    assert g._check_identity(value) is value
    assert value == before
    assert value['components'][0]['ports'][0]['metadata'] is shared
    assert value['components'][1]['ports'][0]['metadata'] is shared
    assert 'physical_graph_id' not in value


def test_public_assessment_uses_a_snapshot_even_if_an_internal_consumer_mutates_it(monkeypatch):
    value = graph(); before = deepcopy(value)
    original = g._stock_totals
    def mutate_snapshot(snapshot):
        snapshot['unknown_metadata']['unresolved'][1]['evidence'] = 'mutated-inside-assessment'
        snapshot['components'][0]['stock']['mass_kg'] = 42.0
        return original(snapshot)
    monkeypatch.setattr(g, '_stock_totals', mutate_snapshot)
    result = g.assess(value)
    assert value == before and result['stock']['known_stock_mass_kg'] == 44.0
    assert result['stock']['complete_installed_mass_kg'] is None
    assert all(result[key] is False for key in g.FLAGS)


def invalid_graph(kind):
    value = graph()
    if kind == 'candidate': value['candidate_id'] = 'not-a-sha'
    elif kind == 'components': value['components'] = []
    elif kind == 'duplicate-occurrence': value['components'][1]['occurrence_id'] = 'source'
    elif kind == 'mixed-candidate': value['components'][0]['candidate_id'] = 'd'*64
    elif kind == 'function-duplicate': value['components'][0]['functions'] = ['feed', 'feed']
    elif kind == 'port-kind': value['components'][0]['ports'][0]['kind'] = 'unregistered'
    elif kind == 'port-duplicate': value['components'][0]['ports'].append(deepcopy(value['components'][0]['ports'][0]))
    elif kind == 'port-direction': value['components'][0]['ports'][0]['direction'] = 'undefined'
    elif kind == 'absent-endpoint': value['connections'][0]['to'] = ['missing', 'in']
    elif kind == 'duplicate-connection': value['connections'].append(deepcopy(value['connections'][0]))
    elif kind == 'required-duplicate': value['required_functions'] = ['feed', 'feed']
    elif kind == 'physical-id': value['physical_graph_id'] = 'f'*64
    elif kind == 'nonfinite': value['unknown_metadata']['unresolved'][0] = float('nan')
    else: raise AssertionError(kind)
    return value


@pytest.mark.parametrize('kind,message', [
    ('candidate', 'Explicit graph schema, physical candidate and requirement revision required'),
    ('components', 'Explicit component occurrences required'),
    ('duplicate-occurrence', 'Unique occurrence, part and component definition identities required'),
    ('mixed-candidate', 'Mixed candidate occurrence identities'),
    ('function-duplicate', 'Unique explicit function identities required'),
    ('port-kind', 'Unique typed port identity required'),
    ('port-duplicate', 'Unique typed port identity required'),
    ('port-direction', 'Typed source/sink/bidirectional direction required'),
    ('absent-endpoint', 'Connection references an absent occurrence/port'),
    ('duplicate-connection', 'Unique connection identity required'),
    ('required-duplicate', 'Unique explicit function identities required'),
    ('physical-id', 'Physical interface graph identity differs'),
    ('nonfinite', 'Out of range float values are not JSON compliant: nan'),
])
def test_public_and_private_checkers_preserve_rejection_and_do_not_mutate_input(kind, message):
    for validator in (g.validate_identity, g._check_identity):
        value = invalid_graph(kind)
        before = json.dumps(value, sort_keys=True, allow_nan=True)
        with pytest.raises(ValueError) as failure: validator(value)
        assert str(failure.value) == message
        assert json.dumps(value, sort_keys=True, allow_nan=True) == before


def test_error_order_and_invalid_header_are_checked_before_public_deepcopy():
    class NoCopy(dict):
        def __deepcopy__(self, memo): raise AssertionError('deepcopy called before invalid header was checked')
    invalid_header = NoCopy(graph()); invalid_header['candidate_id'] = 'bad'
    for validator in (g.validate_identity, g._check_identity):
        with pytest.raises(ValueError, match='Explicit graph schema'):
            validator(invalid_header)
    value = invalid_graph('port-kind'); value['connections'][0]['to'] = ['missing', 'in']
    for validator in (g.validate_identity, g._check_identity):
        with pytest.raises(ValueError, match='Unique typed port identity'):
            validator(value)
    value = invalid_graph('physical-id'); value['unknown_metadata']['unresolved'][0] = float('nan')
    for validator in (g.validate_identity, g._check_identity):
        with pytest.raises(ValueError, match='Physical interface graph identity differs'):
            validator(value)


@pytest.mark.parametrize('with_declared_id', [False, True])
@pytest.mark.parametrize('name', ['validate_identity', '_check_identity'])
def test_each_validator_calculates_physical_identity_once(monkeypatch, with_declared_id, name):
    value = graph()
    if with_declared_id: value['physical_graph_id'] = g.physical_identity(value)
    original = g.physical_identity; calls = []
    def counted(item):
        calls.append(item)
        return original(item)
    monkeypatch.setattr(g, 'physical_identity', counted)
    getattr(g, name)(value)
    assert len(calls) == 1


# Exact parent and three mutation projections captured at 32263d93; identity of
# `structure` excludes only source_sha256, which is checked separately below.
BASELINE = {
    'add-longitudinal-spine': ('886f88aca24e166b3d488ea05bdaa73cb0a15f18287e993adf302f1e6dc09a28',
        '866b0d0084fa536df7660371a9e16940b430202b574761fcfee72c3f14ea0947',
        '2f18c73cd9c23b206d1916e3ca92c2bcbac7d6820f6d98270c912339f80083c2',
        '17bb450ddedb80427dbe7309f8f5dcff347a258ce7f9595de0c036bf7afd6a5b',
        '3e83ea9a0934868f358db8689c6f6228116ef474f5d2851e4a3f249d93b5b038', 3905.4715426388575),
    'add-cellular-diaphragms': ('093dfb3ab582707bade73727ccecb31031843ebbcdd820aeb520a57c5127b79a',
        '7218be4ddd7d489eb5a247b1eb7fd100117bc00bfc0b41316442e9ff8718a132',
        'bdfa9d56933705c4ee325dae36056edefcf118fbb35a715d279bd1aec07e616d',
        '570dc9ad574c14548d42e274b5ea32a21f75ea66bf96c01ff6acd984d6e8c5a3',
        '5a3730dd3fd45bc39f56cd78740ec15abf33b83cec23a5a955762075d7c4d708', 4377.234257322449),
    'remove-alternate-crossframe-bracing': ('77a5b2a369846bd47583e8d33d8eaf1c006c3d96ad0a9719e656366e2d181be9',
        '70199082207897526720d4c99958151957298f12ffdf7afb3fcbb9a4f82b19b3',
        'cca2e6208612301a345c755205d36ba9c34dcec61dd0e72755df8da11fa49adb',
        '0e2f66696c621289850946f10c8aa980f6df9269a83675bc6263e133d0bb1fde',
        '943f1c1034f5540f7ced17cfba6f78ac8dadb071ed6db54d7f6efe2f66d7a3f6', 3123.904961321802),
}
BASELINE_DEFINITIONS = {
    'add-longitudinal-spine': 'ef7902b795aedf8140db7eb74fac49109d8548ca5007a4cbb6ab98abbcb9e9a1',
    'add-cellular-diaphragms': '7d627337e93ecd978326b803a2cd8a02961c8cf8281fef1b9d1bb114179cfaa6',
    'remove-alternate-crossframe-bracing': 'eec9834069ed9d7f385b9e4c6d157f71482f33902ded7798eb9ae3dead64b1ed',
}


@pytest.mark.parametrize('operator', list(BASELINE))
def test_topology_physical_and_accounting_projections_match_prior_source_epoch(operator):
    parameters = grammar.parameters(); parameters['braced'] = True
    parent = grammar.build(parameters)
    assert parent['candidate_id'] == '4798717e70ffcf5b36036605ebddf32a212832a184924cf0ef4afe21dd718975'
    before = deepcopy(parent)
    if operator == revision.OPERATOR:
        value = revision.mutate(parent, requirement_revision=parent['requirement_revision'])
        producer = revision.PRODUCER
    else:
        value = mutation.mutate(parent, operator, requirement_revision=parent['requirement_revision'])
        producer = mutation.PRODUCER
    candidate, components, connections, assembly, structure, stock = BASELINE[operator]
    assert parent == before and value['parent_candidate_ids'] == [parent['candidate_id']]
    assert value['candidate_id'] == candidate == identity(value['physical'])
    assert value['definition_id'] == identity({k: v for k, v in value.items() if k != 'definition_id'})
    assert value['definition_id'] != BASELINE_DEFINITIONS[operator]
    assert identity(value['components']) == components
    assert identity(value['connections']) == connections
    assert identity(value['assembly']) == assembly
    assert identity({k: v for k, v in value['structure'].items() if k != 'source_sha256'}) == structure
    assert value['known_structure_stock_kg'] == stock
    assert identity(value['retained_equipment_accounts']) == 'e6b22d4197490a07aaaf6012087ba68691252a3fb06c992b3f46132734439bbb'
    assert identity(value['required_functions']) == 'b80773b1668a73425d153637fe89d7eb9f908905beb964750620520ccc5eca02'
    for name in (producer, g.PRODUCER):
        assert value['sources'][name] == digest(ROOT / name)
        assert value['structure']['source_sha256'][name] == value['sources'][name]
    assert value.get('complete_installed_mass_kg') is None
    assert all(value[key] is False for key in grammar.FLAGS)
