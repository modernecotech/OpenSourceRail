"""Read-only post-publication checks; not an engineering acceptance evaluator."""
from hashlib import sha256
from pathlib import Path
import gzip
import json
import math
import numpy as np
from engineering.ferrite_maglev import pilot_actuators as a


def packet(path):
    with gzip.open(path / 'study.json.gz', 'rb') as stream:
        raw = stream.read(64 * 1024 * 1024 + 1)
    assert len(raw) <= 64 * 1024 * 1024
    return json.loads(raw)


status = a.verify()
current = packet(a.OUTPUT)
baseline_path = a.OUTPUT.with_name('pilot-actuators-python-observer-baseline')
baseline = packet(baseline_path)
cases = []
for now, old in zip(current['full_estimator_cases'], baseline['full_estimator_cases']):
    assert now['estimator_scale'] == old['estimator_scale']
    assert now['profile'] == old['profile']
    assert now['completed_moving_steps'] == now['planned_moving_steps'] == 140417
    assert now['observer_execution']['backend'] == 'rust-cdylib'
    assert now['observer_execution']['successful_calls'] == 142417
    assert now['configuration_sha256'] == status['qualified_configuration_sha256']
    assert all(now[key] is False for key in a.FLAGS)
    area = now['configuration']['magnetic']['support_winding']['pole_area_m2']
    # Two attractive pole faces: this also bounds the observed post-step pose,
    # whereas the applied-force samples are evaluated before each advance.
    post_pose_force_bound = area / (4 * math.pi * 1e-7) * now['extrema']['peak_flux_t'] ** 2
    assert post_pose_force_bound <= 20000
    assert len(now['trace']) == len(old['trace'])
    differences = {}
    for key in ('car_relative_x_m', 'car_actual_speed_m_s', 'body_down_roll_pitch'):
        x = np.asarray([row[key] for row in now['trace']])
        y = np.asarray([row[key] for row in old['trace']])
        differences[key] = float(np.max(np.abs(x - y)))
    cases.append(dict(scale=now['estimator_scale'], configuration_sha256=now['configuration_sha256'],
                      profile_sha256=now['profile_sha256'], study_pass=now['study_pass'],
                      extrema=now['extrema'], observer_execution=now['observer_execution'],
                      post_pose_flux_force_bound_n=post_pose_force_bound,
                      python_reference_max_trace_difference=differences))

assert status['any_full_candidate_feasible'] is True
assert status['all_negative_controls_held'] is True
assert status['control_configuration_sha256'] == status['qualified_configuration_sha256']
assert len(current['controls']) == 9
assert all(item['expected_hold'] is True for item in current['controls'])
result = dict(schema='osr-pilot-rust-post-publication-observations/1',
              manifest_sha256=sha256((a.OUTPUT / 'manifest.json').read_bytes()).hexdigest(),
              sources=a.sources(), source_count=len(a.sources()), cases=cases,
              exact_candidate_controls_held=9,
              scope='Current packet verification, independent post-pose force bound and retained Python/Rust model trace comparison. No physical acceptance.',
              **a.FLAGS)
path = Path('build/pilot-actuators-rust-independent-check.json')
path.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
print(json.dumps(result, sort_keys=True, indent=2))
