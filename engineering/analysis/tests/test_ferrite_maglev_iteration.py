"""Adaptive search evidence: outcomes affect proposals; failures cannot win."""
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from engineering.ferrite_maglev import iteration as it,model


def fake(vector,*,reverse=False,confirmation=False):
    score=sum(vector) if not reverse else -sum(vector)
    return dict(candidate_id=it.identity(vector),vector=vector,parameters=dict(zip(it.NAMES,vector)),
        phase='confirmation' if confirmation else 'training',screen_pass=True,
        metrics=dict(score=score,ordinary_civil_allowance_usd_dual_km=score,tare_kg=1,
            hot_cycle_kwh_per_car=1,maximum_final_heave_error_m=1,minimum_gap_margin_m=1),**model.FLAGS)


def test_proposals_adapt_to_measured_results_and_are_reproducible():
    a=it.load()
    first=it.search(a,fake,lambda v:fake(v,confirmation=True))
    again=it.search(a,fake,lambda v:fake(v,confirmation=True))
    opposite=it.search(a,lambda v:fake(v,reverse=True),lambda v:fake(v,confirmation=True))
    assert first==again
    assert first['history'][0]['candidate_ids']==opposite['history'][0]['candidate_ids']
    assert first['history'][1]['candidate_ids']!=opposite['history'][1]['candidate_ids']
    assert len({r['candidate_id'] for r in first['candidates']})==len(first['candidates'])
    rows={r['candidate_id']:r for r in first['candidates']}
    for row in rows.values():
        for parent in row['proposal']['parents']:assert rows[parent]['generation']<row['generation']
    assert any(r['proposal']['parents'] for r in rows.values())
    assert first['global_optimum_proven'] is False


def test_failed_confirmation_disqualifies_exact_revision_and_selects_alternative():
    a=it.load();calls=[]
    def confirm(v):
        row=fake(v,confirmation=True);row['screen_pass']=bool(calls);calls.append(row['candidate_id']);return row
    result=it.search(a,fake,confirm)
    assert len(calls)==2
    assert result['selected_candidate_id']==calls[1]
    failed=next(r for r in result['candidates'] if r['candidate_id']==calls[0])
    assert failed['screen_pass']  # original analysis remains in history
    assert failed['confirmation_state']=='failed'
    assert not failed['eligible_for_research_recommendation']
    assert calls[0] not in result['pareto_candidate_ids']


def test_no_confirmed_candidate_means_no_recommendation():
    def reject(v):return dict(fake(v,confirmation=True),screen_pass=False)
    r=it.search(it.load(),fake,reject)
    assert r['selected_candidate_id'] is None
    assert not any(row['eligible_for_research_recommendation'] for row in r['candidates'])


def test_execution_error_is_a_hold_not_a_cached_candidate_rejection():
    def unavailable(v):raise RuntimeError('tool unavailable')
    with pytest.raises(RuntimeError,match='tool unavailable'):it.search(it.load(),unavailable,fake)


def test_cache_requires_exact_sources_vector_hash_and_false_release_flags(tmp_path):
    v=it.quantise([.8,1.9,.15,.18,25,1,1,1,1,90,212.5,.8],it.load());r=fake(v)
    path=tmp_path/'cache.json'
    def write():path.write_bytes(it.encoded(dict(epoch='a',result=r,sha256=sha256(it.encoded(r)).hexdigest())))
    write();assert it.read_cache(path,v,'a')==r
    assert it.read_cache(path,v,'b') is None
    changed=v.copy();changed[0]=.9
    assert it.read_cache(path,changed,'a') is None
    r['physical_release']=True;write();assert it.read_cache(path,v,'a') is None
    path.write_text('{interrupted');assert it.read_cache(path,v,'a') is None


def test_nonfinite_or_outside_physical_envelope_cannot_pass():
    a=it.load();r=dict(minimum_relative_gap_m=.006,maximum_relative_gap_m=.01,
        final_fitted_relative_heave_error_m=.00001,final_roll_rad=0.,final_pitch_rad=0.,peak_station_force_n=15000.,
        physical_output_authorised=False,structural_acceptance=False)
    assert it.case_pass(r,a)
    for k,v in [('minimum_relative_gap_m',.0029),('final_roll_rad',float('nan')),
                ('physical_output_authorised',True),('peak_station_force_n',20001.)]:
        assert not it.case_pass(dict(r,**{k:v}),a)


def test_published_campaign_has_actual_cases_and_source_receipts():
    it.verify();r=json.loads(gzip.decompress((it.OUTPUT/'result.json.gz').read_bytes()))
    assert r['selected_candidate_id']
    assert r['execution']['bridge_sha256']
    assert len(r['history'])>=2
    assert r['evaluator']=='actual Rust coupled_bridge and Python modal beam'
    assert all(row['cases'] and row['protection']['passed'] for row in r['confirmations'] if row['screen_pass'])


def test_passing_confirmation_cannot_omit_required_cases_even_with_new_hashes(tmp_path):
    # Consistent checksums do not replace complete applicable evidence.
    import shutil
    shutil.copytree(it.OUTPUT,tmp_path/'packet');packet=tmp_path/'packet'
    r=json.loads(gzip.decompress((packet/'result.json.gz').read_bytes()))
    selected=r['selected_candidate_id']
    next(row for row in r['confirmations'] if row['candidate_id']==selected)['cases']=[]
    data=gzip.compress(it.encoded(r),mtime=0);(packet/'result.json.gz').write_bytes(data)
    m=json.loads((packet/'manifest.json').read_text());m['files_sha256']['result.json.gz']=sha256(data).hexdigest()
    (packet/'manifest.json').write_bytes(it.encoded(m))
    with pytest.raises(ValueError,match='mandatory'):it.verify(packet)
