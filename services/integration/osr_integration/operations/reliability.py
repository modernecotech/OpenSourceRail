"""Exposure/failure analytics and source-bound, held-out degradation calibration."""
import math
import copy
from .contracts import digest, finite, integer, records
from ..config import identifier


def exposure(readings, resets):
    """Monotonic lifetime meter; replacement/reset requires its approved record."""
    rows = sorted(readings, key=lambda r: r['at_s'])
    if not rows: return None
    reset_by_time = {r['at_s']: r for r in resets}
    if len(reset_by_time) != len(resets): raise ValueError('Duplicate meter reset time')
    total = 0
    used_resets = set()
    for row in rows:
        integer(row['at_s'], 0, 10**12); finite(row['value'], 0, 1e12)
    if len({r['at_s'] for r in rows}) != len(rows): raise ValueError('Duplicate meter timestamp')
    for a, b in zip(rows, rows[1:]):
        delta = b['value'] - a['value']
        reset = reset_by_time.get(b['at_s'])
        if delta < 0 or reset is not None:
            if not reset or reset.get('approved') is not True or not reset.get('record'):
                raise ValueError('Decreasing meter requires approved reset/replacement')
            if reset.get('before') != a['value'] or reset.get('after') != b['value']:
                raise ValueError('Meter reset does not bind before/after readings')
            delta = finite(reset.get('increment'), 0, 1e12)
            used_resets.add(b['at_s'])
        total += delta
    if used_resets != reset_by_time.keys(): raise ValueError('Meter reset is outside observed adjacent readings')
    return total


def analyse(data):
    input_sha = digest(data)
    data = copy.deepcopy(data)
    assets = records(data.get('assets'), 'reliability assets', 1000)
    total_km = 0; km_known = True; failures = 0; durations = []; open_failures = 0; by_fault = {}
    periods = data.pop('periods', [])
    trends = []
    for period in records(periods, 'reliability periods', 100).values():
        start = integer(period['start_s'], 0, 10**12); end = integer(period['end_s'], start + 1, 10**12)
        subset = copy.deepcopy(data)
        for asset in subset['assets']:
            for meter, resets in [('km', 'km_resets'), ('cycles', 'cycle_resets')]:
                asset[meter] = [r for r in asset.get(meter, []) if start <= r['at_s'] <= end]
                asset[resets] = [r for r in asset.get(resets, []) if start < r['at_s'] <= end]
            asset['failures'] = [r for r in asset.get('failures', []) if start <= r['failed_at_s'] < end]
        subset['analysis_start_s'] = start; subset['analysis_end_s'] = end
        report = analyse(subset)
        trends.append(dict(id=period['id'], start_s=start, end_s=end, mdbf_km=report['mdbf_km'], mttr_hours=report['mttr_hours'], failures=report['failures'], exposure_complete=report['total_exposure_km'] is not None))
    for asset in assets.values():
        km = exposure(asset.get('km', []), asset.get('km_resets', []))
        readings = asset.get('km', [])
        if km is None: km_known = False
        else: total_km += km
        if readings:
            start = min(r['at_s'] for r in readings); end = max(r['at_s'] for r in readings)
            if any(not start <= f['failed_at_s'] <= end for f in asset.get('failures', [])): km_known = False
            if data.get('analysis_start_s', start) != start or data.get('analysis_end_s', end) != end: km_known = False
        cycles = exposure(asset.get('cycles', []), asset.get('cycle_resets', []))
        incidents = records(asset.get('failures', []), 'failures', 10000)
        for fault in incidents.values():
            if not fault.get('fault_code'): raise ValueError('Controlled fault code required')
            integer(fault['failed_at_s'], 0, 10**12)
            if fault.get('restored_at_s') is not None:
                restored = integer(fault['restored_at_s'], fault['failed_at_s'], 10**12)
                durations.append(restored - fault['failed_at_s'])
            else: open_failures += 1
            failures += 1
            by_fault[fault['fault_code']] = by_fault.get(fault['fault_code'], 0) + 1
        asset['exposure_km'] = km; asset['exposure_cycles'] = cycles
    result = dict(schema='osr-reliability/1', failures=failures, open_failures=open_failures,
        repaired_failures=len(durations), total_exposure_km=total_km if km_known else None,
        mdbf_km=total_km / failures if failures and km_known else None,
        mttr_hours=sum(durations) / len(durations) / 3600 if durations else None,
        failure_free_exposure_km=total_km if km_known and not failures else None,
        fault_codes=by_fault, assets=list(assets.values()), trends=trends,
        note='No failures gives observed failure-free exposure, not infinite MDBF; MTTR excludes open incidents.')
    result['input_sha256'] = input_sha
    return result


def estimate(samples, threshold):
    """Linear degradation estimate, with an explicit scope and no fabricated RUL."""
    if not isinstance(samples, list) or len(samples) > 10000: raise ValueError('Condition samples must be a bounded list')
    for row in samples:
        integer(row['at_s'], 0, 10**12); finite(row['value'], -1e12, 1e12)
    finite(threshold, -1e12, 1e12)
    if len(samples) < 3: return dict(status='insufficient-data', remaining_s=None)
    points = sorted(samples, key=lambda s: s['at_s'])
    if len({r['at_s'] for r in points}) != len(points): raise ValueError('Duplicate condition timestamp')
    for r in points:
        integer(r['at_s'], 0, 10**12); finite(r['value'], -1e12, 1e12)
    finite(threshold, -1e12, 1e12)
    origin = points[0]['at_s']; xs = [r['at_s'] - origin for r in points]; ys = [r['value'] for r in points]
    mx = sum(xs) / len(xs); my = sum(ys) / len(ys)
    denom = sum((x - mx)**2 for x in xs)
    if not denom: return dict(status='insufficient-time-span', remaining_s=None)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom
    if ys[-1] >= threshold: return dict(status='threshold-reached', remaining_s=0, slope_per_s=slope)
    if slope <= 0: return dict(status='no-rising-degradation-trend', remaining_s=None, slope_per_s=slope)
    intercept = my - slope * mx
    remaining = (threshold - intercept) / slope - xs[-1]
    if remaining < 0: return dict(status='inconsistent-fit', remaining_s=None, slope_per_s=slope)
    error = math.sqrt(sum((y - (intercept + slope*x))**2 for x, y in zip(xs, ys)) / len(xs))
    return dict(status='estimated', remaining_s=remaining, slope_per_s=slope, residual_rmse=error,
        remaining_s_sensitivity=[max(0, remaining - 2*error/slope), remaining + 2*error/slope],
        sensitivity_basis='plus/minus twice residual RMSE divided by trend slope; not a calibrated confidence interval',
        method='linear-degradation-to-declared-threshold', last_at_s=points[-1]['at_s'])


def calibrate(data):
    training = records(data.get('training'), 'training assets', 1000)
    held_out = records(data.get('held_out'), 'held-out assets', 1000)
    if training.keys() & held_out.keys(): raise ValueError('Asset leakage between training and held-out data')
    if data.get('direction') != 'rising' or not isinstance(data.get('unit'), str) or not data['unit']:
        raise ValueError('Calibration requires rising degradation with exact units')
    threshold = finite(data.get('threshold'), -1e12, 1e12)
    warning = integer(data.get('warning_horizon_s'), 1, 10**12)
    minimum = integer(data.get('minimum_assets', 3), 2, 1000)
    minimum_lead = finite(data.get('minimum_lead_s', 0), 0, warning)
    max_mae = finite(data.get('maximum_mae_s'), 0, 10**12)
    max_false = finite(data.get('maximum_false_alert_rate'), 0, 1)
    training_errors = []; validation_errors = []; false_alerts = 0; negatives = 0; leads = []; misses = 0
    for partition, rows, errors in [('training', training, training_errors), ('held-out', held_out, validation_errors)]:
        for row in rows.values():
            if row.get('unit') != data['unit'] or row.get('asset_family') != data.get('asset_family'):
                raise ValueError('Calibration unit/asset-family mismatch')
            samples = row.get('samples', [])
            result = estimate(samples, threshold)
            if result['status'] != 'estimated':
                raise ValueError('Calibration requires valid pre-failure degradation samples')
            last = result['last_at_s']; predicted = last + result['remaining_s']
            failure = row.get('failed_at_s')
            if failure is not None:
                integer(failure, last + 1, 10**12); errors.append(abs(predicted - failure))
                if partition == 'held-out':
                    if result['remaining_s'] <= warning: leads.append(failure - last)
                    else: misses += 1
            elif partition == 'held-out':
                end = integer(row.get('observed_until_s'), last + warning, 10**12)
                negatives += 1
                if result['remaining_s'] <= warning and predicted <= end: false_alerts += 1
    enough = len(training_errors) >= minimum and len(validation_errors) >= minimum and negatives >= minimum
    mae = sum(validation_errors) / len(validation_errors) if validation_errors else None
    false_rate = false_alerts / negatives if negatives else None
    lead = min(leads) if leads else None
    passed = bool(enough and mae <= max_mae and false_rate <= max_false and misses == 0 and lead is not None and lead >= minimum_lead)
    result = dict(schema='osr-rul-calibration/1', input_sha256=digest(data),
        asset_family=data.get('asset_family'), unit=data['unit'], threshold=threshold,
        training_assets=sorted(training), held_out_assets=sorted(held_out),
        held_out_mae_s=mae, false_alert_rate=false_rate, minimum_observed_lead_s=lead,
        missed_failure_alerts=misses, validation_passed=passed,
        status='validated-research-model' if passed else 'insufficient-data-or-validation-failed',
        commissioned_predictive_maintenance=False, creates_work_order=False)
    result['sha256'] = digest(result)
    return result


def forecast(data):
    identifier(data.get('asset_id'))
    calibration = calibrate(data['calibration'])
    if data.get('unit') != calibration['unit'] or data.get('asset_family') != calibration['asset_family']:
        raise ValueError('Forecast calibration unit/asset-family mismatch')
    result = estimate(data.get('samples', []), calibration['threshold'])
    return dict(schema='osr-rul-forecast/1', asset_id=data['asset_id'], estimate=result,
        calibration=calibration, maintenance_review_recommended=bool(calibration['validation_passed'] and (result['status'] == 'threshold-reached' or result['status'] == 'estimated' and result['remaining_s'] <= data['calibration']['warning_horizon_s'])),
        predictive_model_commissioned=False, creates_work_order=False)
