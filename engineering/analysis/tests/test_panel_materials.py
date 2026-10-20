"""Independent controls and adverse cases for matched panel route comparisons."""
from copy import deepcopy
from pathlib import Path
import json
import math
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from engineering.panel_materials import study
from engineering.twin_workflow import core


@pytest.fixture
def inputs():
    return core.read(study.CONFIG), core.read(study.BASELINE)


def test_section_matches_independent_composite_area_and_parallel_axis_control():
    # Two rectangular flanges with a known centroid and inertia.
    result = study.section_properties([(.1, .01, -.05), (.1, .01, .05)])
    assert result['area_m2'] == pytest.approx(.002)
    assert result['centroid_z_m'] == pytest.approx(0)
    assert result['inertia_m4'] == pytest.approx(2*(.1*.01**3/12+.001*.05**2))


def test_beam_matches_closed_form_scaling_and_plate_limit():
    # Single full-width metal strip, independent textbook formula.
    p, span, young, thickness = 2000, .8, 70e9, .002
    expected = 5*p*span**4/(32*young*thickness**3)
    value = study.beam_deflection(p, span, young*thickness**3/12)
    assert value == pytest.approx(expected)
    assert study.beam_deflection(2*p, span, young*thickness**3/12) == pytest.approx(2*value)
    assert study.beam_deflection(p, 2*span, young*thickness**3/12) == pytest.approx(16*value)


@pytest.mark.parametrize('route', study.ROUTES)
def test_exact_same_context_installed_mass_and_pressure_sensitivity(inputs, route):
    config, base = inputs
    ctx = study.context(config, base, 'side')
    variables = (dict(sheet_m=.002, hat_depth_m=.035, hat_pitch_limit_m=.25) if route == study.ROUTES[0]
                 else dict(skin_m=.0015, core_m=.0246, core_density_kg_m3=80))
    a = study.candidate(config, base, ctx, route, variables)
    changed = deepcopy(config); changed['pressure_pa'] *= 2
    b = study.candidate(changed, base, study.context(changed, base, 'side'), route, variables)
    assert b['model']['total_deflection_m'] == pytest.approx(2*a['model']['total_deflection_m'])
    assert b['installed_mass_kg'] == a['installed_mass_kg']
    assert a['installed_mass_kg'] == pytest.approx(math.fsum(a['mass_components_kg'].values()))
    for key in ('clips', 'retainer', 'seal', 'finish', 'liner', 'support_rails_brackets_fasteners'):
        assert a['mass_components_kg'][key] > 0
    assert a['mass_components_kg']['support_rails_brackets_fasteners'] == ctx['support_network']['mass_kg']
    assert b['id'] != a['id'] and b['context_revision'] != a['context_revision']
    assert a['installed_cost_usd'] is None and not a['engineering_eligible']
    assert all(value is None for value in a['mandatory_engineering_checks'].values())
    assert all(a[key] is False for key in core.FLAGS)


def test_roof_failed_temperature_cannot_be_promoted_or_hidden(inputs):
    contexts, cases = study.generate_cases(*inputs)
    assert len(cases) == 162 and len({c['id'] for c in cases}) == 162
    assert len({c['context_revision'] for c in cases}) == 2
    roofs = [c for c in cases if c['kind'] == 'roof']
    assert len(roofs) == 81
    assert all(c['screening_checks']['core_continuous_temperature'] is False for c in roofs)
    assert all(c['conditional_screen_pass'] is False for c in roofs)
    reps = study.representatives(cases)
    assert len(reps) == 6
    assert all(not r['screening_pass'] and 'diagnostic' in r['selection'] for r in reps if r['kind'] == 'roof')
    assert not any(c['engineering_eligible'] for c in cases)
    assert contexts[1]['developed_length_m'] > contexts[1]['chord_m']


def test_overload_is_a_rejection_even_with_unchanged_mass(inputs):
    config, base = inputs
    variables = dict(skin_m=.002, core_m=.03, core_density_kg_m3=100)
    initial = study.candidate(config, base, study.context(config, base, 'side'), 'gfrp-sandwich', variables)
    config['pressure_pa'] *= 1000
    adverse = study.candidate(config, base, study.context(config, base, 'side'), 'gfrp-sandwich', variables)
    assert initial['screening_checks']['deflection_surrogate']
    assert adverse['screening_checks']['deflection_surrogate'] is False
    assert adverse['screening_checks']['small_deflection'] is False
    assert adverse['conditional_screen_pass'] is False


def test_thermal_paths_are_counted_rather_than_bare_insulation_claim(inputs):
    config, base = inputs
    ctx = study.context(config, base, 'side')
    folded = study.candidate(config, base, ctx, study.ROUTES[0], dict(sheet_m=.002, hat_depth_m=.035, hat_pitch_limit_m=.25))
    assert folded['conduction_resistance_screen_m2k_w'] < .035/base['core_grades']['80']['thermal_conductivity_w_mk']
    assert not folded['screening_checks']['conduction_review']
    al = study.candidate(config, base, ctx, study.ROUTES[1], dict(skin_m=.0015, core_m=.0246, core_density_kg_m3=80))
    glass = study.candidate(config, base, ctx, study.ROUTES[2], dict(skin_m=.0015, core_m=.0246, core_density_kg_m3=80))
    assert al['conduction_resistance_screen_m2k_w'] < glass['conduction_resistance_screen_m2k_w']
    # Solid aluminium perimeter closures are intentionally heavier than glass.
    assert al['mass_components_kg']['skins_and_solid_edge_lands'] > glass['mass_components_kg']['skins_and_solid_edge_lands']


@pytest.mark.parametrize('key,value', [('pressure_pa', 0), ('pressure_pa', True), ('width_m', float('nan')),
    ('roof_crown_m', -1), ('roof_crown_m', float('nan')), ('side_temperature_c', True),
    ('roof_temperature_c', float('inf')), ('gfrp_stiffness_sensitivity_factor', 1.5)])
def test_invalid_contexts_never_become_designs(inputs, key, value):
    config, base = inputs; config[key] = value
    with pytest.raises(ValueError): study.generate_cases(config, base)


def test_unknown_prices_and_unbuildable_hats_are_not_zero_cost_candidates(inputs):
    config, base = inputs
    config['commercial']['material_usd_kg'] = 1
    with pytest.raises(ValueError, match='quotation'): study.generate_cases(config, base)
    with pytest.raises(ValueError, match='overlap'):
        study.hat_section(.05, .002, .03, config['hat'])


def test_changed_context_cannot_reuse_an_original_candidate_identity(inputs):
    config, base = inputs
    ctx = study.context(config, base, 'side'); ctx['pressure_pa'] *= 2
    with pytest.raises(ValueError, match='source-bound'):
        study.candidate(config, base, ctx, 'gfrp-sandwich', dict(skin_m=.002, core_m=.03, core_density_kg_m3=100))


def test_artifacts_reproduce_bind_sources_and_reject_tampering(tmp_path):
    summary = study.publish(tmp_path)
    assert summary['candidate_count'] == 162 and summary['engineering_eligible_count'] == 0
    assert summary['qualified_runner_changed'] is False
    study.publish(tmp_path, check=True)
    manifest = json.loads((tmp_path/'manifest.json').read_text())
    for name, digest in manifest['sources_sha256'].items(): assert core.sha(ROOT/name) == digest
    for name, digest in manifest['outputs_sha256'].items(): assert core.sha(tmp_path/name) == digest
    (tmp_path/'candidates.json').write_text('[]')
    with pytest.raises(ValueError, match='stale'): study.publish(tmp_path, check=True)


def test_checked_in_artifacts_and_supplier_origin_limits_are_current():
    study.publish(check=True)
    sources = core.read(study.SOURCES)
    assert sources['contact_status'].startswith('Research only')
    for case in sources['supplier_cases']:
        assert case['configuration_hold']
        if case['origin_class'].startswith('UK manufacture'):
            assert case['source_ids']
