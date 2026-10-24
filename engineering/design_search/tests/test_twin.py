"""Research twins preserve failed screens, real formats and exact variant stock."""
from hashlib import sha256
import json
from pathlib import Path

import pytest

from engineering.design_search import contracts, families, twin


def failed(candidate):
    request=contracts.make_evaluation_request(candidate,evaluator_id='civil',
        evaluator_sources={str(Path(__file__).name):sha256(Path(__file__).read_bytes()).hexdigest()},purpose='next-experiment')
    return contracts.make_result(request,execution_status='executed',numerical_status='converged',
        screen_status='fail',maturity='numerical-screen',metrics={'force_capacity_margin_n':-1000.})


def test_unknown_installed_stock_blocks_implicit_complete_twin(tmp_path):
    candidate=families.initial_families()[1]
    with pytest.raises(contracts.UnknownInstalledStock):
        twin.compile(candidate,[failed(candidate)],output=tmp_path/'blocked',export_native=False)
    assert not (tmp_path/'blocked').exists()


def test_other_candidate_evaluations_are_rejected_before_output(tmp_path):
    a,b,*_=families.initial_families()
    with pytest.raises(ValueError,match='mixed candidate'):
        twin.compile(a,[failed(b)],output=tmp_path/'mixed',allow_incomplete=True,export_native=False)
    assert not (tmp_path/'mixed').exists()


def test_three_variants_use_real_ifc_and_different_selected_stock_without_adoption(tmp_path):
    results=[]
    for candidate in families.initial_families():
        output=tmp_path/candidate['candidate_id']
        summary=twin.compile(candidate,[failed(candidate)],output=output,allow_incomplete=True,export_native=False)
        assert summary['native']['execution_status']=='not-run'
        assert not list(output.rglob('model.step'))
        assert not summary['digital_exports_executed']
        assert summary['bim']['verified']
        assert summary['retained_failed_or_unknown_evaluations']
        assert summary['unknown_installed_stock_ids']
        assert not summary['complete_installed_twin'] and not summary['configuration_adopted']
        products=json.loads((output/'manufacturing-bom.json').read_bytes())['bounded_products']
        delivery=json.loads((output/'delivery.json').read_bytes())
        assert delivery['configuration_sha256']==candidate['candidate_id']
        assert delivery['selected_beam_span_m']==summary['selected_beam']['span_m']
        assert summary['selected_beam_sha256']==products['selected_beam_sha256']
        assert not delivery['complete_cost_known']
        for row in delivery['procurement']:
            assert row['planned_arrival_day']<=row['need_by_day']
        twin.read_retained(output)
        if not results:
            # A forged receipt alone must not permit a foreign downstream config.
            manifest_path=output/'manifest.json';original_manifest=manifest_path.read_bytes()
            for name,message in [('manufacturing-bom.json','manufacturing BOM'),('assembly.json','assembly'),('delivery.json','delivery')]:
                path=output/name;original=path.read_bytes();changed=json.loads(original)
                changed['configuration_sha256']='f'*64;path.write_bytes(twin.encoded(changed))
                receipt=json.loads(original_manifest);receipt['files_sha256'][name]=sha256(path.read_bytes()).hexdigest()
                manifest_path.write_bytes(twin.encoded(receipt))
                with pytest.raises(ValueError,match=message):twin.read_retained(output)
                path.write_bytes(original);manifest_path.write_bytes(original_manifest)
        results.append((summary,products,delivery))
    assert len({row[0]['candidate_id'] for row in results})==3
    assert len({row[1]['products'][1]['geometry_sha256'] for row in results})==3
    assert len({row[0]['geometry_sha256'] for row in results})==3
    assert {row[0]['selected_beam']['span_m'] for row in results}=={20.,25.}
    counts=[row[2]['quantities'][0]['quantity'] for row in results]
    assert len(set(counts))==2


def test_actual_freecad_step_and_ifc_share_exact_known_part_set(tmp_path):
    candidate=families.initial_families()[0]
    summary=twin.compile(candidate,[failed(candidate)],output=tmp_path/'native',allow_incomplete=True)
    assert summary['digital_exports_executed']
    receipt=summary['native']['receipt']
    assert receipt['fcstd_reopened'] and receipt['step_reopened']
    assert receipt['part_count']==summary['known_native_parts']
    folder=tmp_path/'native'/summary['native']['relative_directory']
    assert (folder/'model.FCStd').stat().st_size>1000
    step=(folder/'model.step').read_bytes()
    assert step.startswith(b'ISO-10303-21;')
    assert b'END-ISO-10303-21;' in step
    source=json.loads((tmp_path/'native'/'native-definition.json').read_bytes())
    assert {row['id'] for row in source['parts']}=={row['id'] for row in receipt['parts']}
