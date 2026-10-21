"""Controlled user specification and study/physical evidence allocation."""
from hashlib import sha256
import json
from pathlib import Path
from . import model
INPUT=Path(__file__).with_name('data')/'station-powered-specification.json'

# User steering after the supplied document. Preserve the authored source and
# its digest while exposing the effective requirement used by new designs.
AMENDMENTS={
    1:'Develop fixed station and located midpoint-booster LSM zones with unpowered coasting outside those finite zones. Retain ferrite-PM-biased support/guidance and no onboard main traction. Count all booster equipment, interfaces and power.',
    4:'Use a 1.5 km urban spacing target minimum, approximately 2 km urban mean and explicitly classified 4–5 km suburban legs with located top-up accelerators where required. Preserve mandatory passenger-transfer junction stops and expose any shorter spacing as a conflict. Retain 1 km/90 s authored and 1 km/88 s developed cases as component benchmarks, not new route validation. The study speed limit remains 80 km/h; longer profiles require their own force, services, protection and recovery verification.',
    25:'Compare and price finite station and booster winding lengths and fixed groups against qualified sectioned supplies. A longer station gap cannot reuse a 200 m winding without an overlap/force/voltage check. Include phase-correct section handover and inactive-stator faults; no physical acceptance is implied by offline replay.',
    56:'Use independent fixed lines and passenger transfers at junction stations. Do not route trains between mainlines. Preserve located transfer nodes; any straight-chord rerouting requires fresh site and civil classification. Terminal/depot turnback geometry remains separately designed, costed and qualified.',
    57:'Provide recovery from every stop position on the longer station/booster corridors, including passive coasting portions. Count accessible recovery posts or rescue equipment, towing time, cable reach, anchors, protected services energy and staffing. A midpoint accelerator cannot move a train stopped outside its finite zone.',
    70:'Package and price station and located booster converters, feeders, protection, DC links, braking resistors, controls, cooling, access and cabinet foundations. Resolve simultaneous duty and utility connection. Passenger stations and nonpassenger accelerator sites are separate assets.'}


def register():
    data=json.loads(INPUT.read_text());source=model.ROOT/data['source']
    if sha256(source.read_bytes()).hexdigest()!=data['source_sha256']:raise ValueError('station specification changed; reconcile controlled requirements')
    if [r['number'] for r in data['requirements']]!=list(range(1,101)):raise ValueError('complete 100-item station specification required')
    for row in data['requirements']:
        n=row['number']
        if n in AMENDMENTS:
            row.update(source_requirement=row['requirement'],requirement=AMENDMENTS[n],
                amendment='User fixed-line transfer and urban/suburban spacing instructions, 21 October 2026',
                amendment_configuration='ferrite-maglev-study.toml [operating_strategy]')
        if n in {3,36,37,38,43,44,45,68,69,81,85,97}:owner='station_structure.body'
        elif n in {59,60,61,62,63,64,65,66,67,86,91,98}:owner='station_structure.civil/production'
        elif n in {10,11,12,13,14,15,16,17,18,19,20,21,22,24,78,79,95}:owner='station_structure.magnetic_reference; field.study'
        elif 47<=n<=58 or n in {82,83,87}:owner='Rust station launch/support contracts; offline replays'
        elif n in {75,76,77,84,88,89,99,100}:owner='configuration/geometry/manufacturing/workflow'
        else:owner='station.trajectory/evaluate; model/configuration'
        row.update(implementation_owner=owner,digital_scope='Implemented bounded study or allocated interface; detailed/physical qualification remains open',physical_evidence=[],accepted=False)
    data.update(accepted_requirements=0,implemented_complete_system=False,**model.FLAGS)
    return data
