"""Worker copied into a reconstructed frozen research tree; never run in place."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import itertools
import json
import math
from pathlib import Path


def main():
    work = Path(__file__).resolve().parent
    if work.name != 'pole-return-research' or not (work / 'run_guidance.py').is_file():
        raise ValueError('worker requires an isolated retained-model reconstruction')
    spec = importlib.util.spec_from_file_location('closure_frozen_guidance', work / 'run_guidance.py')
    guidance = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guidance)
    research = guidance.r
    cm = research.cm
    before = cm.sources()
    parent = cm.definition()
    rows = []
    plans = itertools.product((.020, .0225, .025, .0275, .030, .035),
                              (1.5, 1.75, 2., 2.2, 2.4), (140., 200.), (False, True), (False, True))
    for width, scale, turns, large, sensitive in plans:
        outer = [.72 if large else .62, .188]
        inner = [.16 * scale + .02, .10]
        pack_volume = (math.prod(outer) - math.prod(inner)) * .073
        mean_length = sum(inner) + sum(outer)
        # Remain slightly inside the unchanged fill ceiling to avoid rounding
        # labelling an exact boundary as a physical fit.
        area = .549 * pack_volume / (turns * mean_length) * 1e6
        context, fit = guidance.winding_context(width, scale, turns, area, large)
        if not sensitive:
            # Only the allocation sensitivity changed these paths. Restore the
            # complete original paths for an explicit paired-model comparison.
            context[2]['core_paths'] = deepcopy(research.context_for(width, scale, 140., 23.5)[2]['core_paths'])
        a, _, module = context[:3]
        aw3 = parent['controlled_aw3_kg'] + a['module_count_per_car'] * (module['mass_kg'] - parent['module']['mass_kg'])
        target = aw3 * research.G / a['module_count_per_car']
        with research.installed(context):
            nominal = guidance.ctrl.asymmetric(context, target, .1 * target)
            adverse = guidance.ctrl.asymmetric(context, 1.3 * target, .1 * target)
        fill = max(c['fill_fraction'] for c in module['coils']) <= a['coil_fill_limit']
        passed = bool(fit['nominal_aabb_clear'] and fill and nominal.get('map_valid', False)
                      and nominal.get('continuous_current_density_screen', False)
                      and nominal.get('constant_current_thermal_screen', False))
        # Rank research utility by maximum normalized nominal constraint
        # violation, then moving mass; all constraints retain their limits.
        density_ratio = max(nominal.get('current_density_a_mm2', [1e30])) / a['continuous_current_density_a_mm2']
        current_ratio = max(abs(i) for i in nominal.get('required_current_a', [1e30])) / a['current_limit_a']
        field_ratio = nominal.get('max_core_b_t', 1e30) / 2.2
        cu = a['materials']['copper']
        coils = module['coils']
        r20 = [coils[0]['conductor_length_m'] / (coils[0]['conductor_area_mm2'] * 1e-6) * cu['resistivity_20c_ohm_m'],
               sum(c['conductor_length_m'] for c in coils[1:]) / (coils[1]['conductor_area_mm2'] * 1e-6) * cu['resistivity_20c_ohm_m']]
        required_cooling = [i ** 2 * resistance * (1 + cu['resistance_temperature_coefficient_per_k'] * (a['maximum_copper_c'] - 20))
                            / (a['maximum_copper_c'] - a['ambient_c'])
                            for i, resistance in zip(nominal['required_current_a'], r20)]
        thermal_ratio = max(required / available for required, available in zip(required_cooling, context[1]['cooling_w_k']))
        violation = max(density_ratio, current_ratio, field_ratio, thermal_ratio,
                        1. if fit['nominal_aabb_clear'] and fill else 1e30)
        hypothesis = dict(width_m=width, core_scale=scale, guide_turns=turns,
                          guide_conductor_area_mm2=area, wide_pack=large,
                          topology='useful-only-poles-sensitivity' if sensitive else 'original-branch-flux',
                          guide_copper_fill_target=.549)
        rows.append(dict(id=f"closure-{len(rows):03d}", hypothesis=hypothesis,
                         hypothesis_sha256=sha256(cm.encoded(hypothesis)).hexdigest(),
                         module_mass_kg=module['mass_kg'], controlled_aw3_kg=aw3,
                         counted_stock_mass_kg=sum(part['mass_kg'] for part in module['parts']),
                         nominal_aabb_clear=fit['nominal_aabb_clear'], collision_count=len(fit['collisions']),
                         copper_fill_fractions=[c['fill_fraction'] for c in module['coils']],
                         nominal_joint=nominal, adverse_joint=adverse,
                         fixed_current_required_cooling_at120c_w_k=required_cooling,
                         normalised_constraint_ratios=dict(density=density_ratio, current=current_ratio, field=field_ratio, thermal=thermal_ratio),
                         maximum_constraint_ratio=violation, joint_screen_pass=passed,
                         topology_independently_validated=False, configuration_adopted=False))
    assert before == cm.sources()
    fitting = [row for row in rows if row['nominal_aabb_clear'] and max(row['copper_fill_fractions']) <= a['coil_fill_limit']]
    ranked = sorted(fitting, key=lambda row: (row['maximum_constraint_ratio'], row['controlled_aw3_kg'], row['id']))
    best = {name: next((row for row in ranked if row['hypothesis']['topology'] == name), None)
            for name in ('original-branch-flux', 'useful-only-poles-sensitivity')}
    result = dict(schema='osr-bounded-magnetic-winding-optimisation/1',
                  parent_configuration_sha256=parent['configuration_sha256'],
                  source_model_sha256=before, executed_cases=len(rows),
                  nominal_fit_and_fill_cases=len(fitting), joint_screen_passes=sum(row['joint_screen_pass'] for row in rows),
                  ranking='Minimum largest nominal constraint ratio, then counted AW3 mass; ratios above one fail. Thermal ratio is required heat conductance at120C divided by unchanged available conductance. Original and sensitivity models are reported separately.',
                  best_by_topology=best, cases=rows,
                  next_experiment='Use the best original/sensitivity pair to specify independent spatial flux-map and winding/thermal coupons; any enlarged winding or heat path must be fully recounted and both forces solved again.',
                  scope='Fixed bounded research grid. Same unvalidated reluctance network, nominal AABB packs and unmeasured heat conductance. No transient thermal, real-turn fit, voltage, fatigue, civil or route qualification.',
                  complete_system_feasible=False, configuration_adopted=False,
                  engineering_accepted=False, physical_validation=False)
    (work / 'closure-sweep.json').write_bytes(cm.encoded(result))


if __name__ == '__main__':
    main()
