"""Controlled family registration and constraint-first research Pareto choices."""
import math
from engineering.twin_workflow import core

DEFINITIONS = {
    'service-cassette': ('engineering.assembly_design.models', 'steel sheet/RHS and exact bought-out envelopes', 'finite pilot domain; electrical/HVAC/connection qualification open'),
    'bearing-seat': ('engineering.assembly_design.models', 'drilled steel plate and purchased bearing boundary', 'complete reference reaction ledger; ground/resistance/supplier ratings held'),
    'structural-bay': ('engineering.assembly_design.structural_bay', 'stock RHS, sheet floor and bolted equipment interfaces', 'isolated provisional bay; local/modal/fatigue/whole-vehicle exits open'),
    'joints-brackets': ('engineering.integration_programme.joints', 'elastic bolt groups and local connection models', 'generator/resistance benchmark registration required'),
    'composite-panels': ('engineering.design_engine.roof_shell', 'compatible laminate/core/bond/finish bundles', 'hot-wet/fire/insert/contact qualification required; retain known roof failures'),
    'body-panels': ('engineering.assembly_design.panel_adapter', 'matched aluminium/GFRP panel variants and native owned-section companion', 'registered research subset; complete formed panels, attachments, thermal/fire and manufacturing acceptance remain open'),
    'carbody-assembly': ('engineering.assembly_design.carbody_assembly', 'connected underframe, door/window frames, roof, end structure and sheet units', 'provisional complete geometric envelope; bogies, crash, fatigue, weld qualification, door adoption and installed equipment remain open'),
    'civil-assembly': ('engineering.assembly_design.civil_assembly', 'connected foundation, pier, cap, deck, paired track supports and walkway/service units', 'site-specific ground, full reinforcement/prestress, temporary works and connection resistance remain open'),
    'harness': ('engineering.assembly_design.cassette_system', 'exact solder-contact LV reference kits', 'mating routing, ampacity/derating/protection/physical acceptance held'),
    'duct': ('engineering.assembly_design.cassette_system', 'sheet duct and bounded air/heat/moisture model', 'fan/refrigerant maps and calibrated rig required'),
    'battery-enclosure': ('engineering.integration_programme.battery', 'chemistry-specific bought-out battery boundary', 'mechanical/cooling/fire/vent and measured chemistry maps required'),
    'pile-cap-pier': ('engineering.civil_exploration.foundations', 'site-applicable pile/cap/pier forms', 'actual strata/groundwater/settlement/cyclic/calibration required'),
    'station-modules': ('engineering.integration_programme.stations', 'catalogue station structural/service modules', 'new assembly adapter plus site/access/egress/connection qualification required'),
}
COMPANIONS={'body-panels','carbody-assembly','civil-assembly'}


def companion_variables(identity,policy):
    if identity=='body-panels':return {'routes':['stiffened-aluminium','aluminium-sandwich','gfrp-sandwich'],'locations':['side','roof']}
    if identity in {'carbody-assembly','civil-assembly'}:
        from . import carbody_assembly,civil_assembly
        adapter=carbody_assembly if identity=='carbody-assembly' else civil_assembly
        return {'recipes':list(adapter.candidates(policy))}
    return policy['pilots'].get(identity,{}).get('domains',{})


def registry(policy):
    return [dict(id=identity, adapter=adapter, process_domain=domain, limitations=limits,
        registered_for_bounded_design=identity in policy['pilots'] or identity in COMPANIONS,
        variables=companion_variables(identity,policy),
        qualification='exact-source assembly qualification required' if identity in policy['pilots'] or identity in COMPANIONS else 'adapter development and independent benchmarks required',
        execution='finite companion after registered queue' if identity in COMPANIONS else 'registered queue' if identity in policy['pilots'] else 'unregistered',
        required_registration=['frozen architecture/interface/load/material/process domain',
            'source/runtime qualification receipt', 'independent analytical or numerical controls',
            'known-invalid adverse controls', 'manufactured-CAD reconstruction/native confirmation',
            'explicit unresolved and applicability bounds'],
        **core.FLAGS) for identity, (adapter, domain, limits) in DEFINITIONS.items()]


def pareto(rows, objectives=('installed_mass_kg','largest_lift_kg','site_hours','cost')):
    """Never obtain a cheap/light optimum from failed checks or unknown costs.

    Missing objectives permit a partial frontier comparison only against peers
    with exactly the same known-objective mask; no missing-as-zero ranking.
    """
    candidates=[]
    for row in rows:
        checks=row.get('mandatory_checks', {})
        if not checks or any(value is not True for value in checks.values()):
            continue
        if not row.get('id') or not row.get('context_revision'):
            raise ValueError('exact comparable candidate context required')
        mask=tuple(k for k in objectives if row.get(k) is not None)
        if not mask:
            continue
        for k in mask:
            if isinstance(row[k],bool) or not isinstance(row[k],(int,float)) or not math.isfinite(row[k]) or row[k]<0:
                raise ValueError('finite nonnegative objective required')
        candidates.append((row,mask))
    result=[]
    for row,mask in candidates:
        peers=[r for r,m in candidates if m==mask and r['context_revision']==row['context_revision']]
        if not any(all(p[k]<=row[k] for k in mask) and any(p[k]<row[k] for k in mask) for p in peers):
            result.append(dict(candidate=row, compared_objectives=list(mask), unpriced_objectives=[k for k in objectives if k not in mask],
                scope='Research frontier within identical context and known-objective mask; unknown cost/labour remains unranked', **core.FLAGS))
    return sorted(result,key=lambda r:r['candidate']['id'])
