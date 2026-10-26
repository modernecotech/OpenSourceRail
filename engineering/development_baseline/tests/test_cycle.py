"""Generated refresh units must load in systemd, including spaced project paths."""
import importlib.util
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT=Path(__file__).resolve().parents[3]


def test_refresh_units_load_with_real_systemd_parser(tmp_path):
    tool=shutil.which('systemd-analyze')
    if tool is None:pytest.skip('systemd unit parser unavailable on this platform')
    path=ROOT/'tools/automation/default-design-cycle.py'
    spec=importlib.util.spec_from_file_location('current_refresh_units',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    directory=tmp_path/'rail project with spaces';directory.mkdir()
    for name,text in module.units(directory,python='/bin/true').items():
        (tmp_path/name).write_text(text)
    result=subprocess.run([tool,'--user','verify',str(tmp_path/'osr-development-baseline.service'),
                           str(tmp_path/'osr-development-baseline.timer')],capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr
    with pytest.raises(ValueError,match='single-line'):
        module.units(Path('/tmp/project\nInjected=setting'))
