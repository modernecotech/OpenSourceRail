import os
from pathlib import Path
import pytest
from engineering.trip_dynamics.archive import verify_magnetic_archive


def test_retained_actual_solver_attempts_are_hashed_replayable_and_uncredited():
    root = Path(os.environ.get('OSR_EVIDENCE_ROOT', Path(__file__).resolve().parents[3]))
    paths = [root/'docs/design-engine/trip-dynamics/finite-coupon-artifacts.tar.gz',
             root/'build/trip-dynamics/magnetic-fixture-artifacts.tar.gz']
    path = next((p for p in paths if p.is_file()), None)
    if path is None:
        pytest.skip('retained nonlinear archive omitted from sparse checkout')
    r = verify_magnetic_archive(path, root=root)
    assert r['member_hashes_current'] and r['replayed_solver_inputs']
    assert r['manufactured_method_pass'] and not r['force_map_generated']
    assert len(r['finite_candidate']['attempts']) == 3
    assert all(a['force_credit'] is False for a in r['finite_candidate']['attempts'])
    assert r['decoded_bytes'] < 64*1024**2
