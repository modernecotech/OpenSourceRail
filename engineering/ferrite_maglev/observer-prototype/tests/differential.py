#!/usr/bin/env python3
"""Independent stdlib analytical/complex-number oracle against the Rust ABI.

No import of the production Python observer or its allocation constants. The
oracle constructs a general Gram matrix and solves its 3x3 equations by pivoted
elimination; Rust uses the independently derived diagonal closed form.
"""
import cmath
import copy
import ctypes
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import random
import subprocess
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('observer_binding', PACKAGE/'python/observer.py')
binding = importlib.util.module_from_spec(spec)
spec.loader.exec_module(binding)
X = [x/2 for x in range(-11, 12, 2) for _ in range(2)]
Y = [-0.88, 0.88]*12
FIXTURE = PACKAGE/'tests/fixtures/delayed-map.json'
SHA = hashlib.sha256(b'isolated-observer-differential-context').hexdigest()
COMPARISONS = 0
MAX_ABS_ERROR = 0.0


def solve(matrix, values):
    augmented = [list(r)+[v] for r, v in zip(matrix, values)]
    for i in range(3):
        pivot = max(range(i, 3), key=lambda j: abs(augmented[j][i]))
        augmented[i], augmented[pivot] = augmented[pivot], augmented[i]
        scale = augmented[i][i]
        if abs(scale) < 1e-12:
            raise ValueError('singular independent allocation')
        augmented[i] = [v/scale for v in augmented[i]]
        for j in range(3):
            if i != j:
                factor = augmented[j][i]
                augmented[j] = [v-factor*w for v, w in zip(augmented[j], augmented[i])]
    return [r[-1] for r in augmented]


def oracle(sample, k, scale):
    fields, speed, currents, centres = sample
    wrench = []
    for car in range(6):
        terms = []
        for group, current in enumerate(currents):
            angle = fields['theta'][group][car] + k*speed[car]*0.001
            local = complex(*current)*cmath.exp(complex(0, -angle))
            terms.append(1.5*k*fields['psi'][group][car]*local.real)
        wrench.append([sum(terms), 0.0,
                       -sum(term*(fields['normal_positions_m'][i][car]-centres[car]) for i, term in enumerate(terms))])
    rows = [[1.0]*24, Y, [-x for x in X]]
    gram = [[sum(a*b for a, b in zip(r, s)) for s in rows] for r in rows]
    correction = []
    for w in wrench:
        multiplier = solve(gram, [scale*v for v in w])
        correction.append([-sum(row[i]*m for row, m in zip(rows, multiplier)) for i in range(24)])
    return wrench, correction


def build_library():
    target = Path(os.environ.get('OSR_OBSERVER_TARGET_DIR', PACKAGE/'target'))
    subprocess.run(['cargo', 'build', '--locked', '--release', '--manifest-path', str(PACKAGE/'Cargo.toml'),
                    '--target-dir', str(target)], check=True)
    return target/'release/libosr_normal_wrench_observer_prototype.so'


class Differential(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library = build_library()

    def near(self, actual, expected):
        global COMPARISONS, MAX_ABS_ERROR
        COMPARISONS += 1
        MAX_ABS_ERROR = max(MAX_ABS_ERROR, abs(actual-expected))
        self.assertTrue(math.isclose(actual, expected, rel_tol=4e-12, abs_tol=2e-9), (actual, expected))

    def execute(self, sample, k, scale, identity=SHA):
        observer = binding.Observer(self.library, identity, len(sample[2]), k, scale)
        desired = [[12400.0]*24 for _ in range(6)]
        first = observer.step(1, 123_000_000, desired)
        self.assertEqual(first.physical_output_authorised, 0)
        result = observer.step(2, 124_000_000, desired, sample,
                               sample_sequence=1, sample_timestamp_ns=123_000_000,
                               sample_configuration_sha256=identity)
        return observer, result

    def compare(self, sample, k, scale, identity=SHA):
        _, actual = self.execute(sample, k, scale, identity)
        wrench, correction = oracle(sample, k, scale)
        for car in range(6):
            for component in range(3):
                self.near(actual.raw_wrench_up_roll_pitch[car][component], wrench[car][component])
                self.near(actual.scaled_wrench_up_roll_pitch[car][component], wrench[car][component]*scale)
            for module in range(24):
                self.near(actual.correction_n[car][module], correction[car][module])
                self.near(actual.requested_support_n[car][module], 12400+correction[car][module])
            # Independent force and torque balance, including sign convention.
            self.near(sum(actual.correction_n[car]), -scale*wrench[car][0])
            self.near(sum(f*y for f, y in zip(actual.correction_n[car], Y)), 0.0)
            self.near(sum(-f*x for f, x in zip(actual.correction_n[car], X)), -scale*wrench[car][2])
        return actual

    def test_retained_exact_python_vector_all_scales(self):
        f = json.loads(FIXTURE.read_text())
        provenance = json.loads((FIXTURE.parent/'provenance.json').read_text())
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), provenance['fixture_sha256'])
        self.assertEqual(f['module_x_m'], X)
        self.assertEqual(f['module_y_m'], Y)
        sample = (f['fields'], f['speed_m_s'], f['currents_alpha_beta_a'], f['centres_m'])
        for scale in (0.9, 1.0, 1.1):
            with self.subTest(scale=scale):
                output = self.compare(sample, f['k_rad_per_m'], scale, f['configuration_sha256'])
                for car in range(6):
                    for j in range(3):
                        self.near(output.raw_wrench_up_roll_pitch[car][j], f['wrench_up_roll_pitch'][car][j])
                    if scale == 1:
                        for module in range(24):
                            self.near(output.correction_n[car][module], f['correction_n'][car][module])
                            self.near(output.requested_support_n[car][module], f['corrected_12400n_baseline'][car][module])

    def test_seeded_finite_random_and_adverse_vectors(self):
        rng = random.Random(0x05F3A11)
        # Includes all 200 groups, reversed speed/current, sparse/zero linkages,
        # phase wraps and varying k, using a fixed seed for exact reproduction.
        for case in range(64):
            count = [1, 3, 140, 200][case % 4]
            k = [math.pi/.25, .001, 100.0, math.pi/.25][case % 4]
            centres = [rng.uniform(-1000, 1000) for _ in range(6)]
            fields = dict(psi=[[0.0 if case%9 == 0 or rng.random()<.3 else rng.uniform(0, .02)
                                for _ in range(6)] for _ in range(count)],
                          theta=[[rng.uniform(-1000, 1000) for _ in range(6)] for _ in range(count)],
                          normal_positions_m=[[c+rng.uniform(-7, 7) for c in centres] for _ in range(count)])
            currents = [[rng.uniform(-200, 200)*(12.56/k) for _ in range(2)] for _ in range(count)]
            sample = (fields, [rng.uniform(-75, 75) for _ in range(6)], currents, centres)
            for scale in (.9, 1.0, 1.1):
                with self.subTest(case=case, scale=scale):
                    self.compare(sample, k, scale)

    def test_binding_refuses_shape_hash_clock_and_nonfinite_without_state_advance(self):
        f = json.loads(FIXTURE.read_text())
        sample = (f['fields'], f['speed_m_s'], f['currents_alpha_beta_a'], f['centres_m'])
        observer, _ = self.execute(sample, f['k_rad_per_m'], 1)
        state = bytes(observer.state)
        desired = [[12400.0]*24 for _ in range(6)]
        for metadata, status in [
            (dict(sequence=2, timestamp_ns=125_000_000), 3),
            (dict(sequence=3, timestamp_ns=125_000_001), 4),
            (dict(sample_sequence=1), 8),
            (dict(sample_timestamp_ns=123_000_000), 9),
            (dict(sample_timestamp_ns=125_000_000), 9),
            (dict(sample_configuration_sha256='f'*64), 7),
        ]:
            args = dict(sequence=3, timestamp_ns=125_000_000, desired_support_n=desired, sample=sample,
                        sample_sequence=2, sample_timestamp_ns=124_000_000,
                        sample_configuration_sha256=SHA)
            args.update(metadata)
            with self.subTest(metadata=metadata), self.assertRaises(binding.ObserverRefusal) as caught:
                observer.step(**args)
            self.assertEqual(caught.exception.status, status)
            self.assertEqual(bytes(observer.state), state)
        for channel in ('psi', 'theta', 'normal_positions_m'):
            broken = copy.deepcopy(sample)
            broken[0][channel][0][0] = float('nan')
            with self.assertRaises(binding.ObserverRefusal) as caught:
                observer.step(3, 125_000_000, desired, broken, sample_sequence=2,
                              sample_timestamp_ns=124_000_000, sample_configuration_sha256=SHA)
            self.assertEqual(caught.exception.status, 11)
        for broken in [(sample[0], sample[1][:-1], sample[2], sample[3]),
                       (sample[0], sample[1], sample[2][:-1], sample[3])]:
            with self.assertRaises(ValueError):
                observer.step(3, 125_000_000, desired, broken, sample_sequence=2,
                              sample_timestamp_ns=124_000_000, sample_configuration_sha256=SHA)
        for invalid in (-1, 2**64, True, 2.0):
            with self.assertRaises(ValueError):
                observer.step(invalid, 125_000_000, desired)
        self.assertEqual(bytes(observer.state), state)

    def test_configuration_abi_layout_and_c_header(self):
        self.assertEqual(ctypes.sizeof(binding.Config), 64)
        self.assertEqual(ctypes.sizeof(binding.State), 88)
        self.assertEqual(ctypes.sizeof(binding.Group), 160)
        self.assertEqual(ctypes.sizeof(binding.Frame), 33320)
        self.assertEqual(ctypes.sizeof(binding.Input), 33472)
        self.assertEqual(ctypes.sizeof(binding.Output), 2696)
        subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fsyntax-only',
                        str(PACKAGE/'tests/header-layout.c')], check=True)
        for groups in (0, 201, -1, 2**32+3):
            with self.assertRaises(ValueError):
                binding.Observer(self.library, SHA, groups, 12.56)
        with self.assertRaises(ValueError):
            binding.Observer(self.library, 'not-a-digest', 3, 12.56)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Differential)
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps(dict(schema='osr-observer-differential-result/1', tests=outcome.testsRun,
                          failed=len(outcome.failures)+len(outcome.errors), comparisons=COMPARISONS,
                          maximum_absolute_difference=MAX_ABS_ERROR, random_vectors=64,
                          scales=[.9, 1, 1.1], integrated_full_journey=False,
                          physical_output_authorised=False), sort_keys=True))
    raise SystemExit(0 if outcome.wasSuccessful() else 1)
