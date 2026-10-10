"""OpenSourceRail screening rules cannot clear physical/ISO release gates."""
from copy import deepcopy
import json
from pathlib import Path
import runpy
import tomllib
import pytest

ROOT=Path(__file__).resolve().parents[3]
API=runpy.run_path(str(ROOT/'tools/automation/check-shared-engineering-standard.py'))
POLICY=tomllib.loads((ROOT/'engineering/assurance/standards/osr-eng-001.toml').read_text())
REVIEW=json.loads((ROOT/'engineering/civil_exploration/examples/shared-spatial-engineering-review.json').read_text())


def test_published_numerical_evidence_passes_without_issuing_iso_or_physical_acceptance():
    r=API['assess'](REVIEW,POLICY)
    assert r['numerical_process_passed']
    assert r['iso_conformity']=='unassessed' and not r['physical_validation'] and not r['engineering_released']
    assert r['open_gates']


def test_failed_refinement_cannot_be_cleared_by_a_passing_summary_flag():
    review=deepcopy(REVIEW)
    review['spatial']['temporal_refinement']['checks']['maximum_wheel_unloading']['relative_change']=.051
    assert review['spatial']['temporal_refinement']['passed']
    assert not API['assess'](review,POLICY)['numerical_process_passed']


def test_nonfinite_work_balance_and_missing_domain_do_not_pass():
    review=deepcopy(REVIEW);review['spatial']['cases'][0]['contact_work_residual_w']=float('nan')
    assert not API['assess'](review,POLICY)['numerical_process_passed']
    review=deepcopy(REVIEW);review['spatial']['cases'][0]['within_adapter_domain']=False
    assert not API['assess'](review,POLICY)['numerical_process_passed']


def test_bias_limit_is_separate_from_rms_and_synthetic_origin():
    review=deepcopy(REVIEW);row=review['synthetic_correlation']['holdout_tests'][0]
    row['residual']=[200.]*len(row['residual'])
    r=API['assess'](review,POLICY)
    assert not r['numerical_process_passed']
    assert next(x for x in r['requirements'] if x['id'].endswith('holdout-bias'))['status']=='fail'


def test_standard_change_reassesses_previous_numeric_results():
    policy=deepcopy(POLICY);policy['numerical']['refinement_relative_limit']=.001
    assert not API['assess'](REVIEW,policy)['numerical_process_passed']


def test_governed_protocols_keep_missing_project_limits_and_physical_execution_open():
    template=dict(levels=[dict(level=x,adopted_standard=None,project_limits=None,status='open')
        for x in ('part','subassembly','train','train-infrastructure')],physical_tests_performed=False)
    governed=API['governed_protocols'](template,POLICY)
    assert governed['governing_internal_standard']['version']=='1.0.0'
    assert all(r['adopted_standard']=='OSR-ENG-001@1.0.0' and r['project_limits'] is None and not r['iso_clause_review_complete'] for r in governed['levels'])
    assert not governed['physical_tests_performed'] and template['levels'][0]['adopted_standard'] is None
