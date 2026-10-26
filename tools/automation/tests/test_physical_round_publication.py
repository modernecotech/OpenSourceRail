"""Compact research must remain candidate-bound and honest about missing raw data."""
import importlib.util
from pathlib import Path
import json
import shutil

import pytest

ROOT=Path(__file__).resolve().parents[3]
SPEC=importlib.util.spec_from_file_location('physical_round_publisher',ROOT/'tools/automation/publish-physical-round.py')
MODULE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(MODULE)
OUTPUT=ROOT/'docs/design-engine/physical-feasibility-round'


def test_compact_git_packet_does_not_claim_full_native_reverification():
    result=MODULE.verify(OUTPUT,ROOT)
    assert result['publication_integrity_verified'] is True
    assert result['native_raw_reverified'] is False
    assert result['physical_accepted'] is False
    eligibility=MODULE.read(OUTPUT/'proposal-eligibility.json')
    assert len(eligibility['proposals'])==5
    assert all(r['positive_material_intersections']>0 and not r['eligible_for_integrated_selection'] for r in eligibility['proposals'])


@pytest.mark.parametrize('mutation', ['identity','acceptance','payload'])
def test_research_mixed_identity_release_and_modified_output_are_rejected(tmp_path,mutation):
    output=tmp_path/'packet';shutil.copytree(OUTPUT,output)
    m=MODULE.read(output/'manifest.json')
    if mutation=='payload':
        (output/'quantity-frontier.svg').write_text('<svg/>')
    else:
        if mutation=='identity':m['candidate_id']='0'*64
        else:m['physical_accepted']=True
        m['publication_id']=MODULE.selection.identity({k:v for k,v in m.items() if k!='publication_id'})
        (output/'manifest.json').write_bytes(MODULE.selection.encoded(m))
    with pytest.raises(ValueError):MODULE.verify(output,ROOT)


def test_human_units_preserve_urls_identifiers_and_commands():
    source='At40mm, native3D and80C. From35 to20mm,32.815m3 P0. [N35](https://example.test/N35) `N35UH`\n```bash\nrun --target N35\n```\n'
    text=MODULE.human_markdown(source)
    assert 'At 40 mm' in text and 'native 3D' in text and '80 C' in text
    assert 'From 35 to 20 mm,32.815 m³ P0.' in text
    assert '[N35](https://example.test/N35)' in text and '`N35UH`' in text
    assert 'run --target N35' in text
