"""Span lengths, proposed supports and procurement identities reconcile exactly."""
from osr_mech.civil.span_layout import plan_spans,span_quantities


def test_twenty_and_twenty_five_metre_spans_fit_without_overstating_length():
    spans=plan_spans('line',[(0,45),(100,140)])
    assert [s['length_m'] for s in spans]==[25,20,20,20]
    q=span_quantities(spans)
    assert q['total_alignment_m']==85 and q['special_spans']==0
    assert q['pi20_beams']==6 and q['pi25_beams']==2
    assert len({beam for s in spans for beam in s['component_ids']})==8
    assert spans[0]['pier_b']==spans[1]['pier_a']


def test_short_intervals_are_special_designs_not_twenty_five_metre_beams():
    spans=plan_spans('line',[(0,4.7),(10,54.7)])
    assert spans[0]['beam_variant'] is None and spans[0]['length_m']==4.7
    assert spans[-1]['beam_variant'] is None and spans[-1]['length_m']==24.7
    assert sum(s['length_m'] for s in spans)==49.4
    assert all(not s['component_ids'] for s in spans if s['beam_variant'] is None)


def test_millimetre_chainages_and_special_closures_reconcile_every_interval():
    spans=plan_spans('line',[(12.345,2086.732)])
    assert spans[0]['start_chainage_m']==12.345
    assert spans[-1]['end_chainage_m']==2086.732
    assert abs(sum(s['length_m'] for s in spans)-(2086.732-12.345))<1e-9
    assert all(a['end_chainage_m']==b['start_chainage_m'] for a,b in zip(spans,spans[1:]))
    assert all(s['length_m'] in (20,25) for s in spans if s['beam_variant'])
