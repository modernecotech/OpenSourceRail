"""Identity-safe closure audit for the bounded Baghdad/Samawah pilot corridors.

This adapter deliberately stops before claiming project evaluation when the
existing mapped-project contract cannot carry the exact whole-candidate seed.
It records unknowns as unknown and retains the geometry preflight as ancestry.
"""
from copy import deepcopy
from engineering.station_rail.common import identity

BODY = 'c89556f453e39448a8f3e9bf2d0d4d008f97cd20d252ac417284e40965e261b3'
SEED = '7c916d9828baa5b694bf8f7e416be4fa8c7f196148174df4aa0474441479026d'
RECOVERY_ALTERNATIVE = 'f9aa3afa47a297da855b2741c9e0fde0d77ad3e3211df500f32f901cfadb1877'
PRIOR_GEOMETRY = {
    'geometry-preflight-01': '02f116157a5d170f5bf0ac7deb0a4f6c21f060679a56e619049fcdbd3ce7ee47',
    'geometry-preflight-02': '396679dd33fde69b4cc1cb0cdac751c5203634c603be9fa18d5c071d2a89a225',
}
SEED_EVALUATION_ID = 'fd0efdb85e780ae2529d818b35c5da96e2f89ad4586026ec788391f09ffd8495'
SEED_SERVICE_EVALUATION_ID = 'ae4186756c63f9d75036c20c83b9ffbd2453487c15a9741791e64c0c894d31cd'
SCOPES = (
    'civil-beam-factory', 'shared-pier-foundation-bearings',
    'beam-transport-and-erection', 'running-rails', 'running-rail-fastenings',
    'station-platforms-and-access', 'powered-zones-and-wayside-equipment',
    'grid-connection-and-substations', 'vehicles-and-fleet', 'depot-and-recovery',
    'operations-and-staff', 'energy-and-charging', 'renewals-and-maintenance',
    'land-utilities-and-siteworks',
)


def audit(seed_candidate_id=SEED, body_candidate_id=BODY, *,
          prior_geometry=PRIOR_GEOMETRY, service_seed=None, source_sha256=None):
    """Return a sealed, explicitly held closure record; never manufacture a pass.

    ``service_seed`` may carry exact service evidence from the separately
    published candidate. It is retained as ancestry and is not silently reused
    for either new corridor.
    """
    if seed_candidate_id != SEED or body_candidate_id != BODY:
        raise ValueError('Only the assigned whole-candidate seed and exact body are in scope')
    if prior_geometry != PRIOR_GEOMETRY:
        raise ValueError('Prior geometry trial identities must be preserved exactly')
    sources = deepcopy(source_sha256 or {})
    if any(not isinstance(k, str) or not isinstance(v, str) or len(v) != 64 for k, v in sources.items()):
        raise ValueError('Source path to SHA-256 manifest required')
    corridors = [
        dict(city_slug='baghdad', source_line_id='line-1', scope='first three source stops',
             source_stop_ids=['line-1-2500-0775-s000000', 'line-1-2343-0771-s003515',
                              'line-1-2180-0774-s007014'],
             source_city_input_id='00e098329827f2b8c79cab859f3cd28bd0934f3a65e3d45e7e9fda55b096757c',
             source_planning_revision_id='a1ff73e7303dc85695eabd22f324a6587ffd88e4affb8d1f3e1ebab56e842853',
             prior_corridor_evaluation_id='987b291261717ec50d4dc6e5c3a4ea658fdf0b42e7da7c7f396dc97404976d39',
             prior_corridor_geometry_id='b06a0d4e3a0be595e6287c41ff176dba1b462a85e3a4ef1d277dfd29fdd85dc2',
             prior_alignment_evaluation_id='3abd018afca95785e028e232dc7e5ce632d509a527023f9a14fd3cb747a261a7',
             prior_alignment_screen_passed=False, prior_route_m=7018.440947502994, prior_station_count=3),
        dict(city_slug='samawah', source_line_id='line-3', scope='first-to-last, retain all source stops',
             source_stop_ids=['line-3-0459-0690-s000000', 'line-3-0462-0630-s001225',
                              'line-3-0472-0464-s004639', 'line-3-0473-0450-s004928',
                              'line-3-0478-0356-s006849', 'line-3-0484-0261-s008799'],
             source_city_input_id='dd952bf0526a58894757dee67031894cece6cd4fc45c074d711a8c76188405de',
             source_planning_revision_id='69d952f6d2157d73ab92804ec2f8e30d6d7b5c474c60afc216b95e4e82a3e18d',
             prior_corridor_evaluation_id='8e9122b2f66e793af7fb0e3d418ff519a1583a1fbaec91279d981b5d8b21173b',
             prior_corridor_geometry_id='e8b9afa75e9d76ab98a7392ecdab2ebe388257212dfeec5b0cc51943c9f770f2',
             prior_alignment_evaluation_id='a56ff7e942605e58637c7e199cf0d2c2a8c602411fcad485ad90341a77b8e2c1',
             prior_alignment_screen_passed=True, prior_route_m=8789.10385269246, prior_station_count=6),
    ]
    value = dict(
        schema='osr-mapped-corridor-closure-audit/1',
        candidate_identity=dict(body_candidate_id=BODY, whole_candidate_seed_id=SEED,
            recovery_equipped_alternative_id=RECOVERY_ALTERNATIVE,
            whole_candidate_evaluation_id=SEED_EVALUATION_ID,
            seed_service_evaluation_id=SEED_SERVICE_EVALUATION_ID,
            identity_rule='These are distinct identities; neither is selected or physically accepted.'),
        corridors=corridors,
        service_context=dict(
            seed_normal_places=276, seed_planning_occupancy=0.85,
            seed_demand_pphpd=4000, seed_headway_s=200, seed_dwell_s=35,
            seed_turnback_s=45, seed_full_tail_clearance='counted in seed evaluation; corridor datum unavailable',
            corridor_capacity_pphpd=None, corridor_dwell_s=None, corridor_headway_s=None,
            corridor_full_tail_clearance_m=None, corridor_grade_profile=None,
            corridor_charging_duty=None, corridor_reserve_fleet=None,
            note='Seed service values are recorded for identity/ancestry only; they are not inherited as corridor service.'),
        coverage=dict(platforms=None, powered_zones=None, grid_equipment=None, fleet=None,
            recovery=None, fourteen_cost_scopes=list(SCOPES), scope_costs_USD=None,
            scalar_cost_per_km_used=False),
        seed_service_evidence=deepcopy(service_seed),
        prior_geometry_evaluation_ids=deepcopy(prior_geometry),
        revised_geometry_parameter=dict(name='maximum_deviation_m', value_m=205.0,
            status='proposed next-evaluation parameter only; prior 200 m screen is not a requirement',
            evaluated=False),
        identity_blockers=[
            'The mapped-project bundle physical identity is composed from body, alignment, civil and station geometry; it has no field binding the whole-candidate seed 7c916d... .',
            'The mapped-project service contract requires candidate_id equal to that bundle identity, so re-labeling it with the seed candidate would fail identity derivation and constitute spoofing.',
            'The whole-candidate seed service evaluation is route-specific; it cannot supply new route force-driven motion, fleet, charging or reserve results.',
            'Samawah line-3 source stop IDs and exact source/evaluation hashes must be loaded from the authoritative city source before corridor closure.',
            'The 14-scope mapped-project cost evaluator requires the exact compatible project bundle and service packet; no costs can be derived here.',
        ],
        unknowns=['surveyed vertical grade/profile', 'land and access', 'ground/geotechnical cases',
            'utilities and grid connection', 'platform/site assembly', 'powered-zone length and count',
            'fleet and reserve fleet', 'recovery/depot arrangement', 'corridor energy and charging duty',
            'supplier/site prices', 'physical maturity and acceptance'],
        evaluation_status='held-before-corridor-service-and-cost',
        engineering_accepted=False, physical_accepted=False, selected_reference_changed=False,
        manufacturing_release=False, operating_release=False, movement_authority=False,
        source_sha256=sources,
    )
    value['evaluation_id'] = identity(value)
    return value


def verify(packet):
    """Check record integrity and assert that the hold/release boundary remains."""
    if not isinstance(packet, dict) or packet.get('schema') != 'osr-mapped-corridor-closure-audit/1':
        raise ValueError('Mapped corridor closure audit required')
    if packet.get('evaluation_id') != identity({k: v for k, v in packet.items() if k != 'evaluation_id'}):
        raise ValueError('Closure audit identity mismatch')
    if any(packet.get(k) is not False for k in ('engineering_accepted', 'physical_accepted',
            'selected_reference_changed', 'manufacturing_release', 'operating_release', 'movement_authority')):
        raise ValueError('Held research audit cannot confer acceptance or release')
    if packet.get('coverage', {}).get('scalar_cost_per_km_used') is not False:
        raise ValueError('Scalar cost-per-km multiplication is prohibited')
    if len(packet.get('coverage', {}).get('fourteen_cost_scopes', [])) != 14:
        raise ValueError('All fourteen distinct cost scopes must remain visible')
    return True
