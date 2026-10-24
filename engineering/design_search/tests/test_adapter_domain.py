"""A signed physical edit must be consumed or refused, never reconstructed away."""
from copy import deepcopy

import pytest

from engineering.design_search import contracts, evaluators, families


@pytest.fixture(scope='module')
def candidate():return families.initial_families()[0]


def signed_change(candidate,mutation):
    value=deepcopy(candidate);geometry={row['id']:row for row in value['geometry']}
    if mutation=='section':geometry['guidebeam/section-definition']['definition']['depth_m']+=.05
    elif mutation=='concrete-position':geometry['guidebeam/concrete/0']['at_m'][2]+=.02
    elif mutation=='magnetic-position':geometry['magnetic-module']['definition']['parts'][0]['at_m'][0]+=.001
    elif mutation=='inventory-cg':value['installed_inventory'][0]['cg_m'][0]+=.01
    elif mutation=='material-basis':value['materials'][0]['basis']='Different material assumption without a registered adapter'
    elif mutation=='interface':value['interfaces'][0]['qualified']=True
    else:raise AssertionError(mutation)
    value['candidate_id']=contracts.identity(dict(units=contracts.UNITS,**{key:value[key] for key in contracts.PHYSICAL_KEYS}))
    contracts.validate_candidate(value)
    return value


@pytest.mark.parametrize('mutation',['section','concrete-position','magnetic-position','inventory-cg','material-basis','interface'])
def test_rehashed_unsupported_physical_edits_are_not_ignored(candidate,mutation):
    changed=signed_change(candidate,mutation)
    with pytest.raises(families.UnsupportedCandidateDomain,match='differs'):
        families.materialize(changed,allow_incomplete=True)
    with pytest.raises(families.UnsupportedCandidateDomain):families.selected_beam(changed)


def test_unknown_stock_is_not_removed_to_make_adapter_accept(candidate):
    value=deepcopy(candidate)
    value['installed_inventory']=[row for row in value['installed_inventory'] if row['status']=='known']
    value['candidate_id']=contracts.identity(dict(units=contracts.UNITS,**{key:value[key] for key in contracts.PHYSICAL_KEYS}))
    with pytest.raises(families.UnsupportedCandidateDomain):families.materialize(value,allow_incomplete=True)


def test_context_and_lineage_variants_preserve_supported_geometry(candidate):
    changed=contracts.bind_context(candidate,requirement_revision='new-req-context',lineage={'parent_candidate_ids':['a'*64],'operation':'reviewed-context'})
    assert changed['candidate_id']==candidate['candidate_id']
    assert families.materialize(changed,allow_incomplete=True)['candidate_id']==candidate['candidate_id']


@pytest.mark.parametrize('name',['definition','mechanical','civil','magnetic','coupling'])
def test_every_registered_evaluator_returns_typed_domain_refusal(candidate,name):
    changed=signed_change(candidate,'section')
    value=evaluators.evaluate(changed,name,purpose='next-experiment')
    assert value['execution_status']=='refused'
    assert value['numerical_status']=='invalid'
    assert value['screen_status']=='unknown'
    assert value['candidate_id']==changed['candidate_id']
    assert value['diagnostics'][0]['error_type']=='UnsupportedCandidateDomain'
    assert not value['physical_accepted']


def test_official_span_revision_remains_in_domain(candidate):
    revised=families.with_beam_selection(candidate,span_m=20.)
    assert families.materialize(revised,allow_incomplete=True)['guideway_definition']['span_m']==20.


def test_revision_helper_cannot_silently_erase_an_unsupported_parent_edit(candidate):
    changed=signed_change(candidate,'magnetic-position')
    with pytest.raises(families.UnsupportedCandidateDomain):families.with_beam_selection(changed,span_m=20.)
    with pytest.raises(families.UnsupportedCandidateDomain):families.propose_revision(changed,[])
