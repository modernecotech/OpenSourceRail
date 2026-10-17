"""Independent cross-domain critic: conservation, source contracts and gates."""
from copy import deepcopy
import hashlib
import math
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'design/component-catalogue/src')]
from engineering.generative_design import civil_detail, mechanical_detail, twin_civil, twin_mechanical


@pytest.mark.parametrize('field', ['force', 'supports', 'source_hash'])
def test_architecture_rejects_weakened_or_unbound_source_context(field):
    context = deepcopy(mechanical_detail.contexts()[0])
    if field == 'force':
        context['source_car_force_n'] = 0.
    elif field == 'supports':
        context['support_x_m'] = [0., context['body_length_m']]
    else:
        name = next(iter(context['source_sha256']))
        context['source_sha256'][name] = '0' * 64
    with pytest.raises(ValueError, match='context|source'):
        twin_mechanical.architecture_variant(context, 'closed-box', .6, .016)


@pytest.mark.parametrize('kind', ['open-i', 'closed-box'])
def test_longitudinal_architecture_plate_mass_and_reactions_conserve_load(kind):
    context = mechanical_detail.contexts()[0]
    variant = twin_mechanical.architecture_variant(context, kind, .6, .016)
    # The leaf fabrication solids, not the section calculator, supply this sum.
    density = mechanical_detail._inputs()['material']['density_kg_m3']
    volume = math.fsum(math.prod(p['specifications']['size_m'])
                      for p in variant['parts'] if 'size_m' in p['specifications'])
    mass = density * volume
    assert variant['objectives']['modeled_longitudinal_mass_kg'] == pytest.approx(mass)
    expected_force = context['source_car_force_n'] + 9.80665 * mass
    assert math.fsum(variant['metrics']['beam']['reactions_n']) == pytest.approx(expected_force)
    assert variant['objectives']['complete_frame_mass_kg'] is None
    assert any(c['state'] == 'unknown' and c['id'] == 'transverse-load-path-and-connections'
               for c in variant['checks'])


def test_civil_moving_point_load_recovers_closed_form_and_scaling():
    span, force, stiffness = 20., 200000., 4e10
    # A single traversing point load has its largest midspan displacement at
    # midspan, independently known as P L^3/(48 EI).
    result = civil_detail.moving_midspan_deflection(span, [{'x_m': 0., 'force_n': force}], stiffness)
    assert result['deflection_m'] == pytest.approx(force * span**3 / (48 * stiffness))
    assert result['governing_origin_m'] == pytest.approx(span / 2)
    doubled = civil_detail.moving_midspan_deflection(span, [{'x_m': 0., 'force_n': 2 * force}], 2 * stiffness)
    assert doubled['deflection_m'] == pytest.approx(result['deflection_m'])
    assert not result['full_span_maximum']


def test_civil_footing_partial_contact_preserves_moment_and_rejects_overturning():
    vertical, width, eccentricity = 1e6, 4., 1.
    result = civil_detail.footing_pressure(vertical, vertical * eccentricity, width)
    assert not result['full_contact'] and result['equilibrium_possible']
    contact = result['compression_contact_length_m']
    qpeak = result['compression_maximum_pressure_pa']
    assert .5 * width * contact * qpeak == pytest.approx(vertical)
    # Triangle resultant is c/3 from the loaded edge.
    assert width / 2 - contact / 3 == pytest.approx(eccentricity)
    overturn = civil_detail.footing_pressure(vertical, vertical * width / 2, width)
    assert not overturn['equilibrium_possible']
    assert overturn['compression_maximum_pressure_pa'] is None


@pytest.fixture(scope='module')
def civil_packet():
    return twin_civil.build()


def test_two_support_civil_mass_boundary_matches_explicit_concrete(civil_packet):
    density = civil_detail._read()['assumptions']['concrete_density_kg_m3']
    for system in civil_packet['systems']:
        for variant in system['variants']:
            substructure_volume = sum(p['specifications'].get('concrete_volume_m3', 0.) for p in variant['parts'])
            objectives = variant['objectives']
            # Existing objective includes one support; the twin explicitly adds
            # the second support, never silently doubles the beam.
            extra_mass = objectives['two_support_known_mass_kg'] - objectives['mass_kg']
            assert extra_mass == pytest.approx(substructure_volume * density / 2)
            assert objectives['full_cost_usd'] is None


def test_civil_variants_cannot_promote_failures_or_unknowns_to_completion(civil_packet):
    assert not civil_packet['full_specification_complete']
    assert not civil_packet['physical_twin_correlated']
    for system in civil_packet['systems']:
        for variant in system['variants']:
            failed = any(c['state'] == 'fail' for c in variant['checks'])
            assert variant['selection_state'].startswith('rejected') if failed else variant['selection_state'] == 'conditional-research-candidate'
            assert any(c['state'] == 'unknown' for c in variant['checks'])
            assert not variant['manufacturing_release']
            ids = {p['id'] for p in variant['parts']}
            assert all(p['parent_id'] is None or p['parent_id'] in ids for p in variant['parts'])
    for name, expected in civil_packet['source_files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected
