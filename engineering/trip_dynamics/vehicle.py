"""Source-bound vehicle comparisons. No retained publication closes an equipped car.

The historical assembled CAD, canonical allocation and newer replacement ledgers
are alternative evidence scopes. Their masses must never be added together.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path, PurePosixPath
import re

from engineering.design_search.contracts import identity as design_identity

ROOT = Path(__file__).resolve().parents[2]
PINS = Path(__file__).parent / 'fixtures/structures/publication-pins.json'
FLAGS = dict(configuration_adopted=False, physical_accepted=False,
             engineering_accepted=False, complete_equipped_vehicle=False)


def identity(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                             allow_nan=False).encode()).hexdigest()


def _bytes(root, relative):
    rel = PurePosixPath(relative)
    if rel.is_absolute() or '..' in rel.parts or not rel.parts:
        raise ValueError('ordinary repository-relative source path required')
    root = Path(root).resolve()
    path = root.joinpath(*rel.parts)
    if any(part.is_symlink() for part in [path, *path.parents] if part != root.parent):
        raise ValueError('symlink source is not a retained ordinary file')
    if not path.is_file() or not path.resolve().is_relative_to(root):
        raise ValueError('missing retained source: ' + relative)
    if path.stat().st_size > 64 * 1024 * 1024:
        raise ValueError('source JSON/file exceeds bounded input budget')
    return path.read_bytes()


def _checked(root, relative, expected):
    data = _bytes(root, relative)
    if sha256(data).hexdigest() != expected:
        raise ValueError('retained source digest changed: ' + relative)
    return data


def _publication(root, folder, names):
    manifest_path = folder + '/manifest.json'
    pins = json.loads(PINS.read_text())['files_sha256']
    manifest = json.loads(_checked(root, manifest_path, pins[manifest_path]))
    bindings = {manifest_path: pins[manifest_path]}
    for relative, digest in manifest['source_sha256'].items():
        _checked(root, relative, digest)
        bindings[relative] = digest
    values = {}
    for name in names:
        path = folder + '/' + name
        digest = manifest['files_sha256'][name]
        values[name] = json.loads(_checked(root, path, digest))
        bindings[path] = digest
    return values, bindings, manifest


def current_vehicle_definitions(root: Path = ROOT) -> dict:
    """Read pinned retained evidence without running CAD or legacy verification.

    ``root`` is the repository containing the *retained* publications, not an
    arbitrary report directory. Any changed publication or bound source refuses.
    Comparison masses include retained allocations; actual installed mass/CG/I
    remain None. Numerical qualification is separate from this byte/ledger check.
    """
    from engineering.ferrite_maglev import candidate_magnetics

    newer, bindings, manifest = _publication(root, 'docs/design-engine/vehicle-optimisation',
                                             ['summary.json', 'equipment.json'])
    old, old_bindings, _ = _publication(root, 'docs/design-engine/ferrite-maglev/assembled-body',
                                       ['definition.json', 'mass-properties.json'])
    bindings.update(old_bindings)
    definition = candidate_magnetics.definition()
    # Guard the executing implementation too, rather than trusting a root with
    # matching data and a different imported canonical model.
    for name, digest in definition['source_sha256'].items():
        _checked(root, name, digest)
        bindings[name] = digest
    accounting = definition['mass_accounting']
    stock_path = 'engineering/ferrite_maglev/data/candidate-retained-body-stock.json'
    retained_stock = json.loads(_checked(root, stock_path, bindings[stock_path]))
    inventory = [dict(id='retained/actual-stock', evidence_class='counted-stock',
                      mass_kg_per_car=accounting['retained_actual_stock_kg'],
                      part_ids=[p['id'] for p in retained_stock['parts']],
                      source_path=stock_path),
                 dict(id='retained/unlocated-equipment-allocation',
                      evidence_class='unlocated-allocation',
                      mass_kg_per_car=accounting['retained_unlocated_allocation_kg'])]
    inventory += [dict(id=x['id'], evidence_class='counted-stock',
                       mass_kg_per_car=x['mass_kg_per_car'])
                  for x in accounting['added_defined_components']]
    empty = float(definition['controlled_tare_kg'])
    if not math.isclose(sum(x['mass_kg_per_car'] for x in inventory), empty, abs_tol=1e-7):
        raise ValueError('canonical disjoint mass ledger does not close')
    unresolved = ['Equipped locations and measured CG/inertia of retained allocation',
                  'As-built laminates, joints, bonds, fasteners and magnetic mounting interfaces',
                  'Full body stiffness, buckling, fatigue, crash and joined load paths',
                  'Equilibrium prestress and modal data for each payload/support boundary',
                  'Six-car coupler and suspension interfaces; hot/wet material applicability']
    canonical = dict(schema='osr-trip-vehicle/1', candidate_id=definition['configuration_sha256'],
        geometry_id=identity({'canonical': definition['configuration_sha256'],
                              'stock': bindings['engineering/ferrite_maglev/data/candidate-retained-body-stock.json']}),
        material_id=identity({'canonical_module': definition['module']['permanent_magnet'],
                              'stock_source': bindings['engineering/ferrite_maglev/data/candidate-retained-body-stock.json']}),
        label='Canonical allocated ferrite comparison with retained GFRP panels and steel frame',
        body_family='retained-GFRP-panels/steel-frame', magnetic_family='canonical-ferrite',
        comparison_empty_kg_per_car=empty,
        comparison_aw3_kg_per_car=float(definition['controlled_aw3_kg']),
        mass_ledger_id=design_identity(dict(tare=empty, aw3=float(definition['controlled_aw3_kg']),
                                            configuration=definition['configuration_sha256'])),
        comparison_mass_basis='Retained canonical allocations plus counted module/protection/propulsion stock; not a weighed equipped car',
        installed_empty_kg_per_car=None, installed_aw3_kg_per_car=None,
        cg_m=None, inertia_kg_m2=None, modules_per_car=len(definition['module_placements']),
        cars=int(definition['cars']), car_length_m=17., payload_aw3_kg_per_car=12000.,
        disjoint_inventory=inventory, unknown_installed_inventory=unresolved,
        source_bindings=deepcopy(bindings), modal_model=None, **FLAGS)
    summary = newer['summary.json']
    selected = summary['next_experiment']['selected_candidate_id']
    selected_row = next(x for x in summary['comparisons'] if x['candidate_id'] == selected)
    rows = [x for x in summary['comparisons'] if x['sample_id'] == selected_row['sample_id']
            and (x['candidate_id'] == selected or x['mode'].startswith('lighter-services/'))]
    alternatives = []
    folder = 'docs/design-engine/vehicle-optimisation'
    for row in rows:
        name = 'candidates/' + row['candidate_id'] + '.json'
        path = folder + '/' + name
        digest = manifest['files_sha256'][name]
        physical = json.loads(_checked(root, path, digest))
        bindings[path] = digest
        if physical['candidate_id'] != row['candidate_id']:
            raise ValueError('candidate file/ledger identity mismatch')
        ledger = row['mass_ledger']
        # Retained publications already expose disjoint scopes. Recheck their
        # essential overlap invariant at the reader boundary.
        parts, allowances = set(), set()
        for change in ledger['changes']:
            kind = change['removal_kind']
            keys = change.get('removed_part_ids', []) if kind == 'counted-stock' else change.get('removed_allocation_ids', [])
            owned = parts if kind == 'counted-stock' else allowances
            if not keys or len(keys) != len(set(keys)) or owned.intersection(keys):
                raise ValueError('overlapping replacement scope')
            owned.update(keys)
        bounds = row['comparison_aw3_mass_band_kg']
        units = {x['modules_per_car'] for x in row['hot_support_bounds']}
        if units != {24}:
            raise ValueError('retained support module count changed')
        chassis = physical['architecture']['chassis']
        alternatives.append(dict(schema='osr-trip-vehicle/1', candidate_id=row['candidate_id'],
            geometry_id=identity(physical['geometry']), material_id=identity(physical['materials']),
            label=row['mode'] + ' / ' + row['sample_id'],
            body_family=chassis['id'] if isinstance(chassis, dict) else chassis, magnetic_family=row['sample_id'],
            comparison_empty_kg_per_car=ledger['comparison_empty_kg_per_car'],
            comparison_aw3_kg_per_car=ledger['comparison_aw3_kg_per_car'],
            mass_ledger_id=ledger['ledger_id'],
            comparison_aw3_mass_band_kg=bounds,
            provisional_installation_addition_kg=row['provisional_installation_addition_kg'],
            comparison_mass_basis='Disjoint replacement ledger retains other canonical allocations; reported band adds provisional installation scenarios, not measured hardware',
            installed_empty_kg_per_car=None, installed_aw3_kg_per_car=None,
            cg_m=None, inertia_kg_m2=None, cars=6, car_length_m=17., modules_per_car=24,
            payload_aw3_kg_per_car=12000., replacement_ledger=deepcopy(ledger),
            unknown_installed_inventory=ledger['unknown_installed_inventory'] + unresolved,
            source_bindings={**bindings, path: digest}, modal_model=None,
            next_experiment_only=row['candidate_id'] == selected, **FLAGS))
    cad = old['mass-properties.json']
    partial = dict(candidate_id=cad['definition_sha256'],
        defined_material_mass_kg=cad['defined_vehicle_material_mass_kg'],
        defined_material_cg_m=cad['defined_vehicle_material_cg_m'],
        defined_material_inertia_kg_m2=cad['defined_vehicle_material_inertia_kg_m2'],
        part_count=cad['part_count'], included_region_count=cad['included_region_count'],
        whole_equipped_vehicle_mass_kg=None, omitted=old['definition.json']['omitted'],
        scope='Historical assembled structural/cartridge material only; overlaps canonical stock; never additive or empty car',
        density_assumptions_are_measured=cad['density_assumptions_are_measured'], **FLAGS)
    return dict(schema='osr-trip-vehicle-catalogue/1', canonical=canonical,
        alternatives=alternatives, partial_cad=partial,
        requested_gfrp_optimisation=dict(status='unknown',
            reason='Retained GFRP material is counted; a revised full-body laminate/geometry/equipped modal model is not published',
            candidate_id=None, installed_empty_kg_per_car=None, **FLAGS),
        aluminium_proposals=newer['equipment.json']['chassis'],
        unresolved_equipment_and_integration=unresolved, source_bindings=bindings, **FLAGS)


def structural_readiness(vehicle: dict, scenario: dict) -> list[dict]:
    """Necessary interface gates; a pass here never grants structural acceptance."""
    def gate(name, state, reason, **values):
        return dict(id=name, state=state, reason=reason, values=values)
    load = scenario.get('load_case')
    mass_key = 'installed_empty_kg_per_car' if load == 'empty' else 'installed_aw3_kg_per_car'
    mass = vehicle.get(mass_key)
    unknown = vehicle.get('unknown_installed_inventory', [])
    identifier = vehicle.get('candidate_id')
    identity_valid = isinstance(identifier, str) and re.fullmatch('[0-9a-f]{64}', identifier) is not None
    formation_valid = (type(vehicle.get('cars')) is int and vehicle['cars'] > 0
                       and type(vehicle.get('car_length_m')) in (int, float)
                       and math.isfinite(vehicle['car_length_m']) and vehicle['car_length_m'] > 0
                       and type(scenario.get('cars')) is int and scenario['cars'] > 0
                       and type(scenario.get('car_length_m')) in (int, float)
                       and math.isfinite(scenario['car_length_m']) and scenario['car_length_m'] > 0)
    mass_state = 'unknown'
    if mass is not None or vehicle.get('complete_equipped_vehicle') is True:
        try:
            from .flexible_body import _equipped
            checked_mass, _, _ = _equipped(vehicle, load)
            if type(mass) not in (int, float) or not math.isfinite(mass) or not math.isclose(mass, checked_mass, rel_tol=1e-9):
                raise ValueError('installed and equipped load-case masses disagree')
            mass_state = 'pass'
        except (ValueError, KeyError, TypeError):
            mass_state = 'fail'
    return [
        gate('body/load-case', 'pass' if load in ('empty', 'AW3', 'asymmetric') else 'fail',
             'Explicit empty, AW3 or asymmetric passenger load case required'),
        gate('body/scenario-identity', 'pass' if identity_valid and scenario.get('candidate_id') == identifier else 'fail',
             'Scenario must identify exactly the physical vehicle; force maps from another candidate do not transfer',
             candidate_id=vehicle.get('candidate_id'), scenario_candidate_id=scenario.get('candidate_id'), scenario_id=scenario.get('scenario_id')),
        gate('body/formation', 'pass' if formation_valid and scenario.get('cars') == vehicle.get('cars') and scenario.get('car_length_m') == vehicle.get('car_length_m') else 'fail',
             'Formation and body length must match the selected inventory'),
        gate('body/equipped-inventory', 'pass' if vehicle.get('complete_equipped_vehicle') is True and not unknown else 'unknown',
             'Counted material and retained budgets do not establish installed equipment', unresolved=unknown),
        gate('body/equipped-mass-inertia', mass_state,
             'Motion/flexible-body import requires equipped load-case mass, CG and full inertia', mass_kg_per_car=mass),
        gate('body/asymmetric-load', 'unknown' if load == 'asymmetric' else 'pass',
             'Asymmetric passenger placement and resulting equilibrium/inertia need an explicit model'),
        gate('body/modal-model', 'unknown' if not vehicle.get('modal_model') else 'unknown',
             'Use flexible_body.load_modal to validate a source-bound load/prestress/boundary-specific model'),
        gate('body/qualification', 'unknown',
             'Material, bonds, joints, fatigue, buckling, crash and installed attachments remain unqualified')]
