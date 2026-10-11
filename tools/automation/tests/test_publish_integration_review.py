"""Review publication preserves source scope and exact retained output integrity."""
import hashlib,importlib.util,json
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('integration_review',ROOT/'tools/automation/publish-integration-review.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)


def test_historical_receipt_cannot_be_relabelled_as_current_or_hide_changed_output(tmp_path,monkeypatch):
    source=tmp_path/'source.py';source.write_text('old source\n')
    folder=tmp_path/'execution';folder.mkdir();artifact=folder/'result.json';artifact.write_text('{}\n')
    receipt=dict(physical_validation=False,sources_sha256={'source.py':review.sha(source)},outputs_sha256={'result.json':review.sha(artifact)})
    (folder/'receipt.json').write_text(json.dumps(receipt));monkeypatch.setattr(review,'ROOT',tmp_path)
    assert review.retained(folder)['current_recorded_sources_match']
    source.write_text('new source\n');row=review.retained(folder)
    assert row['evidence_status']=='historical-source-scope'
    assert row['changed_recorded_sources']==['source.py']
    assert row['retained_receipt']==receipt
    artifact.write_text('{"changed":true}\n')
    with pytest.raises(ValueError,match='retained output changed'):review.retained(folder)


def test_numerical_publication_requires_explicit_nonphysical_scope(tmp_path,monkeypatch):
    (tmp_path/'receipt.json').write_text(json.dumps({'physical_validation':True}))
    with pytest.raises(ValueError,match='nonphysical'):review.retained(tmp_path)
