"""Common applicability register; relationships never confer acceptance."""
from . import transition,evacuation,configuration


def register():
    cfg=configuration.selected();records=[]
    evac=evacuation.onboard_requirements();evac_ids=[r['id'] for r in evac]
    for original in transition.requirement_inputs():
        row=dict(original,register_revision='V052-STATION-POWERED-REQUIREMENTS-1',applicability=['all-primary-configurations'],
            supersedes=[],superseded_by=[],verification_method=['analysis','independent-review','applicable-rig-and-system-tests'],
            evidence_links=[],study_links=['docs/design-engine/ferrite-maglev/reference/result.json'])
        if row['id']=='CIV-004':row.update(
            applicability=['walkway-reference','onboard-evacuation-no-walkway-until-approved-alternative'],
            alternative_requirement_ids=evac_ids,
            selection_condition='Retain walkway fallback until all evacuation requirements and route-specific independent approval are accepted',
            alternative_selected=False)
        records.append(row)
    for original in evac:
        records.append(dict(original,register_revision='V052-STATION-POWERED-REQUIREMENTS-1',
            applicability=['onboard-evacuation-no-walkway'],related_requirements=['CIV-004'],
            supersedes=[],superseded_by=[],verification_method=['configuration-review','full-scale-device-and-route-tests','independent-acceptance'],
            evidence_links=[],study_links=['docs/design-engine/ferrite-maglev/reference/evacuation-study.json.gz']))
    from . import specification
    for original in specification.register()['requirements']:
        records.append(dict(original,register_revision='V052-STATION-POWERED-REQUIREMENTS-1',applicability=['station-powered'],supersedes=[],superseded_by=[],evidence_links=[],study_links=['docs/design-engine/ferrite-maglev/station-powered/result.json.gz','docs/design-engine/ferrite-maglev/station-structure/result.json'],verification_method=['executed-digital-study','qualified-component-and-system-tests','independent-acceptance']))
    return dict(schema='osr-applicable-requirements/1',revision='V052-STATION-POWERED-REQUIREMENTS-1',
        configuration_revision=cfg.revision,requirements=records,
        selected_research_variant=cfg.evacuation['selected'],walkway_removal_approved=False,
        accepted_requirements=0,**transition.FLAGS)
