"""Current entrypoints cannot launch removed designs or enable physical outputs."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import subprocess

import pytest

ROOT=Path(__file__).resolve().parents[3]
SPEC=importlib.util.spec_from_file_location('current_host_contract',ROOT/'tools/automation/validate-host-manifests.py')
HOSTS=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HOSTS)


@pytest.mark.parametrize('arguments',[
    ['build','legacy'],['test','legacy'],['capabilities','--legacy'],
    ['catalogue','--legacy','index'],['example-city','setup'],
])
def test_removed_entrypoints_fail_before_launching_a_design(arguments):
    result=subprocess.run([str(ROOT/'osr'),*arguments],cwd=ROOT,capture_output=True,text=True,timeout=20)
    assert result.returncode==2
    assert 'Traceback' not in result.stderr


def test_only_offline_research_host_is_configured():
    assert HOSTS.validate()==[]
    profile=HOSTS.load_toml('deployment/maglev.toml')
    assert profile['runtime']['core_package'] in HOSTS.workspace_packages()
    assert profile['io']['hardware_addresses']==[]
    assert profile['io']['physical_outputs_enabled'] is False


@pytest.mark.parametrize('section,field,value',[
    ('release','design_complete',True),
    ('release','physical_validation',True),
    ('release','manufacturing_release',True),
    ('release','physical_release',True),
    ('io','physical_outputs_enabled',True),
    ('io','hardware_addresses',['/dev/ttyUSB0']),
    ('io','physical_adapter','current-driver'),
    ('runtime','mode','live-control'),
    ('runtime','target_timing_measured',True),
    ('runtime','target_sku_frozen',True),
])
def test_development_profile_rejects_physical_or_unqualified_claims(section,field,value):
    profile=deepcopy(HOSTS.load_toml('deployment/maglev.toml'))
    profile[section][field]=value
    assert HOSTS.validate_primary(profile)
