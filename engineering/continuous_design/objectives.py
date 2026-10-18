"""Explicit research trade-offs; inspection coverage is never a minimisation target."""
import json
import math

COUNTS=('rectangular_scrap_m2','setup_count','fixture_count','operation_count','destructive_joint_count','blocked_replacement_count')
SCENARIO=('maximum_lift_mass_kg','onsite_wet_concrete_m3','onsite_operation_count','scenario_onsite_person_hours','scenario_delivery_hours','scenario_work_at_height_hours','scenario_cost_usd')


def metrics(row):
    return json.loads(row['objectives']).get('manufacturing_metrics',{}) if 'objectives' in row.keys() else {}


def number(value):return type(value) in (int,float) and math.isfinite(value)


def values(row):
    return dict(mass=row['mass'],effort=row['effort'],**metrics(row))


def dominates(first,second):
    a,b=values(first),values(second)
    names=['mass','effort',*COUNTS]
    if a.get('comparison_basis_sha256') and a.get('comparison_basis_sha256')==b.get('comparison_basis_sha256'):
        names+=list(SCENARIO)
    if a.get('required_test_scope_sha256') and a.get('required_test_scope_sha256')==b.get('required_test_scope_sha256') and a.get('planned_test_coverage_complete') is True and b.get('planned_test_coverage_complete') is True:
        names.append('inspection_effort_person_hours')
    pairs=[(a.get(name),b.get(name)) for name in names if number(a.get(name)) and number(b.get(name))]
    return bool(pairs) and all(x<=y for x,y in pairs) and any(x<y for x,y in pairs)


def primary_rank(row):
    m=metrics(row)
    def value(key):return m[key] if number(m.get(key)) else float('inf')
    base=(row['mass'] if row['mass'] is not None else float('inf'),row['effort'] if row['effort'] is not None else float('inf'))
    if row['kind']=='civil-kit-study':
        return (value('scenario_onsite_person_hours'),value('scenario_delivery_hours'),value('maximum_lift_mass_kg'),*base)
    return base


def roles(rows,eligible=lambda row:True):
    """Return complementary leaders; no single lightest candidate represents all."""
    predicate=eligible;choices={};labels={'mass':'minimum-modeled-mass','maximum_lift_mass_kg':'smallest-lift',
        'scenario_onsite_person_hours':'least-scenario-onsite-work','scenario_delivery_hours':'earliest-scenario-delivery',
        'scenario_cost_usd':'lowest-complete-input-cost','operation_count':'fewest-declared-operations'}
    for key,label in labels.items():
        candidates=[row for row in rows if number(values(row).get(key))]
        if not candidates:continue
        winner=next((row for row in sorted(candidates,key=lambda row:(values(row)[key],primary_rank(row),row['key'])) if predicate(row)),None)
        if winner is None:continue
        choices.setdefault(winner['key'],dict(row=winner,roles=[]))['roles'].append(label)
    return list(choices.values())


def useful_improvement(current,previous,fraction=.05):
    for key in ('mass',*COUNTS,*SCENARIO,'inspection_effort_person_hours'):
        value=values(current).get(key)
        if not number(value):continue
        peers=[]
        for row in previous:
            m=metrics(row);a=metrics(current)
            if key in SCENARIO and (not a.get('comparison_basis_sha256') or a.get('comparison_basis_sha256')!=m.get('comparison_basis_sha256')):continue
            if key=='inspection_effort_person_hours' and (not a.get('planned_test_coverage_complete') or not m.get('planned_test_coverage_complete') or not a.get('required_test_scope_sha256') or a.get('required_test_scope_sha256')!=m.get('required_test_scope_sha256')):continue
            old=values(row).get(key)
            if number(old):peers.append(old)
        if peers and value<(1-fraction)*min(peers)-1e-9:return True
    return False
