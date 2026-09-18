"""Per-line service screening; aggregate mileage cannot hide an unserved line."""
import math

from .network_readme import _scheduled_daily_train_km


def line_service_screen(design, scenario, observations, minimum=0.90, tolerance=0.002):
    issues = []
    lines = scenario.get('lines', [])
    ids = [row['id'] for row in lines]
    names = [row.get('name', row['id']) for row in lines]
    if not lines or len(set(ids)) != len(ids) or len(set(names)) != len(names):
        issues.append('Missing or ambiguous scenario lines')
    measured = {}
    for row in observations:
        if not isinstance(row, (list, tuple)) or len(row) != 2:
            issues.append('Malformed per-line observation')
            continue
        name, km = row
        if not isinstance(name, str) or name in measured or type(km) not in (int, float) or not math.isfinite(km) or km < 0:
            issues.append('Duplicate or invalid per-line observation')
            continue
        measured[name] = km
    if set(measured) != set(names):
        issues.append('Observed lines differ from the scenario')
    if any(f.get('line') not in ids for f in scenario.get('fleets', [])):
        issues.append('Fleet refers to an unknown line')
    rows = []
    for line, name in zip(lines, names):
        fleets = [f for f in scenario.get('fleets', []) if f.get('line') == line['id']]
        expected = _scheduled_daily_train_km(design, {'fleets': fleets})
        actual = measured.get(name)
        ratio = actual / expected if actual is not None and expected > 0 else None
        passed = ratio is not None and ratio + tolerance >= minimum
        rows.append(dict(line_id=line['id'], line_name=name, scheduled_train_km=expected,
                         observed_train_km=actual, raw_completion_ratio=ratio, passed=passed))
    return dict(schema='osr-line-service-screen/1', passed=not issues and all(r['passed'] for r in rows),
                minimum_completion_ratio=minimum, numerical_tolerance=tolerance, lines=rows, issues=issues,
                scope='Full-window mileage by line; does not establish peak headways, directional or station-level service')


def configured_passenger_capacity(scenario):
    """Expose timetable ceilings without treating them as delivered capacity."""
    capacity = scenario.get('consist', {}).get('passenger_capacity')
    valid_capacity = type(capacity) is int and capacity > 0
    rows = []
    for fleet in scenario.get('fleets', []):
        for window in fleet.get('schedule', []):
            headway = window.get('headway_min')
            valid = valid_capacity and type(headway) in (int, float) and math.isfinite(headway) and headway > 0
            rows.append(dict(line_id=fleet.get('line'), start=window.get('from'), end=window.get('to'),
                             headway_min=headway, passengers_per_train=capacity,
                             configured_passengers_per_hour_per_direction=capacity * 60 / headway if valid else None))
    return dict(schema='osr-configured-passenger-capacity/1', status='open', accepted=False,
                configured_inputs_valid=bool(rows) and all(r['configured_passengers_per_hour_per_direction'] is not None for r in rows),
                windows=rows, remaining=['Observed departures and peak headways by line and direction',
                    'Calibrated section demand and passenger assignment',
                    'Boarding, dwell, crowding and denied-boarding checks', 'Independent operator acceptance'],
                scope='Configured timetable ceiling only; mileage completion is not passenger capacity acceptance')
