"""Audit displayed civil objects against the actual spatial assembly.

A candidate association identifies a review domain; it never asserts that a
visual reservation equals an analysed section, spring or contact profile.
"""
from collections import Counter
from engineering.industrialisation.common import fingerprint

ROLE_DOMAINS={
    'track-slab':('deck','mass/section allowance; slab not a separate spatial element'),
    'support-deck-envelope':('deck','rectangular display envelope; analysed composite section is independent'),
    'rail-surrogate':('rail','display rail has no released contact-profile or section equivalence'),
    'replaceable-fastening-study':('rail-pad','homogenised translational pad stiffness; discrete anchors/toes not resolved'),
    'bearing-seat-cap-envelope':('cap','display cap and analysed cap sections/datum require reconciliation'),
    'replaceable-bearing-interface':('bearing','spring law requires actual bearing mode, installation datum and capacity'),
    'jacking-pad-reservation':('temporary-works','jacking-stage structure/loads not represented in running-service assembly'),
}


def audit(model,infrastructure,structure,configuration):
    items=infrastructure['items'];ids=[item['id'] for item in items]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate displayed civil identity')
    unknown={item['role'] for item in items}-ROLE_DOMAINS.keys()
    if unknown:raise ValueError('unregistered civil correspondence role: '+','.join(sorted(unknown)))
    elements=[]
    for index,e in enumerate(structure.elements):
        elements.append(dict(index=index,kind=e['kind'],nodes=e['nodes'],node_coordinates_m=[structure.coordinates[n].tolist() for n in e['nodes']],
            station_start_m=e['station_start'],station_end_m=e['station_end'],track=e['track'],length_m=e['length'],
            section_properties_sha256=fingerprint(e['properties']),mass_kg=e['length']*e['properties']['mass_kg_m']))
    spring_kinds=Counter(s['kind'] for s in structure.springs)
    rows=[]
    for item in items:
        domain,boundary=ROLE_DOMAINS[item['role']]
        indices=[e['index'] for e in elements if e['kind']==domain]
        rows.append(dict(instance_id=item['id'],part_id=item['part_id'],role=item['role'],analysis_domain=domain,
            cad_geometry_sha256=fingerprint(item['geometry']),cad_transform=item['transform'],cad_properties=item['properties'],
            candidate_analysis_element_indices=indices,candidate_analysis_spring_count=spring_kinds.get(domain,0),
            association_status='unreconciled-reservation',geometry_equivalent=False,mass_equivalent=False,
            datum_equivalent=False,material_equivalent=False,capacity_qualified=False,boundary=boundary))
    visible_domains={r['analysis_domain'] for r in rows}
    absent=sorted((set(e['kind'] for e in elements)|set(spring_kinds))-visible_domains)
    return dict(schema='osr-civil-cad-analysis-audit/1',configuration_sha256=fingerprint(model),analysis_configuration_sha256=fingerprint(configuration),
        displayed_instance_count=len(items),audited_instance_count=len(rows),every_displayed_instance_accounted_for=True,
        displayed_role_counts=dict(Counter(item['role'] for item in items)),analysis_element_counts=dict(Counter(e['kind'] for e in elements)),
        analysis_spring_counts=dict(spring_kinds),rows=rows,analysis_elements=elements,
        analysis_domains_without_displayed_equivalent=absent,analysis_length_m=structure.length,analysis_track_centres_m=structure.tracks,
        displayed_gauge_m=infrastructure['gauge_m'],analysis_gauge_m=structure.gauge,
        rail_pad_basis=infrastructure['support_study'],
        complete_cad_analysis_equivalence=False,physical_validation=False,production_released=False,
        open_domains=['one displayed study span/track is not the complete two-track multi-span analysis assembly',
            'reconcile each section, mass allowance, material and installation datum before equivalence',
            'explicit piers/foundations and construction/jacking stages',
            'actual rail profile, discrete fastening/anchorage and bearing calibration'])
