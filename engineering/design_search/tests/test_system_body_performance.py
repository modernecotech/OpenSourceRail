"""Parity tests for the conservative body-stock disjoint prefilter."""
import math
import random

import pytest

from engineering.design_search import system_body as body


def original_subtract(box, cut):
    lo = [max(box[i], cut[i]) for i in (0, 2, 4)]
    hi = [min(box[i + 1], cut[i + 1]) for i in (0, 2, 4)]
    if min(b - a for a, b in zip(lo, hi)) <= 1e-10:
        return [box]
    x0, x1, y0, y1, z0, z1 = box
    a, c, e = lo
    b, d, f = hi
    return [p for p in ((x0,a,y0,y1,z0,z1),(b,x1,y0,y1,z0,z1),
                         (a,b,y0,c,z0,z1),(a,b,d,y1,z0,z1),
                         (a,b,c,d,z0,e),(a,b,c,d,f,z1))
            if min(p[1]-p[0],p[3]-p[2],p[5]-p[4])>1e-10]


def cut_sequence(box, cuts, *, fast):
    remaining = [box]
    finite = body._finite_box(box) and all(body._finite_box(cut) for cut in cuts)
    for cut in cuts:
        if fast and finite and body._disjoint_finite(box, cut):
            continue
        remaining = [q for old in remaining for q in original_subtract(old, cut)]
    return remaining


@pytest.mark.parametrize('offset', [-2e-10, -1e-10, -5e-11, 0.0, 5e-11, 1e-10, 2e-10])
def test_touch_and_tolerance_match_exactly(offset):
    box = (-1.0, 1.0, -2.0, 2.0, -3.0, 3.0)
    cut = (1.0 + offset, 2.0, -1.0, 1.0, -1.0, 1.0)
    assert cut_sequence(box, [cut], fast=True) == cut_sequence(box, [cut], fast=False)


def test_random_cut_sequences_keep_fragment_order_and_bytes():
    rng = random.Random(4280571)
    for _ in range(2500):
        def box():
            starts = [rng.uniform(-30, 30) for _ in range(3)]
            spans = [rng.choice([0.0, 1e-12, 1e-10, rng.uniform(0.00001, 10)]) for _ in range(3)]
            return tuple(v for x, d in zip(starts, spans) for v in (x, x+d))
        source = box()
        cuts = [box() for _ in range(rng.randrange(0, 8))]
        assert cut_sequence(source, cuts, fast=True) == cut_sequence(source, cuts, fast=False)


def test_disjoint_predicate_only_skips_original_unchanged_result():
    rng = random.Random(3125)
    for _ in range(25000):
        box = tuple(rng.uniform(-100,100) for _ in range(6))
        cut = tuple(rng.uniform(-100,100) for _ in range(6))
        if body._disjoint_finite(box, cut):
            assert original_subtract(box, cut) == [box]


def test_overlapping_cut_sequences_preserve_exact_fragments():
    rng = random.Random(641971)
    source = (-5.0, 5.0, -4.0, 4.0, -3.0, 3.0)
    for _ in range(300):
        cuts = []
        for _ in range(5):
            endpoints = [sorted((rng.uniform(-6,6), rng.uniform(-6,6))) for _ in range(3)]
            cuts.append(tuple(value for pair in endpoints for value in pair))
        assert cut_sequence(source, cuts, fast=True) == cut_sequence(source, cuts, fast=False)


def test_negative_zero_and_extreme_finite_coordinates():
    cases = [
        ((-0.0, 0.0, -1.0, 1.0, -1.0, 1.0), (0.0, 1.0, -1.0, 1.0, -1.0, 1.0)),
        ((-1e300, -1e299, -1.0, 1.0, -1.0, 1.0), (1e299, 1e300, -1.0, 1.0, -1.0, 1.0)),
        ((-1e-300, 1e-300, -1.0, 1.0, -1.0, 1.0), (1e-300, 1.0, -1.0, 1.0, -1.0, 1.0)),
    ]
    for box, cut in cases:
        assert repr(cut_sequence(box,[cut],fast=True)) == repr(cut_sequence(box,[cut],fast=False))


@pytest.mark.parametrize('bad', [float('nan'),float('inf'),float('-inf'),10**1000,'invalid',None,True])
def test_nonfinite_or_unsupported_coordinates_disable_fast_path(bad):
    assert not body._finite_box((bad,1.0,0.0,1.0,0.0,1.0))
    box = (bad,1.0,0.0,1.0,0.0,1.0)
    cut = (2.0,3.0,0.0,1.0,0.0,1.0)
    try:
        original = original_subtract(box, cut)
    except Exception as exc:
        with pytest.raises(type(exc)):
            cut_sequence(box,[cut],fast=True)
    else:
        assert repr(cut_sequence(box,[cut],fast=True)) == repr(original)


def test_finite_gate_handles_bad_lengths():
    assert not body._finite_box((0,1))
    assert not body._finite_box(None)
    assert body._finite_box((-0.0,1,0.0,1.0,-1.0,0.0))
