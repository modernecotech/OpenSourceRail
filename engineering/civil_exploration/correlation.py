"""Bounded calibration with specimen-separated holdouts and retained evidence."""
from __future__ import annotations
import hashlib
from pathlib import Path
import math
import numpy as np
from scipy.optimize import least_squares
from osr_mech.engineering_definition import fingerprint


UNITS = {'displacement': 'm', 'acceleration': 'm/s2', 'force': 'N',
         'moment': 'N*m', 'strain': '1', 'mass': 'kg', 'rotation': 'rad', 'angular-acceleration':'rad/s2'}


def evidence(reference, root):
    path = (Path(root) / reference['path']).resolve()
    if not path.is_relative_to(Path(root).resolve()) or not path.is_file():
        raise ValueError('correlation evidence must be a retained file within the project')
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != reference['sha256']:
        raise ValueError('correlation source or calibration evidence changed')
    return digest


def calibrate(model, dataset, parameters, predict, *, root, holdout_specimens):
    """Predict(parameters, test) returns values in that test's declared SI unit.

    The forward solver is supplied explicitly, so calibration cannot silently use
    a reduced surrogate instead of the selected vehicle/structural calculation.
    """
    if dataset.get('schema') != 'osr-instrumented-correlation/1':
        raise ValueError('unknown measurement schema')
    if dataset.get('hardware_definition_sha256') != fingerprint(model):
        raise ValueError('measurement configuration does not match the engineering definition')
    if dataset.get('classification') not in ('synthetic-verification', 'physical-measurement'):
        raise ValueError('measurement origin must be explicit')
    tests = dataset['tests']; holdout = set(holdout_specimens)
    if len({t['id'] for t in tests}) != len(tests) or not holdout:
        raise ValueError('unique tests and independent holdout specimens required')
    sources = {}; training = []; validation = []; specimen_serials={}; serial_specimens={}
    for test in tests:
        if test['quantity'] not in UNITS or test['unit'] != UNITS[test['quantity']]:
            raise ValueError('measurement units do not match the declared physical channel')
        time = np.asarray(test['time_s'], dtype=float)
        values = np.asarray(test['values'], dtype=float)
        sigma = np.asarray(test['standard_uncertainty'], dtype=float)
        if time.ndim != 1 or len(time) < 3 or time.shape != values.shape or time.shape != sigma.shape:
            raise ValueError('aligned channel/time/uncertainty arrays required')
        if not np.isfinite(np.concatenate([time, values, sigma])).all() or np.any(np.diff(time) <= 0) or np.any(sigma <= 0):
            raise ValueError('ordered timestamps, finite samples and positive uncertainty required')
        if not test['specimen_id'] or not test['serial'] or not test['design_revision']:
            raise ValueError('specimen, serial and design revision must be retained')
        specimen=test['specimen_id'];serial=test['serial']
        if specimen in specimen_serials and specimen_serials[specimen]!=serial:
            raise ValueError('one calibration/holdout specimen identity cannot refer to different serials')
        if serial in serial_specimens and serial_specimens[serial]!=specimen:
            raise ValueError('one serial cannot be relabelled as independent calibration/holdout specimens')
        specimen_serials[specimen]=serial;serial_specimens[serial]=specimen
        if test['design_revision'] != model['revision']:
            raise ValueError('measurement revision differs from the model')
        for reference in (test['source'], test['calibration_record']):
            sources[reference['path']] = evidence(reference, root)
        (validation if test['specimen_id'] in holdout else training).append(test)
    if not training or not validation or holdout - {t['specimen_id'] for t in validation}:
        raise ValueError('both calibration and independent holdout specimens required')
    if not parameters or len({p['name'] for p in parameters}) != len(parameters):
        raise ValueError('unique bounded calibration parameters required')
    initial = np.asarray([p['initial'] for p in parameters], dtype=float)
    lower = np.asarray([p['minimum'] for p in parameters], dtype=float)
    upper = np.asarray([p['maximum'] for p in parameters], dtype=float)
    if not np.isfinite(np.concatenate([initial, lower, upper])).all() or np.any(lower >= upper) or np.any(initial < lower) or np.any(initial > upper):
        raise ValueError('finite parameter bounds must contain the initial values')
    def forward(x, test):
        values = np.asarray(predict(dict(zip([p['name'] for p in parameters], x)), test), dtype=float)
        if values.shape != np.asarray(test['values']).shape or not np.isfinite(values).all():
            raise ValueError('forward prediction does not cover the measured channel')
        return values
    def residual(x):
        return np.concatenate([(forward(x, t)-t['values'])/np.asarray(t['standard_uncertainty']) for t in training])
    fit = least_squares(residual, initial, bounds=(lower, upper), x_scale=upper-lower,
                        max_nfev=300, ftol=1e-10, xtol=1e-10, gtol=1e-10)
    singular = np.linalg.svd(fit.jac, compute_uv=False)
    rank = int(np.linalg.matrix_rank(fit.jac))
    dof = len(fit.fun)-len(parameters)
    covariance = None
    if rank == len(parameters) and dof > 0:
        covariance = (np.linalg.inv(fit.jac.T@fit.jac)*(fit.fun@fit.fun)/dof).tolist()
    rows = []
    for test in validation:
        prediction = forward(fit.x, test);delta = prediction-np.asarray(test['values'])
        normalised = delta/np.asarray(test['standard_uncertainty'])
        rows.append(dict(test_id=test['id'], specimen_id=test['specimen_id'], prediction=prediction.tolist(),
            residual=delta.tolist(), unit=test['unit'], rmse=float(np.sqrt(np.mean(delta**2))),
            bias=float(np.mean(delta)), standardised_rmse=float(np.sqrt(np.mean(normalised**2))),
            measurement_95_percent_band=[[float(y-1.96*s), float(y+1.96*s)]
                for y, s in zip(test['values'], test['standard_uncertainty'])],
            acceptance_limit=None, project_requirement=None, accepted=False))
    return dict(schema='osr-correlation-result/1', hardware_definition_sha256=fingerprint(model),
        dataset_sha256=fingerprint(dataset), evidence_sha256=sources,
        fitted_parameters=dict(zip([p['name'] for p in parameters], map(float, fit.x))),
        optimisation_converged=bool(fit.success), identifiable=rank == len(parameters),
        sensitivity_rank=rank, sensitivity_singular_values=singular.tolist(), parameter_covariance=covariance,
        covariance_basis='local linearised weighted residual variance; no physical acceptance',
        training_tests=[t['id'] for t in training], holdout_tests=rows,
        physical_measurements_used=dataset['classification'] == 'physical-measurement',
        physical_validation=False, engineering_released=False,
        open_gates=['adopted project residual/error limits', 'independent reviewer', 'model discrepancy and extrapolation assessment'])


def protocols(model):
    """Executable evidence checklist tied to the exact frozen configuration."""
    levels = [
        ('part', ['dimensions and thickness', 'weighing and CG', 'material coupons', 'NDT'],
         ['calibrated gauges/scales', 'material batch', 'inspection characteristic limits']),
        ('subassembly', ['joint preload', 'proof load and slip', 'compliance and free motion', 'interference'],
         ['calibrated load cell/displacement', 'joint serial', 'approved safe test load']),
        ('train', ['wheel weighing empty/nominal/crush/uneven', 'braking', 'ride and articulation'],
         ['wheel-force and acceleration calibration', 'approved test route/speeds', 'safe stop envelope']),
        ('train-infrastructure', ['static span influence line', 'repeated passages', 'two-track passages', 'holdout passages'],
         ['synchronised clocks', 'span/soil instrumentation', 'adopted limits', 'independent holdout plan'])]
    return dict(schema='osr-engineering-test-protocols/1', hardware_definition_sha256=fingerprint(model),
        revision=model['revision'], asset_id=model['asset_id'],
        levels=[dict(level=level, tests=tests, required_records=required,
                     stop_conditions=['instrument saturation or calibration expiry', 'approved test envelope exceeded',
                                      'contact loss/slip, damage or abnormal motion beyond the approved stop limit'],
                     adopted_standard=None, project_limits=None, status='awaiting-authorised-test-inputs')
                for level, tests, required in levels],
        physical_tests_performed=False, engineering_released=False)
