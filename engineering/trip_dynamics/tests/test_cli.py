import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from engineering.trip_dynamics import __main__ as cli
from engineering.trip_dynamics import experiments


def test_module_default_is_status_and_case_list_is_available(monkeypatch,capsys):
    monkeypatch.setattr(experiments,'status',lambda root:dict(status='source-bound'))
    assert cli.main([])==0
    assert json.loads(capsys.readouterr().out)=={'status':'source-bound'}
    assert cli.main(['cases'])==0
    answer=json.loads(capsys.readouterr().out)
    assert len(answer['cases'])==9 and not answer['journey_accepted']


def test_selected_cli_constructs_only_bounded_request(tmp_path,monkeypatch,capsys):
    seen=[]
    def execute(request,output,root):seen.append((request,output,root));return {'execution_status':'refused'}
    monkeypatch.setattr(experiments,'execute',execute)
    assert cli.main(['simulate','--output',str(tmp_path/'job'),'--vehicle-id','a'*64,
        '--mode','evidence','--distance-m','1500','--load-case','empty','--temperature','50',
        '--mechanical-step-s','.0005'])==0
    request=seen[0][0]
    assert request==dict(action='experiment',parameters=dict(vehicle_id='a'*64,mode='evidence',
        distance_m=1500,load_case='empty',temperature_C=50.,mechanical_step_s=.0005))
    assert 'max_speed_m_s' not in request['parameters']


@pytest.mark.parametrize('arguments',[
    ['simulate','--max-speed-m-s','100'],['simulate','--mode','exploration'],
    ['simulate','--temperature','80'],['simulate','--distance-m','3000'],
    ['simulate','--mechanical-step-s','.01']])
def test_cli_rejects_unsupported_controls_before_execution(tmp_path,arguments):
    with pytest.raises(SystemExit) as error:cli.main([*arguments,'--output',str(tmp_path/'job')])
    assert error.value.code==2 and not (tmp_path/'job').exists()


def test_execute_job_loads_only_request_and_passes_inline_models(tmp_path,monkeypatch,capsys):
    request=dict(action='validate-modal',parameters=dict(vehicle_id='a'*64,model_data={'source_sha256':{'do-not-open':'0'*64}}))
    path=tmp_path/'request.json';path.write_text(json.dumps(request));seen=[]
    monkeypatch.setattr(experiments,'execute',lambda request,output,root:seen.append(request) or {'valid':False})
    assert cli.main(['execute-job','--request',str(path),'--output',str(tmp_path/'job')])==0
    assert seen==[request]


@pytest.fixture
def launcher(tmp_path):
    shutil.copyfile(experiments.ROOT/'osr',tmp_path/'osr')
    tools=tmp_path/'tools/automation';tools.mkdir(parents=True)
    helper=tools/'osr-python';helper.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
    helper.chmod(0o755)
    return tmp_path/'osr'


@pytest.mark.parametrize('args,expected',[
    (['trip'],['-m','engineering.trip_dynamics','status']),
    (['trip','cases'],['-m','engineering.trip_dynamics','cases']),
    (['trip','simulate','--mode','evidence'],['-m','engineering.trip_dynamics','simulate','--mode','evidence']),
    (['sim'],['-m','engineering.ferrite_maglev.cities','--simulate','baghdad']),
    (['twin','compile'],['-m','engineering.design_search','twin','compile']),
    (['design','campaign','tasks'],['-m','engineering.design_search','campaign','tasks']),
])
def test_launcher_trip_routing_preserves_existing_commands(launcher,args,expected):
    result=subprocess.run(['bash',str(launcher),*args],capture_output=True,text=True,check=True)
    assert result.stdout.splitlines()==expected


def test_launcher_help_lists_trip(launcher):
    result=subprocess.run(['bash',str(launcher),'--help'],capture_output=True,text=True,check=True)
    assert 'trip [action]' in result.stdout and 'assurance' in result.stdout


def test_native_probe_preserves_exact_solver_receipt(monkeypatch,capsys):
    from engineering.trip_dynamics import chrono_runner
    receipt=dict(available=True,fallback=False,solver_id='a'*64,backend='actual-native-test-receipt')
    monkeypatch.setattr(chrono_runner,'solver_info',lambda:receipt)
    def no_nested_probe(*a,**kw):raise AssertionError('native campaign probe must retain exact original backend receipt')
    monkeypatch.setattr(experiments,'probe',no_nested_probe)
    assert cli.main(['probe'])==0
    assert json.loads(capsys.readouterr().out)==receipt
