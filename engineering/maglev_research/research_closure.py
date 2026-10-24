"""Join bounded research results to the complete, still-open qualification plan.

This separate workstream preserves the original source-bound design packets.
Passing this publication check means the research is reproducible and current;
it cannot adopt a candidate or close a physical qualification task.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import gzip
import json
from pathlib import Path
import tomllib

from . import dynamics_readiness, magnetic_research_closure, propulsion_research, readme_context
from engineering.ferrite_maglev import qualification

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'docs/design-engine/ferrite-maglev/research-closure'
OPTIMISATION = OUTPUT / 'magnetic-optimisation.json'
FLAGS = dict(configuration_adopted=False, design_complete=False,
             engineering_accepted=False, physical_validation=False,
             manufacturing_release=False, physical_release=False)
GROUP_OWNERS = {
    'body-joints-hardpoints': 'Vehicle structures and equipment',
    'magnetic-circuit': 'Magnetic assemblies and maps',
    'station-motor-interfaces': 'Station propulsion and receiving brakes',
    'civil-strength-stages': 'Civil design and construction',
    'energy-services': 'Services, storage and charging',
    'control-protection': 'Controls, target hardware and protection',
    'station-egress': 'Stations, access and evacuation',
    'industrial-recovery-assurance': 'Manufacturing, economics and independent assurance',
}


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()


def task_order(tasks):
    pending = {row['id']: set(row['prerequisites']) for row in tasks}
    if not pending or len(pending) != len(tasks):
        raise ValueError('unique nonempty task inventory required')
    if any(not deps <= pending.keys() for deps in pending.values()):
        raise ValueError('unknown task prerequisite')
    ordered = []
    while pending:
        ready = sorted(identity for identity, deps in pending.items() if not deps)
        if not ready:
            raise ValueError('cyclic task dependencies')
        ordered.extend(ready)
        pending = {identity: deps - set(ready) for identity, deps in pending.items() if identity not in ready}
    return ordered


def check_optimisation(value, root=ROOT):
    return magnetic_research_closure.validate_optimisation(value, root)


def service_summary(value):
    return {key: value[key] for key in ('parent_configuration_sha256', 'assumptions',
        'coverage', 'grade_necessary_force_screen', 'ranking', 'recommended_research_specification')}


def validate_design_round(support, nominal, heavier, geometry, intent):
    identity = support['parent_configuration_sha256']
    if {identity, nominal['parent_configuration_sha256'], heavier['parent_configuration_sha256'],
            geometry['parent_configuration_sha256']} != {identity}:
        raise ValueError('mixed second-round parent configurations')
    contract = support['recommended_next_design_contract']
    if heavier['assumptions']['aw3_mass_kg_per_car'] != contract['controlled_aw3_material_lower_bound_kg_per_car']:
        raise ValueError('service and support proposal masses differ')
    if heavier['comparison_mass_support_binding']['proposed_case_id'] != contract['proposed_case_id']:
        raise ValueError('service and support proposal identities differ')
    for value in (support, nominal, heavier, geometry, intent):
        if value.get('configuration_adopted') is not False:
            raise ValueError('research comparison cannot adopt a specification')
    if any(value.get('physical_validation') is not False for value in (support, nominal, heavier, geometry)):
        raise ValueError('numerical comparisons cannot confer physical validation')
    if contract['release_authorised'] is not False or geometry['complete_installed_carrier_fit'] is not False:
        raise ValueError('unmeasured guidance and carrier stock cannot become installed acceptance')
    comparison = intent['service_comparison']
    a = nominal['assumptions']
    for key, name in (('formation_options', 'formation_options'), ('speed_caps_m_s', 'speed_caps_m_s'),
                      ('station_spacings_m', 'spacings_m'), ('dwell_candidates_s', 'dwells_s'),
                      ('charger_candidates_kw_per_car', 'chargers_kw_per_car')):
        if comparison[key] != a[name]:
            raise ValueError('declared research service domain differs: ' + key)
    if comparison['reference_normal_capacity_passengers_hour_direction'] != a['reference_aw2_throughput_floor_pph']:
        raise ValueError('normal passenger capacity floor changed')
    screens = intent['unchanged_magnetic_screens']
    for declared, actual in (('support_peak_load_factor', 'adverse_lift_aw3_factor'),
            ('current_limit_a', 'current_limit_a'),
            ('continuous_current_density_a_mm2', 'current_density_limit_a_mm2'),
            ('steel_field_limit_t', 'field_limit_t'),
            ('copper_temperature_limit_c', 'maximum_copper_c'), ('coil_fill_limit', 'coil_fill_limit')):
        if screens[declared] != support['fixed_constraints'][actual]:
            raise ValueError('declared unchanged magnetic screen differs: ' + declared)
    if screens['limits_are_independently_qualified'] is not False:
        raise ValueError('research limits cannot become independently qualified')
    if geometry['dynamics_rerun_ready'] is not False:
        raise ValueError('stock geometry cannot confer current-based dynamics readiness')
    return dict(design_intent=intent, support=dict(
        executed_joint_model_cases=support['executed_joint_model_cases'],
        nominal_joint_passes=support['nominal_joint_passes'],
        simultaneous_survivor_count=support['simultaneous_survivor_count'],
        original_topology_survivors=support['original_topology_survivors'],
        sensitivity_topology_survivors=support['sensitivity_topology_survivors'],
        separate_guidance_bounds=len(support['separate_guidance_bound_cases']),
        recommended_next_design_contract=contract),
        service_at_canonical_comparison_mass=service_summary(nominal),
        service_at_support_material_mass=service_summary(heavier),
        carrier_geometry=geometry,
        specification_decision=dict(status='research-contracts-prepared-integrated-adoption-held',
            existing_defaults_changed=False, common_accepted_configuration=False,
            counted_support_mass_is_lower_bound=True,
            carrier_and_remaining_installed_mass_reconciled=False,
            full_route_or_cost_advantage_established=False,
            reasons=['Separate guidance still lacks steel/leakage/control margin and a spatial force map.',
                     'Carrier joints, slides, capture, coolers and guidance have no complete installed fit or weighed mass.',
                     'Propulsion sharing, current control, repeated cooling, grade, boarding and receiving protection remain open.',
                     'Longer trains and shorter spacing add platform, station, charging and powered-guideway quantities; total cost remains unknown.']))


def design_round():
    from . import carrier_geometry, service_envelope, support_architecture
    intent = tomllib.loads(Path(__file__).with_name('design-intent.toml').read_text())
    return validate_design_round(support_architecture.study(),
        service_envelope.read_retained(OUTPUT / 'service-envelope.json'),
        service_envelope.read_retained(OUTPUT / 'service-envelope-proposed-mass.json'),
        carrier_geometry.study(), intent)


def assemble(magnetic, propulsion, dynamics, optimisation, register):
    identity = magnetic['canonical_configuration_sha256']
    if {identity, propulsion['parent_configuration_sha256'], dynamics['configuration_sha256'],
            optimisation['parent_configuration_sha256']} != {identity}:
        raise ValueError('mixed research parent configurations')
    if (magnetic['configuration_adopted'] or propulsion['configuration_adopted']
            or dynamics['eligible_for_adoption'] or optimisation['configuration_adopted']):
        raise ValueError('conditional research cannot adopt a configuration')
    if any(register.get(flag) is not False for flag in qualification.FLAGS):
        raise ValueError('unaccepted qualification register required')
    tasks = register['tasks']
    if any(row['accepted'] or row['state'] != 'hold' for row in tasks):
        raise ValueError('research checks cannot close qualification tasks')
    if set(GROUP_OWNERS) != {group['id'] for group in register['groups']}:
        raise ValueError('all qualification groups need a workstream owner')
    tasks = [dict(row, owner_roles=sorted({GROUP_OWNERS[group] for group in row.get('group_ids', [])})
                  or ['Systems engineering and independent reviewer']) for row in tasks]
    order = task_order(tasks)
    if len(tasks) != register['coverage']['tasks']:
        raise ValueError('qualification task coverage differs')
    admission = [dict(row) for row in dynamics['admission_requirements']]
    revised_admission = {
        'candidate-definition': 'One revised configuration digest with the selected car formation, support/guide channel counts, complete installed mass/CG/inertia, tolerances and protection equipment counted once.',
        'maps-and-initial-equilibrium': "Same-revision finite-geometry lift/guidance maps over actual gaps/current/temperature and within-drive current/thermal/material limits; solve the actual support and guidance channel counts across the selected formation and prove static guideway equilibrium. The canonical 144-module/six-car inverse remains a separate preserved reference.",
        'continued-fault-motion': 'Current-based motion of the complete selected formation, actual revised channel allocation and post-injection trajectories under all named faults, with nonzero frames, energy balance and verified supported/captured stop outcomes; no inherited six-car credit for longer formations.',
        'four-stop-electromechanical': 'Actual front/tail authority and complete selected-formation poses through four stops, receiving braking, dwell, services/charging, terminal return and repeated dispatch at the exact revised installed mass/maps/channel counts.',
    }
    for row in admission:
        row['evidence'] = revised_admission.get(row['id'], row['evidence'])
    # Preserve both allocations at identical dimensions. Comparing only the
    # independent best cases would confound topology with pack size and mass.
    paired = {}
    rows = optimisation['cases']
    for best in optimisation['best_by_topology'].values():
        number = next(index for index, row in enumerate(rows) if row['id'] == best['id'])
        first = number - number % 2
        for row in rows[first:first + 2]:
            paired[row['id']] = dict(id=row['id'], hypothesis=row['hypothesis'],
                hypothesis_sha256=row['hypothesis_sha256'],
                state='planned-independent-spatial-and-thermal-coupon', executed=False,
                comparison_pair_ids=[candidate['id'] for candidate in rows[first:first + 2]],
                retained_aw3_kg=row['controlled_aw3_kg'],
                required_cooling_at_120c_w_k=row['fixed_current_required_cooling_at120c_w_k'],
                new_hardware_mass_reconciled=False, physical_validation=False)
    return dict(schema='osr-research-execution-plan/1', canonical_configuration_sha256=identity,
        reviewed_revision='d875faec185bc1fbe75565f986bda22d529ad84f',
        scope='Repository-executed research plus the complete qualification queue; no manufactured or accepted train.',
        qualification_binding=register['binding'], coverage=register['coverage'],
        tasks=tasks, topological_task_order=order,
        workstreams=[dict(group, owner_role=GROUP_OWNERS[group['id']]) for group in register['groups']],
        research=dict(magnetics=magnetic, propulsion=propulsion, dynamics=dynamics,
            magnetic_optimisation=dict(executed_cases=optimisation['executed_cases'],
                joint_screen_passes=optimisation['joint_screen_passes'],
                best_by_topology=optimisation['best_by_topology'],
                receipt='magnetic-optimisation.json')),
        admission_requirements=admission,
        next_magnetic_experiments=[paired[key] for key in sorted(paired)],
        next_actions=[
            'Build independent nonlinear spatial flux models for paired original/sensitivity geometries; establish mesh/domain and energy/force consistency before interpreting gains.',
            'Design and count revised guidance windings and heat paths, including insulation, cooling/protection and support mass; rerun simultaneous AW3 lift/lateral/current/thermal screens.',
            'Resolve propulsion local peaks with independent longitudinal/depth refinement and retain refused meshes; count the changed installed propulsion geometry.',
            'Develop shorter or articulated magnetic mounting candidates for curves; count mechanisms and verify gap, capture, brake and structural load paths.',
            'Bind one surviving revision to actual current control, repeated duty, initial equilibrium and fault trajectories before the four-stop electromechanical run.',
            'Execute all physical, supplier, site and independent-review tasks using the existing typed qualification procedures and approved limits.'],
        full_line_rerun_ready=False, **FLAGS)


def study(optimisation=OPTIMISATION):
    qualification.verify()
    value = assemble(magnetic_research_closure.audit(), propulsion_research.study(),
        dynamics_readiness.study(), check_optimisation(json.loads(Path(optimisation).read_bytes())),
        qualification.study())
    context = readme_context.audit()
    if not context['current']:
        raise ValueError('README system context is incomplete: ' + str(context['errors'][:3]))
    value['documentation'] = {key: context[key] for key in ('readme_count', 'categories',
        'owned_manual_readmes', 'owned_introductions_current', 'existing_context_routes',
        'central_context_routes', 'current_source_packet_readmes_preserved', 'current')}
    value['design_round'] = design_round()
    if value['design_round']['service_at_canonical_comparison_mass']['parent_configuration_sha256'] != value['canonical_configuration_sha256']:
        raise ValueError('design round and qualification research parents differ')
    return value


def source_paths(optimisation=OPTIMISATION):
    paths = [Path(__file__), Path(optimisation), qualification.OUTPUT / 'manifest.json',
        ROOT / 'docs/ROADMAP.md', ROOT / 'engineering/maglev_research/_magnetic_research_sweep.py']
    paths += sorted(Path(__file__).parent.glob('*.py'))
    paths += sorted((ROOT / 'engineering/maglev_research/tests').glob('test_*.py'))
    paths += [ROOT / 'tools/automation/test-maglev-research.sh']
    paths += [OUTPUT / name for name in ('magnetics.md', 'propulsion.md', 'dynamics.md')]
    paths += [ROOT / name for name in ('README.md', *readme_context.OWNED)]
    paths += [Path(__file__).with_name('design-intent.toml')]
    paths += [OUTPUT / name for name in ('support-architecture.json', 'service-envelope.json',
        'service-envelope-proposed-mass.json', 'support-architecture.md', 'service-envelope.md', 'carrier-geometry.md')]
    return sorted(set(paths))


def second_round_readme(value):
    second = value.get('design_round')
    if second is None:
        return ''
    support = second['support']; contract = support['recommended_next_design_contract']
    nominal = second['service_at_canonical_comparison_mass']; heavy = second['service_at_support_material_mass']
    chosen = heavy['recommended_research_specification']; geometry = second['carrier_geometry']
    return f'''## Simplicity, cost and passenger-capacity design round

The [versioned research specification](../../../../engineering/maglev_research/design-intent.toml)
allows lower speed, different stop spacing, dwell and repeated-car formations.
It preserves the normal **14,400 passengers/hour/direction** comparison floor,
full-tail protection, passenger loads and magnetic/current/thermal screens.
These are proposed study inputs, not approved operating or city specifications.

| Executed workstream | Result |
|---|---|
| [Counted support architectures](support-architecture.md) | {support['executed_joint_model_cases']} shared-circuit cases; {support['nominal_joint_passes']} nominal passes; **{support['simultaneous_survivor_count']}** combined reserve/fit survivors |
| Separate guidance contract | {support['separate_guidance_bounds']} material-bound cases; proposed {contract['support_modules_per_car']} support modules plus {contract['guidance_units_per_car']} guide units/car, **{contract['controlled_aw3_material_lower_bound_kg_per_car']/1000:.3f} t AW3/car minimum** |
| [Service at canonical comparison mass](service-envelope.md) | {nominal['coverage']['service_variants']} service variants; {nominal['coverage']['reference_throughput_floor_passes']} meet the normal capacity comparison floor conditionally |
| Service at the support material-mass floor | {heavy['coverage']['service_variants']} variants; {heavy['coverage']['reference_throughput_floor_passes']} meet that floor conditionally |
| [Finite-stock carriers and terminal curves](carrier-geometry.md) | {geometry['executed_geometry_cases']} cases; {geometry['yaw_only_geometry_survivors']} yaw-only survivors; installed joints/guidance/cooling fit remains open |

The separate-guide contract is a **stationary spatial-model/rig proposal**.
Its gap field and steel flux, turns, conductor, bobbin, fluid, cooling and mass
are explicit. Airgap-only MMF still omits steel/leakage/control margin; it is
not a demonstrated guidance circuit. The counted mass excludes unweighed carrier
mechanisms and remaining installed interfaces. Its nominal support power fits
the inherited suspension allocation conditionally, while the static 1.3-load
subtotal exceeds it; repeated duty and fault reserve remain unqualified.

The same lower-bound mass is used for the heavier service study; the lighter
canonical mass supplies no free performance credit. Its ranking selects a
**research comparison** with {chosen.get('cars', 0)} cars,
{chosen.get('train_length_m', 0):.1f} m overall,
{chosen.get('station_spacing_m', 0)/1000:g} km stop spacing,
{chosen.get('max_speed_m_s', 0)*3.6:g} km/h speed cap,
{chosen.get('dwell_s', 0):g} s dwell and approximately
{chosen.get('conditional_capacity_pph', 0):,.0f} normal passengers/hour/direction.
The full comparison includes station, platform, winding and charging quantities.
All service cases retain failed/open thermal, support, grade and protection gates.
The existing 5% grade comparison is still unmet; no unproved lower-grade route
is substituted. Longer trains and high charging ratings do not establish low
total cost.

Carrier geometry includes full stock envelopes, tolerance reserve, collisions,
body offset and actual lateral travel. Multiple yaw pivots on one rigid body
cannot independently follow the curve without the declared lateral mechanism.
Larger terminal radii and a 3.0 m underbody clearance are explicit research
changes; the 2.65 m body and current city layouts are not silently widened.
Guide units, capture/brakes, coolers, bearings and slides must fit and be weighed
before repeating the support and service calculations.

**Integrated specification decision: hold.** No one configuration yet combines
validated lift/guidance, complete installed mass, carriers, repeated thermal duty,
protection, route geometry and cost at the desired normal passenger capacity.
The existing catalogue defaults remain preserved, and the next work is defined
by exact research contracts rather than automatic promotion of separate wins.

'''


def readme(value):
    research = value['research']; magnetic = research['magnetics']
    propulsion = research['propulsion']; dynamics = research['dynamics']; coverage = value['coverage']
    groups = '\n'.join('| ' + ' | '.join((row['owner_role'], row['deliverable'],
        '; '.join(row['missing_evaluators_or_external_tests']))) + ' |' for row in value['workstreams'])
    admission = '\n'.join(f"{number}. **{row['id']}** — {row['evidence']}" for number, row in enumerate(value['admission_requirements'], 1))
    actions = '\n'.join(f'{number}. {action}' for number, action in enumerate(value['next_actions'], 1))
    experiments = '\n'.join(f"| {row['id']} | {row['hypothesis']['topology']} | "
        f"{row['hypothesis']['width_m']*1000:g} | {row['hypothesis']['core_scale']:g} | "
        f"{row['hypothesis']['guide_turns']:g} | {row['hypothesis']['guide_conductor_area_mm2']:.3f} | "
        f"{'wide' if row['hypothesis']['wide_pack'] else 'standard'} |" for row in value['next_magnetic_experiments'])
    return f'''# Design completion and optimisation execution plan

OpenSourceRail pursues simple locally buildable urban transport, low construction
and operating cost, affordable debt and high useful passenger throughput. Fixed
station motors launch and receive trains; onboard support and services remain
independent through the coast. Passengers transfer between fixed lines.
[Project introduction and ethos](../../../../README.md).

Reviewed baseline: `d875faec18` (24 October 2026). Canonical candidate:
`{value['canonical_configuration_sha256']}`. Repository checks and bounded
research are executed; **the train design remains incomplete and unaccepted**.

This plan retains **all {coverage['tasks']} qualification tasks**, covering
{coverage['applicable_requirements']} requirements, {coverage['system_ids']} system IDs,
{coverage['obligation_groups']} workstreams, {coverage['protocols']} protocols and G0–G5.
No task is dropped because a simulation fails. Physical/site/supplier measurements,
approved limits and independent decisions remain required. Owner roles below
are proposed responsibilities, not appointments or reviewer approvals.

## Completed repository work

| Work | Executed result | Scope |
|---|---|---|
| [Magnetic archive audit](magnetics.md) | {magnetic['executed_case_records']} original records independently checked | Four original static passes; fifteen conditional topology passes; zero combined guidance passes |
| [Additional magnetic optimisation](magnetic-optimisation.json) | {research['magnetic_optimisation']['executed_cases']} new paired-topology winding cases; {research['magnetic_optimisation']['joint_screen_passes']} joint survivors | Counted mass feedback and unchanged current, fill, field and thermal limits |
| [Propulsion follow-up](propulsion.md) | Four scalar electrical fixtures; {propulsion['search']['cases']} current/duty variants, {propulsion['search']['conditional_coupon_passes']} conditional coupon passes | All remain ineligible for system adoption; local peak convergence unresolved |
| [Dynamics and curve optimisation](dynamics.md) | {dynamics['cases']} retained cases audited; {dynamics['meaningful_motion_cases']} motion cases; {dynamics['continued_post_fault_cases']} continued post-fault cases | Attempted initial currents distinguished from executed currents; analytical curve fitting only |
| Full qualification inventory | {coverage['tasks']} dependency-ordered tasks retained | Zero accepted requirements or physical gates |

Digital ERP/FUXA screens remain separate from physical engineering acceptance.
The 240 new magnetic cases are additional records; the sealed 225-record archive
is unchanged. No replacement configuration is adopted. A conditional propulsion
coupon does not cure the canonical support deficit or provide an installed mass.

## Next optimisation and design work

{actions}

The magnetic search found no simultaneous survivor. Its best original-topology
case requires about 139 W/K guidance cooling against the assumed 18 W/K; the
unvalidated sensitivity needs about 50 W/K. Adding cooling changes mass and lift
demand, so neither figure is a completed heat-path design. Propulsion ranking
selects a next fixed-pose coupon using force-times-duty, not route performance.
Recentring the existing rigid array reduces the necessary curve radius from
about 2,521 m to 1,250 m; the 300 m and 50 m cases still fail. Shorter/articulated
mounts require a new geometry, mass, tolerance and structural definition.

### Prepared next magnetic comparisons

The independent spatial/thermal experiments below are **planned and unexecuted**.
Each pair holds dimensions, conductor area and pack size fixed while changing
the flux-allocation hypothesis. This separates topology from winding/mass changes.
The original and sensitivity winners use different pack sizes, so comparing only
those two winners would confound the experiment. Exact hypothesis digests and
paired case IDs are retained in the machine-readable plan.

| Seed | Flux hypothesis | Pole width mm | Core scale | Guide turns | Guide conductor mm² | Pack |
|---|---|---:|---:|---:|---:|---|
{experiments}

The next model must derive the physical flux split from the same spatial
geometry, rather than impose either reluctance-network hypothesis as truth.
Cooling requirements remain fixed-load lower bounds; redesigned hardware still
needs its own mass and support calculation before an operating comparison.

## Complete work allocation

The [machine-readable plan](execution-plan.json.gz) contains every original task,
deliverable, prerequisite, hold rule and topological order. The original
[qualification procedures](../qualification/README.md) remain the authority for
typed physical evidence. All {coverage['tasks']} tasks remain on hold there.

| Responsible role | Design deliverable | Missing evidence / evaluator |
|---|---|---|
{groups}

City rollout, factory output, hardware timing, surveyed routes and whole-life
economics remain in these workstreams. Planning assumptions and synthetic demand
must retain their labels. Software tests do not resolve measured demand, price,
site, material or hardware gaps.

{second_round_readme(value)}

## README introductions

The [README context register](readme-coverage.md) audits every repository README,
maintains concise introductions at the thirteen manual entrypoints and preserves
source-bound city, numerical and archived evidence wording. Each audited README
has a route to the current system introduction, either through its own navigation
or directly from that register. The [coverage receipt](readme-coverage.json)
records individual file digests and checks original evidence bindings.

## Admission order for integrated operation

{admission}

The complete four-stop electromechanical journey remains unexecuted. Known
initial refusals are preserved; rerunning them is not useful motion evidence.

## Reproduce and maintain

```bash
tools/automation/osr-python -m engineering.maglev_research.research_closure publish
tools/automation/osr-python -m engineering.maglev_research.research_closure check
tools/automation/osr-python -m engineering.maglev_research.magnetic_research_closure --optimise build/magnetic-followup-new.json
bash tools/automation/test-maglev-research.sh
tools/automation/osr-python -m engineering.maglev_research.readme_context --check
./osr test
```

`publish` refreshes audits, electrical coupons, curve bounds and the full plan.
It verifies the retained magnetic optimisation; it does not rerun that search.
`check` recomputes the publication and rejects changed sources or payloads.
Optimisation requires a new output path, preserving previous runs. New results
must be reviewed against the joint constraints before changing this plan.
'''


def publish(output=OUTPUT, optimisation=OPTIMISATION, *, check=False):
    output = Path(output)
    paths = source_paths(optimisation)
    sources = {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest() for path in paths}
    value = study(optimisation)
    value['source_sha256'] = sources
    files = {'execution-plan.json.gz': gzip.compress(encoded(value), mtime=0),
             'README.md': readme(value).encode(),
             **{name + '.json': encoded(value['research'][name])
                for name in ('magnetics', 'propulsion', 'dynamics')}}
    if 'design_round' in value:
        files['carrier-geometry.json'] = encoded(value['design_round']['carrier_geometry'])
    manifest = dict(schema='osr-research-closure-publication/1', source_sha256=sources,
        files_sha256={name: sha256(payload).hexdigest() for name, payload in files.items()}, **FLAGS)
    if sources != {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest() for path in paths}:
        raise ValueError('research sources changed during execution')
    for name, payload in {**files, 'manifest.json': encoded(manifest)}.items():
        destination = output / name
        if check:
            if not destination.is_file() or destination.read_bytes() != payload:
                raise ValueError('stale research publication: ' + name)
        else:
            output.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload)
    return dict(tasks=len(value['tasks']), states=dict(Counter(task['state'] for task in value['tasks'])),
        magnetic_cases=value['research']['magnetic_optimisation']['executed_cases'],
        full_line_rerun_ready=False, **FLAGS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('publish', 'check'))
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--optimisation', type=Path, default=OPTIMISATION)
    args = parser.parse_args()
    print(json.dumps(publish(args.output, args.optimisation, check=args.action == 'check'), indent=2))


if __name__ == '__main__':
    main()
