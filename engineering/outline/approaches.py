"""Open proposal intake; the current numerical adapters do not bound invention."""
from copy import deepcopy
from pathlib import Path
import tomllib

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity

PRODUCER='engineering/outline/approaches.py'
POLICY='engineering/outline/transport-goal.toml'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,
    selected_reference_changed=False,manufacturing_release=False,
    operating_release=False,native_evaluator_admission=False)
REQUIRED_OUTPUTS=('passenger-service-and-geographic-access', 'geometry-and-interfaces',
    'mass-support-and-energy', 'performance-and-stopping',
    'production-installation-and-repair', 'installed-and-whole-life-cost',
    'assumptions-uncertainties-and-physical-evidence')


def _seal(value,key):
    value[key]=identity(value)
    return value


def catalogue(root=ROOT):
    root=Path(root);policy=tomllib.loads((root/POLICY).read_text())
    if (policy.get('schema')!='osr-open-transport-search-policy/1'
            or policy.get('search_space_closed') is not False
            or policy.get('reference_is_mandatory') is not False):
        raise ValueError('An open, goal-led transport policy is required')
    rows=policy['approaches'];ids=[r['id'] for r in rows]
    if len(ids)!=len(set(ids)):raise ValueError('Unique approach identifiers required')
    return _seal(dict(schema='osr-open-transport-approaches/1',policy=policy,
        examples_are_exhaustive=False,custom_proposals_allowed=True,
        capability_declarations_grant_dispatch=False,
        selection_scope='Explicitly evaluated alternatives only',
        required_comparison_outputs=list(REQUIRED_OUTPUTS),
        source_sha256={n:digest(root/n) for n in (PRODUCER,POLICY,'engineering/station_rail/common.py')},
        **FLAGS),'catalogue_id')


def propose(value,*,requirements_id,root=ROOT):
    """Accept an unfamiliar idea for research without inventing its evidence.

    This intake neither admits an evaluator nor reuses reference mass, force,
    cost or qualification. Bounded calculated assumptions remain available to
    an eventual outline adapter; an exact market counterpart is not compulsory.
    """
    value=deepcopy(value)
    if not isinstance(value,dict) or not isinstance(requirements_id,str) or not requirements_id.strip():
        raise ValueError('Explicit proposal and transport requirements identity required')
    for key in ('name','approach','transport_function','concept'):
        if not isinstance(value.get(key),str) or not value[key].strip():
            raise ValueError('Explicit '+key+' required')
    # Unknown names are deliberately valid: this list is not a technology gate.
    encoded(value)
    policy=catalogue(root)
    definition_id=identity(value)
    tasks=[_seal(dict(output=output,action='Define or connect an approach-specific model and bounded inputs',
        approach_definition_id=definition_id,requirements_id=requirements_id,
        physical_failure_inferred=False),'task_id') for output in REQUIRED_OUTPUTS]
    return _seal(dict(schema='osr-transport-approach-proposal/1',proposal=value,
        requirements_id=requirements_id,policy_id=policy['catalogue_id'],approach_definition_id=definition_id,
        research_intake='accepted',outline_acceptance='not-assessed',
        evaluator_status='requires-explicit-adapter-and-input-contract',
        physical_feasibility='not-assessed',comparison_admitted=False,
        physical_candidate_id=None,performance=None,mass=None,cost=None,
        automatic_dispatch=False,inherits_reference_results=False,
        next_tasks=tasks,source_sha256=policy['source_sha256'],**FLAGS),'proposal_id')
