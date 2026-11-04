from copy import deepcopy
from functools import partial
from http.server import ThreadingHTTPServer
import json
import subprocess
import sys
import threading
import urllib.request
import urllib.error
import pytest
from engineering.outline import approaches
from engineering.station_rail import ROOT
from engineering.development_baseline.server import Handler
from engineering.station_rail.common import identity


def test_reference_and_examples_do_not_close_transport_search():
    value=approaches.catalogue()
    assert value['policy']['reference_is_mandatory'] is False
    assert value['examples_are_exhaustive'] is False
    assert value['custom_proposals_allowed'] is True
    assert len(value['policy']['approaches'])>=7
    assert value['catalogue_id']==identity({k:v for k,v in value.items() if k!='catalogue_id'})


def test_unfamiliar_concept_is_retained_without_inherited_results_or_admission():
    value=approaches.propose(dict(name='New combined-function system',approach='not-in-any-seed-list',
        transport_function='Carry the declared passengers between access points',
        concept='An alternative physical arrangement needing its own models'),requirements_id='same-transport-goal')
    assert value['research_intake']=='accepted'
    assert value['physical_feasibility']=='not-assessed'
    assert value['comparison_admitted'] is False
    assert value['inherits_reference_results'] is False
    assert value['physical_candidate_id'] is None and value['cost'] is None
    assert len(value['next_tasks'])==len(approaches.REQUIRED_OUTPUTS)
    assert all(task['physical_failure_inferred'] is False for task in value['next_tasks'])
    assert all(value[k] is False for k in approaches.FLAGS)


def test_proposal_claims_cannot_grant_physical_release():
    original=dict(name='Onboard comparator',approach='wheel-traction',transport_function='Meet demand',
        concept='Own mass and energy definition',physical_accepted=True,manufacturing_release=True)
    before=deepcopy(original)
    value=approaches.propose(original,requirements_id='goal')
    assert value['physical_accepted'] is False and value['manufacturing_release'] is False
    assert value['automatic_dispatch'] is False
    assert value['proposal']['physical_accepted'] is True  # preserved as an input claim
    assert original==before


def test_model_tasks_are_bound_to_the_specific_alternative():
    base=dict(name='First idea',approach='first',transport_function='Meet demand',concept='Own model')
    a=approaches.propose(base,requirements_id='goal')
    base['name']='Second idea';base['approach']='second'
    b=approaches.propose(base,requirements_id='goal')
    assert a['next_tasks'][0]['task_id']!=b['next_tasks'][0]['task_id']


@pytest.mark.parametrize('missing',['name','approach','transport_function','concept'])
def test_proposals_need_a_function_and_definition(missing):
    value=dict(name='Proposal',approach='new',transport_function='Move passengers',concept='Definition')
    del value[missing]
    with pytest.raises(ValueError):approaches.propose(value,requirements_id='goal')


def test_cli_catalogue_does_not_require_a_numerical_run_or_output_directory():
    run=subprocess.run([sys.executable,'-m','engineering.outline','approaches'],cwd=ROOT,
        capture_output=True,text=True,check=True,timeout=10)
    value=json.loads(run.stdout)
    assert value['custom_proposals_allowed'] is True
    assert value['capability_declarations_grant_dispatch'] is False


def test_workbench_catalogue_is_read_only_and_exposes_the_search_scope():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,root=ROOT))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base='http://127.0.0.1:'+str(server.server_port)
    try:
        value=json.load(urllib.request.urlopen(base+'/api/outline-approaches'))
        assert value['examples_are_exhaustive'] is False
        assert '20 m' in value['policy']['current_calculator_scope']
        with pytest.raises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(urllib.request.Request(base+'/api/outline-approaches',data=b'{}'))
        assert caught.value.code==405
    finally:server.shutdown();server.server_close();thread.join(timeout=2)
