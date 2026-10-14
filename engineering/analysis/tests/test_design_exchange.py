from copy import deepcopy
import json
from pathlib import Path
import pytest
from engineering.design_engine.exchange import definition_diff,desktop_file_state
from engineering.design_consistency.demonstrators import panel_bay

ROOT=Path(__file__).resolve().parents[3]


def test_changed_supports_preserve_physical_ids_and_invalidate_all_dependent_evidence():
    config=json.loads((ROOT/'engineering/composite_panels/config/development.json').read_text())
    original=panel_bay(config);proposed=panel_bay(config,span=.2)
    result=definition_diff(original,proposed)
    assert result['changed_definition']and result['added']
    assert 'solver inputs'in result['invalidated']and 'mass-cg-inertia'in result['invalidated']
    assert result['baseline_overwrite_permitted']is False
    assert desktop_file_state('original','edited')['state']=='stale'


def test_uncontrolled_geometry_or_release_flags_cannot_be_reviewed_as_valid_definition():
    config=json.loads((ROOT/'engineering/composite_panels/config/development.json').read_text());model=panel_bay(config)
    bad=deepcopy(model);bad['production_released']=True
    with pytest.raises(ValueError):definition_diff(model,bad)


def test_revision_only_edit_is_a_visible_change_and_invalidates_evidence():
    config=json.loads((ROOT/'engineering/composite_panels/config/development.json').read_text())
    original=panel_bay(config,span=.2);proposed=deepcopy(original);proposed['revision']='desktop-fixture'
    result=definition_diff(original,proposed)
    assert result['changed_definition']is True and result['invalidated']
    assert result['changed']==[] and not result['added'] and not result['removed']
    assert result['physical_release']is False
