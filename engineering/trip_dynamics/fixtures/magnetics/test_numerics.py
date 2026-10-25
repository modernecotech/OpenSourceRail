"""Independent checks for the air-surface integration and replay recipes."""
import importlib.util
import json
import os
from pathlib import Path

import numpy as np
import pytest


SPEC = importlib.util.spec_from_file_location('finite_coupon', Path(__file__).with_name('finite_coupon.py'))
coupon = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(coupon)


def test_closed_air_contour_has_zero_net_force_and_moment_in_uniform_field(tmp_path):
    lo, hi = [-.7, -.3, -.1], [.4, .2, .8]
    field = [.31, -.47, .83]
    for axis in range(3):
        others = [i for i in range(3) if i != axis]
        for side in (0, 1):
            rows = []
            for a in np.linspace(lo[others[0]], hi[others[0]], 9):
                for b in np.linspace(lo[others[1]], hi[others[1]], 7):
                    point = lo.copy()
                    point[axis] = hi[axis] if side else lo[axis]
                    point[others[0]], point[others[1]] = a, b
                    rows.append([*point, *field])
            np.savetxt(tmp_path / f'face-0-{axis}-{side}.txt', rows)
    result = coupon.maxwell(tmp_path, [[lo, hi]])[0]
    assert result['force_N'] == pytest.approx([0., 0., 0.], abs=1e-8)
    assert result['moment_Nm'] == pytest.approx([0., 0., 0.], abs=1e-8)
    # A missing face must never silently become zero force.
    (tmp_path / 'face-0-0-0.txt').unlink()
    with pytest.raises(FileNotFoundError):
        coupon.maxwell(tmp_path, [[lo, hi]])


ROOT = Path(os.environ.get('OSR_EVIDENCE_ROOT', '/nonexistent'))
RECEIPT = ROOT / 'build/trip-dynamics/finite-coupon3d-v2/receipt.json'


@pytest.mark.skipif(not RECEIPT.is_file(), reason='explicit retained execution root required')
def test_current_recipe_replays_exact_newton_and_picard_solver_inputs():
    data = json.loads(RECEIPT.read_bytes())
    output = RECEIPT.parent
    for method, iterations, folder in [('newton', 60, 'coarse'), ('picard', 80, 'coarse-picard')]:
        actual = (output / folder / 'coupon.pro').read_bytes()
        replay = coupon.formulation(data['source']['value'], data['rows'][0]['mesh'],
                                    data['contours_m'], method=method, max_iterations=iterations)
        assert replay.encode() == actual
    with pytest.raises(ValueError, match='bounded declared'):
        coupon.formulation({}, {}, [], method='unsourced-law')


@pytest.mark.skipif(not RECEIPT.is_file(), reason='explicit retained execution root required')
def test_actual_failed_3d_attempts_supply_no_force_credit():
    data = json.loads(RECEIPT.read_bytes())
    repair = json.loads((RECEIPT.parent / 'picard-receipt.json').read_bytes())
    assert data['rows'][0]['nonlinear_converged'] is False
    assert data['rows'][0]['residual_relative'] > 1
    assert repair['nonlinear_converged'] is False and repair['residual_relative'] > .2
    assert repair['force_credit'] is False
    assert repair['force_map_generated'] is False and repair['physical_accepted'] is False
