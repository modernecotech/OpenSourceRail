from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from engineering.trip_dynamics import campaign

ROOT = Path(os.environ.get('OSR_SOURCE_ROOT', campaign.ROOT))
HAS_SOURCE = (ROOT/'docs/design-engine/vehicle-optimisation/manifest.json').is_file()


@pytest.fixture
def packet(tmp_path):
    if not HAS_SOURCE:
        pytest.skip('explicit retained source root required in a sparse checkout')
    output = tmp_path/'trip'
    campaign.run(output, root=ROOT, run_rust=False)
    return output


def reseal(output, name):
    path = output/'manifest.json'
    value = json.loads(path.read_bytes())
    value['files_sha256'][name] = sha256((output/name).read_bytes()).hexdigest()
    path.write_text(json.dumps(value))


def test_missing_models_refuse_motion_and_no_backend_is_invented(packet):
    summary = json.loads((packet/'summary.json').read_bytes())
    assert summary['integrated_journeys_executed'] == summary['chrono_benchmarks_executed'] == 0
    assert summary['evidence_states'] == {'pass':0,'fail':0,'unknown':9}
    attempts = json.loads((packet/'evidence-attempts.json').read_bytes())
    assert len(attempts) == 9 and all(x['trajectory'] is None for x in attempts)
    assert '](benchmark-traces.png)' not in (packet/'README.md').read_text()
    assert not (packet/'benchmark-traces.png').exists()
    assert campaign.verify(packet, root=ROOT)['physical_accepted'] is False
    with pytest.raises(ValueError, match='fresh campaign'):
        campaign.run(packet, root=ROOT, run_rust=False)


def test_resealed_false_summary_counts_are_rejected(packet):
    path = packet/'summary.json'; value = json.loads(path.read_bytes())
    value['evidence_states']['pass'] = 9
    path.write_text(json.dumps(value)); reseal(packet, 'summary.json')
    with pytest.raises(ValueError, match='execution dispositions'):
        campaign.verify(packet, root=ROOT)


def test_resealed_acceptance_or_altered_gates_are_rejected(packet):
    path = packet/'evidence-attempts.json'; value = json.loads(path.read_bytes())
    value[0]['launch_authorised'] = True
    path.write_text(json.dumps(value)); reseal(packet, 'evidence-attempts.json')
    with pytest.raises(ValueError, match='source-bound evidence'):
        campaign.verify(packet, root=ROOT)


def test_template_mesh_and_runtime_lock_are_in_source_closure():
    if not HAS_SOURCE:
        pytest.skip('explicit retained root required')
    value = campaign.source_snapshot(ROOT)
    assert 'engineering/trip_dynamics/fixtures/structures/laminate.mail' in value
    assert 'engineering/trip_dynamics/environment-linux-64.lock' in value


def test_option_review_uses_upper_installation_band_and_never_selects(packet):
    rows = json.loads((packet/'option-review.json').read_bytes())
    assert len(rows['comparisons']) == 40
    assert rows['integrated_candidate_selected'] is None and rows['installed_cost'] is None
    for row in rows['comparisons']:
        context = row['comparison_mass_context']
        if 'AW3_band_kg_per_car' in context:
            assert context['AW3_kg_per_car'] == max(context['AW3_band_kg_per_car'])
            assert context['AW3_kg_per_car']-context['empty_kg_per_car'] == pytest.approx(12000.)
        assert row['dynamic_execution'] == 'not-run'


def test_evidence_packet_is_portable_to_another_retained_source_root(packet, tmp_path):
    alternate = tmp_path/'another-checkout'
    sources = json.loads((packet/'manifest.json').read_bytes())['source_sha256']
    for name in sources:
        destination = alternate/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/name, destination)
    # Portability includes authenticated historical producer objects. A copy
    # lacking the declared local ancestry must hold instead of fetching/falling back.
    with pytest.raises(ValueError, match='producer ancestry unavailable locally'):
        campaign.verify(packet, root=alternate)
    subprocess.run(['git','init','--quiet',str(alternate)],check=True)
    objects=subprocess.check_output(['git','rev-parse','--path-format=absolute','--git-path','objects'],
        cwd=ROOT,text=True).strip()
    (alternate/'.git/objects/info/alternates').write_text(objects+'\n')
    assert campaign.verify(packet, root=alternate)['physical_accepted'] is False
