"""Conditional mass-position and two-support statics for the selected car.

This analytical sensitivity uses already-accounted residuals once, at synthetic
account centroid intervals. It is neither installed mass/CG nor axle loading,
and it cannot justify engineering acceptance or operation.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_ID = '756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'
SELECTION_ID = '8e5905bc7c81d6177bbaafde81ab3a5f8cc54947c4923eb4493949566ac85cdc'
WORKSHEET_ID = '849009c782d593c10894c02689f9a6deea269c5fb485345a75174238c2c0ad0c'
LEDGER_MANIFEST_ID = 'e8a1fab1d7bcc6c7d2d59c053639e103195c5aab5a23726ad4151ca55e4d8edd'
RESERVE_MANIFEST_ID = 'b17bbeb8c967b12a66be618fb7643e7177e8b9d8df9bf8361dbf0238d9239e3a'
RESERVE_RESULT_ID = 'f37b7de0af9666240ce7a1e9c44f362498a49877f344af3e017fefff6bb7fb9f'
BRIEF_OBJECT_ID = '46d42822c15fbe020e2eaa6e61f71f502ec9be6229f22a35093b666953190b2c'
GRAVITY_M_S2 = 9.80665
MAX_ABS_CENTROID_M = 1_000_000.0  # numerical-domain guard, not a physical envelope
LEDGER = 'docs/design-engine/mass-reconciliation/current/'
RESERVE = 'docs/design-engine/mass-reserve-sensitivity/current/'
BRIEF = 'engineering/station_rail/brief.toml'
PRODUCER = 'engineering/design_search/installed_mass_cg.py'
# Immutable published-input bytes are external pins, not hashes inferred from
# data presented by the caller. Revisions require a reviewed source epoch.
INPUT_SHA256 = {
    LEDGER+'manifest.json': '7df5a1f863ad92d7df69a941cd2ca31d695385cca99e601a98c8f002886e0a5d',
    LEDGER+'summary.json': 'cf80d76b75156b34c16e45fd97d445e1a769b92cc38e8d68859c0b6d0111ac50',
    LEDGER+'mass-closure-worksheet.json.gz': 'b8f107138ea90867414ade17a35026bfa70a8f93b55d4e27ab26527fcd16b277',
    RESERVE+'manifest.json': 'edf023516b5932fc1fe7bbc71df309b520eb121faaf9f286d6bc40bf81b4c795',
    RESERVE+'result.json': '26fc807e80580839140ca37b3079041e8988fff13d791db7a6a3e079ca72cb8d',
    BRIEF: 'a23e432d43a3f5648b4d31c4e96e9b87dbc6742b422389a4ce707c275453cad9',
}
CASES = ('low', 'base', 'high')
FLAGS = dict(installed_mass_complete=False, engineering_accepted=False,
             physical_accepted=False, manufacturing_release=False, operating_release=False)


def _encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def _id(value):
    return hashlib.sha256(_encoded(value)).hexdigest()


def _number(value, label):
    if type(value) not in (int, float):
        raise ValueError(label+' must be a finite number')
    try:
        number = float(value)
    except OverflowError as exc:
        raise ValueError(label+' must be a finite number') from exc
    if not math.isfinite(number):
        raise ValueError(label+' must be a finite number')
    return number


def _near(a, b):
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-7)


def load_inputs(root=ROOT):
    """Read only externally pinned published bytes, not self-authenticating hashes."""
    root = Path(root)
    raw = {}
    for name, expected in INPUT_SHA256.items():
        data = (root/name).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError('Pinned source differs: '+name)
        raw[name] = data
    return dict(manifest=json.loads(raw[LEDGER+'manifest.json']),
                summary=json.loads(raw[LEDGER+'summary.json']),
                worksheet=json.loads(gzip.decompress(raw[LEDGER+'mass-closure-worksheet.json.gz'])),
                reserve_manifest=json.loads(raw[RESERVE+'manifest.json']),
                reserve=json.loads(raw[RESERVE+'result.json']),
                brief=tomllib.loads(raw[BRIEF].decode()))


def _identity(record, field, expected):
    if record.get(field) != expected:
        raise ValueError(field+' differs from the pinned selected reference')
    copy = {k:v for k,v in record.items() if k != field}
    if _id(copy) != expected:
        raise ValueError(field+' payload does not reproduce its identity')


def _inputs(data):
    try:
        manifest, summary, worksheet, rm, reserve, brief = (data[k] for k in
            ('manifest','summary','worksheet','reserve_manifest','reserve','brief'))
        _identity(manifest, 'manifest_id', LEDGER_MANIFEST_ID)
        _identity(worksheet, 'worksheet_id', WORKSHEET_ID)
        _identity(rm, 'manifest_id', RESERVE_MANIFEST_ID)
        _identity(reserve, 'result_id', RESERVE_RESULT_ID)
        for obj in (manifest, summary, worksheet, reserve):
            if obj['candidate_id'] != CANDIDATE_ID or obj['selection_id'] != SELECTION_ID:
                raise ValueError('Candidate or selection identity differs')
        if _id(summary) != INPUT_SHA256[LEDGER+'summary.json'] or _id(brief) != BRIEF_OBJECT_ID:
            raise ValueError('Summary or parsed brief differs from pinned input')
        if (summary['closure_worksheet_id'] != WORKSHEET_ID or reserve['worksheet_id'] != WORKSHEET_ID
                or reserve['ledger_manifest_id'] != LEDGER_MANIFEST_ID or rm['result_id'] != RESERVE_RESULT_ID
                or rm['files_sha256']['result.json'] != INPUT_SHA256[RESERVE+'result.json']
                or manifest['files_sha256']['mass-closure-worksheet.json.gz'] != INPUT_SHA256[LEDGER+'mass-closure-worksheet.json.gz']):
            raise ValueError('Mass worksheet, reserve or source manifest relationship differs')
        if (worksheet['unknown_is_zero'] is not False or summary['installed_mass_complete'] is not False
                or reserve['installed_mass_complete'] is not False):
            raise ValueError('Unknown installation state cannot be promoted')
        v, s = brief['vehicle'], brief['support']
        if v['body_length_m'] != 17.0 or s['bogie_centres_x_m'] != [-6.4, 6.4]:
            raise ValueError('Selected 17 m car and support interfaces required')
        closures = [r for r in worksheet['rows'] if r['record_kind'] == 'account-closure']
        geometry = [r for r in worksheet['rows'] if r['record_kind'] == 'candidate-geometry-occurrence']
        if len(closures) != summary['account_row_count'] or len(geometry) != summary['located_geometry_occurrence_count']:
            raise ValueError('Incomplete selected-candidate worksheet')
        accounts, account_geometry = {}, {}
        for row in closures:
            name = row['account_id']
            if not isinstance(name,str) or not name or name in accounts:
                raise ValueError('Duplicate or missing account identity')
            acc = _number(row['accounted_source_mass_kg'],name+' source mass')
            geo = _number(row['candidate_geometry_mass_kg'],name+' geometry mass')
            mass = _number(row['accounting_residual_kg'],name+' residual')
            if min(acc,geo,mass) < -1e-8 or not _near(acc,geo+mass):
                raise ValueError('Account geometry and reserve do not reconcile')
            account_geometry[name] = geo
            if mass > 1e-9: accounts[name] = mass
            else: accounts[name] = 0.0
        positive = {name:mass for name,mass in accounts.items() if mass>0}
        reserve_rows = {}
        for row in reserve['reserve_accounts']:
            name = row['account_id']
            if name in reserve_rows or name not in positive:
                raise ValueError('Duplicate or unexpected residual account')
            reserve_rows[name] = row
            if row['added_instead_of_replaced'] is not False or not _near(_number(row['existing_residual_kg'],'residual'),positive[name]):
                raise ValueError('Reserve must replace the same source account')
        if set(reserve_rows) != set(positive) or len(positive) != summary['closure_worksheet_account_residual_count']:
            raise ValueError('Missing residual account')
        sensitivity = reserve['sensitivity_cases']
        if len(sensitivity) != len(CASES) or {r['name'] for r in sensitivity} != set(CASES):
            raise ValueError('Exactly one low/base/high mass case is required')
        for case in sensitivity:
            factor = _number(case['reserve_factor'],'reserve factor')
            if factor <= 0 or (case['name'] == 'base' and factor != 1.0):
                raise ValueError('Positive factors and exact base replacement required')
            for name, row in reserve_rows.items():
                if not _near(_number(row['scenario_reserve_kg'][case['name']],'scenario reserve'),
                             positive[name]*factor):
                    raise ValueError('Each scenario must replace each matching account exactly once')
        ids = set()
        gm, moment = [], []
        geometry_by_account = {name: [] for name in accounts}
        for row in geometry:
            occurrence = row['occurrence_id']
            if not occurrence or occurrence in ids or row['account_id'] not in accounts:
                raise ValueError('Duplicate or missing located geometry occurrence')
            ids.add(occurrence)
            mass = _number(row['candidate_geometry_mass_kg'],'geometry mass')
            x = _number(row['candidate_geometry_centroid_m'][0],'geometry x')
            if mass <= 0: raise ValueError('Geometry mass must be positive')
            gm.append(mass);moment.append(mass*x)
            geometry_by_account[row['account_id']].append(mass)
        if any(not _near(math.fsum(geometry_by_account[name]), expected)
               for name, expected in account_geometry.items()):
            raise ValueError('Geometry occurrences do not reconcile to their own account')
        located, located_moment = math.fsum(gm), math.fsum(moment)
        residual = math.fsum(positive.values())
        if (not _near(located,summary['located_geometry_mass_kg'])
                or not _near(located, reserve['located_geometry_mass_kg_per_car'])
                or not _near(located_moment/located,summary['located_material_CG_m'][0])
                or not _near(residual,summary['residual_reference_or_unlocated_mass_kg'])
                or not _near(located+residual,summary['accounted_tare_kg_per_car'])
                or not _near(located+residual,reserve['accounted_tare_mass_kg_per_car'])):
            raise ValueError('Located or residual mass does not reconcile to source')
        return positive, reserve_rows, located, located_moment, s['bogie_centres_x_m'], v['body_length_m']
    except (KeyError, TypeError, IndexError) as exc:
        raise ValueError('Incomplete or malformed source data') from exc


def _evaluate_data(data, intervals=None):
    """Private arithmetic helper; its return contains no source authentication.

    Unspecified account intervals default to the entire 17 m car length. The
    intervals are scenario inputs, not demonstrated geometry or guaranteed
    physical bounds. Values may extend beyond the body for sensitivity tests,
    within the explicitly declared 1,000 km numerical-domain guard.
    """
    positive, rows, located, located_moment, supports, length = _inputs(data)
    if intervals is None: intervals = {}
    if not isinstance(intervals,dict) or set(intervals)-set(positive):
        raise ValueError('Intervals must map existing positive account IDs')
    spaces = {}
    for name in sorted(positive):
        span = intervals.get(name,[-length/2,length/2])
        if not isinstance(span,(list,tuple)) or len(span)!=2:
            raise ValueError('Each centroid interval must have two endpoints')
        lo,hi=(_number(span[0],name+' interval'),_number(span[1],name+' interval'))
        if lo>hi: raise ValueError('Centroid interval endpoints must be ordered')
        if max(abs(lo),abs(hi))>MAX_ABS_CENTROID_M:
            raise ValueError('Centroid interval exceeds numerical-domain guard')
        spaces[name] = dict(x_min_m=lo,x_max_m=hi,
            basis='caller supplied synthetic hypothesis' if name in intervals else 'synthetic full car-length default')
    left,right = map(float,supports); width=right-left
    cases=[]
    for case in CASES:
        account_mass={name:_number(row['scenario_reserve_kg'][case],case+' mass') for name,row in rows.items()}
        if any(m<=0 for m in account_mass.values()): raise ValueError('Reserve mass must be positive')
        reserve=math.fsum(account_mass.values()); mass=located+reserve
        source_cases=[r for r in data['reserve']['sensitivity_cases'] if r['name']==case]
        if len(source_cases)!=1 or not _near(mass,source_cases[0]['scenario_tare_mass_kg_per_car']):
            raise ValueError('Scenario must replace every named account exactly once')
        endpoints=[]
        for side in ('min','max'):
            position='x_'+side+'_m'
            residual_moment=math.fsum(account_mass[name]*spaces[name][position] for name in account_mass)
            moment=located_moment+residual_moment
            cg=moment/mass; weight=mass*GRAVITY_M_S2
            rr=GRAVITY_M_S2*(moment-left*mass)/width; ll=weight-rr
            endpoints.append(dict(x_cg_m=cg,
                located_geometry_first_moment_kg_m=located_moment,
                residual_first_moment_kg_m=residual_moment,scenario_first_moment_kg_m=moment,
                left_bogie_force_N=ll,right_bogie_force_N=rr,
                force_residual_N=ll+rr-weight,
                moment_residual_N_m=rr*width-GRAVITY_M_S2*(moment-left*mass)))
        cases.append(dict(case=case,located_geometry_mass_kg=located,
            residual_replacement_mass_kg=reserve,account_residual_mass_kg=account_mass,
            scenario_accounted_mass_kg=mass,gravity_weight_N=mass*GRAVITY_M_S2,
            lower_cg_endpoint=endpoints[0],upper_cg_endpoint=endpoints[1],
            x_cg_interval_m=[endpoints[0]['x_cg_m'],endpoints[1]['x_cg_m']],
            left_bogie_force_interval_N=[endpoints[1]['left_bogie_force_N'],endpoints[0]['left_bogie_force_N']],
            right_bogie_force_interval_N=[endpoints[0]['right_bogie_force_N'],endpoints[1]['right_bogie_force_N']],
            possible_negative_reaction=min(endpoints[1]['left_bogie_force_N'],endpoints[0]['right_bogie_force_N'])<0))
    result=dict(schema='osr-selected-mass-support-sensitivity/1',candidate_id=CANDIDATE_ID,
        selection_id=SELECTION_ID,worksheet_id=WORKSHEET_ID,ledger_manifest_id=LEDGER_MANIFEST_ID,
        reserve_manifest_id=RESERVE_MANIFEST_ID,reserve_result_id=RESERVE_RESULT_ID,
        coordinate_frame='x along car, origin at nominal body centre; z=0 top of rail',
        gravity_m_s2=GRAVITY_M_S2,bogie_centres_x_m=[left,right],
        maximum_absolute_centroid_m=MAX_ABS_CENTROID_M,account_centroid_intervals=spaces,
        scenario_assumptions=['Each account is one point mass at an independently variable assumed centroid',
            'Located geometry masses and centroids are nominal, not verified installed occurrences',
            'Synthetic account intervals need not represent feasible placement or guaranteed physical bounds',
            'Two vertical point supports, rigid whole-car static equilibrium; no suspension/equalisation mechanics',
            'Existing cross-account overlap is unresolved; totals are conditional accounting cases, not physical mass bounds'],
        account_overlap_resolved=False,complete_installed_mass_kg=None,installed_cg_m=None,
        axle_reactions_N=None,release_or_selection_effect=False,cases=cases,**FLAGS)
    return result


def evaluate(intervals=None, *, root=ROOT):
    """Authenticate exact pinned bytes and source, then evaluate assumed positions."""
    root = Path(root)
    executing = Path(__file__).resolve()
    producer = root/PRODUCER
    source_hash = hashlib.sha256(executing.read_bytes()).hexdigest()
    if hashlib.sha256(producer.read_bytes()).hexdigest() != source_hash:
        raise ValueError('Executing producer differs from declared source root')
    data = load_inputs(root)
    result = _evaluate_data(data, intervals)
    if (hashlib.sha256(executing.read_bytes()).hexdigest() != source_hash
            or hashlib.sha256(producer.read_bytes()).hexdigest() != source_hash):
        raise ValueError('Executing producer changed during evaluation')
    result.update(source_sha256=dict(INPUT_SHA256),producer=PRODUCER,producer_sha256=source_hash,
        input_authentication='Exact pinned input bytes checked before evaluation; executing and declared-root producer bytes checked before and after evaluation')
    result['evaluation_id']=_id(result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--intervals-json',type=Path,help='Optional JSON object mapping residual account IDs to [xmin,xmax] m')
    args=p.parse_args()
    intervals=json.loads(args.intervals_json.read_text()) if args.intervals_json else None
    print(json.dumps(evaluate(intervals),indent=2,sort_keys=True,allow_nan=False))


if __name__=='__main__': main()
