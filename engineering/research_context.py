"""Explicit retained physical configurations, separate from the active selection.

Loading the named comfort-PM configuration reads authenticated historical bytes.
It does not load the v0.6 selector, regenerate a vehicle or grant acceptance.
Historical producer hashes remain ancestry; they are not the current evaluator's
source epoch.
"""
from copy import deepcopy
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import identity, digest
from engineering.station_rail import common, families, history
from engineering.station_rail.families import Family, describe
from engineering.station_rail.history import REVISION
from engineering.station_rail import vehicle as wheel_vehicle

CODE = 'engineering/research_context.py'
FLAGS = dict(engineering_accepted=False, physical_accepted=False,
             installed_mass_complete=False, manufacturing_release=False,
             operating_release=False, configuration_adopted=False)
CONFIGURATION = dict(
    schema='osr-retained-research-configuration/1',
    revision='RETAINED-COMFORT-PM-1', family=Family.PM_MAGLEV.value,
    source_revision=REVISION, role='historical-physical-research',
    vehicle_candidate_id='957f7e4e2e0e98b575810fb0c568554968fc1eb0715fb673827a16bcf63d400b',
    body_candidate_id='1eca1897b983bf62ec315cdc39aca2e2387f93ad6ab0c195bc278e14c8fb120b',
    magnet_component_id='397ddf033ab98afaea053acaa3047249a3329f542f1f5e52a6eb1b466b9662e0',
    vehicle=dict(cars=6, body_length_m=17., normal_passengers_per_car=46,
                 fixed_seats_per_car=44, wheelchair_places_per_car=2,
                 standing_passengers_per_car=0, retained_crowd_control_per_car=160),
    source_design=wheel_vehicle.PARENT,
    source_design_sha256=wheel_vehicle.PARENT_PAYLOAD_SHA,
    source_manifest=wheel_vehicle.PARENT_MANIFEST,
    source_manifest_sha256=wheel_vehicle.PARENT_MANIFEST_SHA,
    development_default=False, **FLAGS)


def retained_maglev(root=ROOT, *, family, source_revision):
    """Resolve only the explicitly requested, pinned comfort-PM configuration."""
    if family != Family.PM_MAGLEV.value:
        raise ValueError('Retained PM-maglev research requires an explicit compatible physical family')
    if source_revision != REVISION:
        raise ValueError('Retained PM-maglev research requires its pinned source revision')
    historical = describe(Family.PM_MAGLEV, root)
    car = deepcopy(historical['vehicle'])
    if historical.get('active') is not False or historical.get('source_revision') != REVISION:
        raise ValueError('Retained PM-maglev source configuration differs')
    for key, configured in (('candidate_id', 'vehicle_candidate_id'),
                            ('body_candidate_id', 'body_candidate_id'),
                            ('magnet_component_id', 'magnet_component_id')):
        if car.get(key) != CONFIGURATION[configured]:
            raise ValueError('Retained PM-maglev physical identity differs: ' + key)
    if identity(car['physical_definition']) != car['candidate_id']:
        raise ValueError('Retained PM-maglev physical definition differs')
    if any(car.get(k) is not False for k in FLAGS):
        raise ValueError('Retained research cannot grant acceptance')
    config = deepcopy(CONFIGURATION)
    source_files = {CODE: Path(__file__)}
    source_files.update({'engineering/station_rail/' + Path(module.__file__).name: Path(module.__file__)
                         for module in (common, families, history, wheel_vehicle)})
    return dict(schema='osr-retained-research-context/1',
        research_configuration_id=identity(config), configuration=config,
        family=family, source_revision=source_revision, vehicle=car,
        historical_vehicle_evaluation_id=car['evaluation_id'],
        ancestry_source_sha256=deepcopy(car['source_sha256']),
        source_sha256={**{name: digest(path) for name, path in source_files.items()},
            wheel_vehicle.PARENT: wheel_vehicle.PARENT_PAYLOAD_SHA,
            wheel_vehicle.PARENT_MANIFEST: wheel_vehicle.PARENT_MANIFEST_SHA},
        development_default=False, **FLAGS)


def retained_comfort(root=ROOT):
    """Read the explicitly named historical comfort-PM research configuration."""
    return retained_maglev(root, family=Family.PM_MAGLEV.value, source_revision=REVISION)


def require_retained_maglev(context, root=ROOT):
    """Reject mixed families and resealed substitutions before a retained solve."""
    if not isinstance(context, dict) or context.get('family') != Family.PM_MAGLEV.value:
        raise ValueError('Retained PM-maglev research requires an explicit compatible physical family')
    expected = retained_maglev(root, family=context['family'], source_revision=context.get('source_revision'))
    if context != expected:
        raise ValueError('Retained PM-maglev research configuration, physical identity or source binding differs')
    return deepcopy(expected)
