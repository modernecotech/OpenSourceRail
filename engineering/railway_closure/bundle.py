"""Canonical whole-railway identity and explicit component evidence bindings."""
from engineering.station_rail.common import identity
from engineering.pilot_civil.design import validate_track_interface
from . import FLAGS


def combine(installed,civil):
    for v in (installed,civil):
        if v['evaluation_id']!=identity({k:x for k,x in v.items() if k!='evaluation_id'}):
            raise ValueError('Sealed component evaluations required')
    if civil['system_candidate_id']!=installed['candidate_id'] or civil['mass_evaluation_id']!=installed['evaluation_id']:
        raise ValueError('Civil evidence belongs to a different installed load revision')
    if installed['candidate_id']!=identity(installed['physical_definition']):
        raise ValueError('Installed physical identity mismatch')
    terminal=installed['terminal_geometry']
    if terminal['geometry_id']!=identity(terminal['physical_definition']):
        raise ValueError('Terminal physical identity mismatch')
    if civil['civil_candidate_id']!=identity(civil['physical_definition']):
        raise ValueError('Civil physical identity mismatch')
    track=installed['physical_definition']['track_interface']
    validate_track_interface(track)
    if track!=civil['physical_definition']['rail_interface']['track_interface']:
        raise ValueError('Installed vehicle and civil wheel/rail interfaces disagree')
    physical=dict(schema='osr-railway-closure-physical/1',
        installed_vehicle_and_station_candidate_id=installed['candidate_id'],
        body_candidate_id=installed['vehicle_candidate_id'],
        civil_candidate_id=civil['civil_candidate_id'],
        terminal_geometry_id=installed['terminal_geometry']['geometry_id'])
    result=dict(schema='osr-railway-closure-bundle/1',candidate_id=identity(physical),
        physical_definition=physical,installed_component_candidate_id=installed['candidate_id'],
        installed_mass_evaluation_id=installed['evaluation_id'],civil_evaluation_id=civil['evaluation_id'],
        body_evaluation_id=installed['body_evaluation_id'],
        purpose='Reconciled research assembly; no integrated selection or inherited physical approval',**FLAGS)
    result['evaluation_id']=identity(result)
    return result
