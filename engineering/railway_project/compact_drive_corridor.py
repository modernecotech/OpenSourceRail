"""Identity checks for the source-built compact-drive corridor experiment.

The compact-drive vehicle is a new research candidate. This helper prevents its
body, project bundle, service packet and the older pilot seeds from being
silently interchanged when an experiment stops at an unsupported stage.
"""
from copy import deepcopy

from engineering.station_rail.common import identity

SEED = '7c916d9828baa5b694bf8f7e416be4fa8c7f196148174df4aa0474441479026d'
RECOVERY = 'f9aa3afa47a297da855b2741c9e0fde0d77ad3e3211df500f32f901cfadb1877'
PARENT = '9f6d223074b3438a546d5b3d71cd9b970807387ef0542023bed79bef46dbdeba'
FLAGS = ('engineering_accepted', 'physical_accepted', 'selected_reference_changed',
         'manufacturing_release', 'operating_release', 'movement_authority')


def packet(body, *, route_records, stage_records, holds, source_sha256,
           service_assumptions=None):
    """Seal a source-built corridor result with unresolved quantities explicit.

    Route and stage records may contain successful geometry/project packets or
    exact failure records. Service and cost completeness are derived only from
    exact candidate links; absent values remain ``None``.
    """
    if body.get('schema') != 'osr-vehicle-installation/1':
        raise ValueError('Source-built installed vehicle body required')
    bid = body.get('candidate_id')
    if bid != identity(body.get('physical_definition', {})) or bid in (SEED, RECOVERY):
        raise ValueError('New body identity must be physical and distinct from both pilot seeds')
    if body.get('evaluation_id') != identity({k:v for k,v in body.items() if k!='evaluation_id'}):
        raise ValueError('Sealed source-built body evaluation required')
    if body.get('parent_candidate_id') != PARENT:
        raise ValueError('Exact compact-drive powered-body ancestry required')
    if any(not isinstance(k,str) or not isinstance(v,str) or len(v)!=64 or
           any(c not in '0123456789abcdef' for c in v) for k,v in source_sha256.items()):
        raise ValueError('Source path to lowercase SHA-256 manifest required')
    projects=[]
    for row in stage_records:
        item=deepcopy(row)
        if item.get('kind')=='project-bundle':
            bundle=item.get('packet',{})
            if bundle.get('schema')!='osr-mapped-railway-project-bundle/1':
                raise ValueError('Project bundle stage must carry the native project schema')
            phys=bundle.get('physical_definition',{})
            if phys.get('body_candidate_id')!=bid or bundle.get('body_evaluation_id')!=body.get('evaluation_id'):
                raise ValueError('Project bundle is mixed with another body evaluation')
        if item.get('kind')=='network-service':
            service=item.get('packet',{})
            parent=next((r.get('packet',{}) for r in stage_records if r.get('kind')=='project-bundle'),{})
            if (service.get('candidate_id')!=parent.get('candidate_id') or
                service.get('bundle_evaluation_id')!=parent.get('evaluation_id')):
                raise ValueError('Service packet is not bound to the exact project bundle')
        projects.append(item)
    value=dict(schema='osr-source-compact-drive-corridor/1',
        candidate_identity=dict(body_candidate_id=bid,body_evaluation_id=body['evaluation_id'],
            parent_candidate_id=PARENT,whole_candidate_seed_id=SEED,
            recovery_equipped_alternative_id=RECOVERY,
            selection='unselected research candidate; no inheritance from either pilot seed'),
        body_definition_complete=body.get('layout_definition_complete') is True,
        installed_mass_complete=body.get('installed_mass_complete') is True,
        route_records=deepcopy(route_records),stage_records=projects,holds=list(holds),
        service=dict(normal_passenger_capacity_per_train=None,dwell_s=None,
            full_tail_clearance_m=None,grade_profile=None,charging_duty=None,
            reserve_fleet=None,demand_cases=deepcopy(service_assumptions or []),
            force_driven=False,service_complete=False),
        infrastructure=dict(platforms=None,powered_zones=None,grid_equipment=None,
            fleet=None,recovery=None),
        costs=dict(scope_count=14,scope_costs_USD=None,scalar_cost_per_km_used=False,
            complete=False,price_maturity='unknown'),
        source_sha256=deepcopy(source_sha256),**{k:False for k in FLAGS})
    value['evaluation_id']=identity(value)
    return value


def verify(value):
    if value.get('schema')!='osr-source-compact-drive-corridor/1':
        raise ValueError('Source compact-drive corridor result required')
    if value.get('evaluation_id')!=identity({k:v for k,v in value.items() if k!='evaluation_id'}):
        raise ValueError('Candidate corridor result identity mismatch')
    if any(value.get(k) is not False for k in FLAGS):
        raise ValueError('Research result cannot grant acceptance or release')
    if value['service']['service_complete'] or value['costs']['complete']:
        raise ValueError('Held result cannot claim complete service or cost')
    return True
