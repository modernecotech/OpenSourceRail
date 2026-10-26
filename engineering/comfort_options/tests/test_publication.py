"""Cross-domain replay, identity and honest selection regressions."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import json
import pytest
from engineering.comfort_options import ROOT
from engineering.comfort_options import publication as p


@pytest.fixture(scope='module')
def campaign():
    return p.assemble(ROOT)


def test_primary_benches_capacity_and_service_are_consistent(campaign):
    result=p.summary(campaign)
    default=next(r for r in result['comparisons'] if r['role']=='door-bench-default' and r['HVAC_units']==5 and r['glazing'].startswith('Retained'))
    assert (default['seats'],default['benches'],default['wheelchair_places'],default['standing'],default['cap'])==(44,4,2,0,46)
    assert default['required_headway_s']==69
    assert default['capacity_at_180s_pphpd']==5520
    assert default['accounted_loaded_kg'] == pytest.approx(default['accounted_tare_kg']+46*75)
    assert not default['stable_hover_established']
    assert not campaign['selection']['integrated_candidate_selected']


def test_reused_field_samples_do_not_become_a_new_hover_pass(campaign):
    assert len(campaign['comparisons'])==36
    assert campaign['counts']['integrated_feasible']==0
    assert campaign['budgets']['new_native_field_solves']==0
    for row in campaign['comparisons']:
        assert row['magnet_component_id']==campaign['parent_magnet_component_id']
        assert row['mass']['actual_installed_tare_kg_per_car'] is None
        assert not row['stable_hover_established']
        assert not row['integrated_baseline_eligible']
        assert row['mass']['interior_allowance_saving_claimed_kg']==0
        assert any(c['passengers_total']==160 for c in row['support']['cases'])
        assert row['service']['safe_headway_s'] is None
    assert not campaign['structural_replacements_applied_to_composed_mass']


def test_thick_pc_mass_and_thin_pc_are_retained_as_alternatives(campaign):
    rows=[r for r in p.summary(campaign)['comparisons'] if r['role']=='door-bench-default' and r['HVAC_units']==5]
    glass=next(r for r in rows if r['glazing'].startswith('Retained'))
    thin=next(r for r in rows if '6 mm' in r['glazing'])
    thick=next(r for r in rows if '12 mm' in r['glazing'])
    assert thin['accounted_tare_kg']<glass['accounted_tare_kg']<thick['accounted_tare_kg']
    assert all(r['glazing_screen']=='unknown' for r in rows)


def test_packet_and_browser_digest_bind_exact_comparison(campaign):
    files=p.payloads(campaign)
    receipt=json.loads(files['manifest.json'])
    assert json.loads(gzip.decompress(files['study.json.gz']))==campaign
    assert receipt['study_id']==campaign['study_id']
    for name,digest in receipt['files_sha256'].items():
        assert sha256(files[name]).hexdigest()==digest
    ui=p.ui_files(ROOT,files)
    assert b'__SUMMARY_SHA256__' not in ui['app.js']
    assert sha256(files['summary.json']).hexdigest().encode() in ui['app.js']
    assert '5,520 pphpd' in files['README.md'].decode()
    assert b'69 s' in files['README.md']


def test_verifier_rejects_a_forged_seating_result(campaign,tmp_path,monkeypatch):
    changed=deepcopy(campaign);changed['comparisons'][0]['mass']['actual_installed_tare_kg_per_car']=0
    changed['study_id']=p.identity({k:v for k,v in changed.items() if k!='study_id'})
    for name,raw in p.payloads(changed).items():(tmp_path/name).write_bytes(raw)
    monkeypatch.setattr(p,'assemble',lambda root:campaign)
    with pytest.raises(ValueError,match='deterministic replay'):p.verify(tmp_path)
