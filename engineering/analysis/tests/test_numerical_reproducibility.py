"""Round-off agreement never weakens exact design, source or release identity."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from engineering.assurance.numerical_reproducibility import differences,require_equivalent,require_html_equivalent


def test_contact_roundoff_reproduces_but_a_changed_force_does_not():
    expected=dict(review=dict(minimum_static_contact_n=40726.1007143399,static_reaction_balance_n=0.))
    actual=deepcopy(expected);actual['review']['minimum_static_contact_n']+=2.2e-11
    actual['review']['static_reaction_balance_n']=4e-10
    assert differences(actual,expected)==[]
    actual['review']['minimum_static_contact_n']+=.001
    with pytest.raises(ValueError,match='minimum_static_contact_n'):require_equivalent(actual,expected,'solver reproduction')


@pytest.mark.parametrize('path,value', [('source_sha256','changed'),('configuration_sha256','changed'),
    ('engineering_accepted',True),('instance_count',319),('material_density',7850.000000001)])
def test_sources_configuration_decisions_counts_and_design_values_stay_exact(path,value):
    expected=dict(source_sha256='original',configuration_sha256='original',engineering_accepted=False,instance_count=318,material_density=7850.)
    actual=deepcopy(expected);actual[path]=value
    assert differences(actual,expected)==[path]


@pytest.mark.parametrize('value',[float('nan'),float('inf'),True,40726])
def test_nonfinite_or_changed_types_cannot_use_numeric_tolerances(value):
    assert differences({'minimum_static_contact_n':value},{'minimum_static_contact_n':40726.})


def test_html_checks_script_bytes_exactly_and_only_tolerates_the_embedded_solver_metric():
    start='<script id="data" type="application/json">';end='</script><script>render()</script>'
    def page(force):return start+json.dumps(dict(review=dict(minimum_static_contact_n=force)))+end
    require_html_equivalent(page(40000.+2e-11),page(40000.))
    with pytest.raises(ValueError,match='source'):require_html_equivalent(page(40000.).replace('render()','tampered()'),page(40000.))
    with pytest.raises(ValueError,match='minimum_static'):require_html_equivalent(page(40001.),page(40000.))
