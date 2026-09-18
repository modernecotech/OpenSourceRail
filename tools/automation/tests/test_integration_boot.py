"""ERP parent navigation trusts configured origins, never malformed URL prefixes."""
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import pytest


def hook(monkeypatch,origins):
    def fail(message):raise ValueError(message)
    fake=SimpleNamespace(conf={'osr_workbench_origins':origins},throw=fail)
    monkeypatch.setitem(sys.modules,'frappe',fake)
    path=Path(__file__).resolve().parents[3]/'deployment/erpnext/apps/osr_erpnext/osr_erpnext/integration_boot.py'
    spec=importlib.util.spec_from_file_location('boot_under_test',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def test_isolated_origin_reaches_native_boot(monkeypatch):
    boot=SimpleNamespace()
    hook(monkeypatch,['http://127.0.0.1:8190']).boot_session(boot)
    assert boot.osr_workbench_origins==['http://127.0.0.1:8190']


@pytest.mark.parametrize('origins',[[], 'http://localhost:8190', [None], ['javascript:alert(1)'],
    ['https://example.test/path'], ['https://example.test?query'], ['https://user:pass@example.test'],
    ['https://example.test#fragment']])
def test_invalid_origins_fail_before_navigation(monkeypatch,origins):
    with pytest.raises(ValueError):hook(monkeypatch,origins).boot_session(SimpleNamespace())
