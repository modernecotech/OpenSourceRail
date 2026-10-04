"""Shared workforce evaluator, also installed with the native ERP adapter."""
import importlib.util
from pathlib import Path

_source = Path(__file__).resolve().parents[2] / 'deployment/erpnext/apps/osr_erpnext/osr_erpnext/workforce_rules.py'
_spec = importlib.util.spec_from_file_location('osr_shared_workforce_rules', _source)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
assignment_eligibility = _module.assignment_eligibility
