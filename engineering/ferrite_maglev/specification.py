"""Controlled user specification and study/physical evidence allocation."""
from hashlib import sha256
import json
from pathlib import Path
from . import model
INPUT=Path(__file__).with_name('data')/'station-powered-specification.json'


def register():
    data=json.loads(INPUT.read_text());source=model.ROOT/data['source']
    if sha256(source.read_bytes()).hexdigest()!=data['source_sha256']:raise ValueError('station specification changed; reconcile controlled requirements')
    if [r['number'] for r in data['requirements']]!=list(range(1,101)):raise ValueError('complete 100-item station specification required')
    for row in data['requirements']:
        n=row['number']
        if n in {3,36,37,38,43,44,45,68,69,81,85,97}:owner='station_structure.body'
        elif n in {59,60,61,62,63,64,65,66,67,86,91,98}:owner='station_structure.civil/production'
        elif n in {10,11,12,13,14,15,16,17,18,19,20,21,22,24,78,79,95}:owner='station_structure.magnetic_reference; field.study'
        elif 47<=n<=58 or n in {82,83,87}:owner='Rust station launch/support contracts; offline replays'
        elif n in {75,76,77,84,88,89,99,100}:owner='configuration/geometry/manufacturing/workflow'
        else:owner='station.trajectory/evaluate; model/configuration'
        row.update(implementation_owner=owner,digital_scope='Implemented bounded study or allocated interface; detailed/physical qualification remains open',physical_evidence=[],accepted=False)
    data.update(accepted_requirements=0,implemented_complete_system=False,**model.FLAGS)
    return data
