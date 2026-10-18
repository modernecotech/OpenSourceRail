"""Unit/revision/serial-specific QA plans; simulated hold points are not tests."""
from engineering.twin_workflow import core

STAGES=('design','factory','transport','installed')
REQUIRED={
    'design':['unit-definition','handling-and-connections'],
    'factory':['material-trace','dimensions','embedded-interfaces'],
    'transport':['damage-and-identity'],
    'installed':['positive-lock','survey','interface-test'],
}


def requirements(unit):
    values={stage:list(tests) for stage,tests in REQUIRED.items()}
    if unit.get('service_type')=='drainage':values['factory'].append('leak-and-fall-test')
    if unit.get('service_type') in {'power','data'}:values['factory'].append('continuity-isolation-and-identification')
    if unit.get('process')=='precast':values['factory'].append('strength-and-curing')
    if unit.get('process')=='site-concrete':values['installed'].append('strength-and-curing')
    return values


def template(unit):
    return dict(unit_id=unit['id'],unit_revision=unit['revision'],serial=None,batch=None,
        required=requirements(unit),material_certificates=[],records=[],
        dimensional_plan=[dict(axis=axis,nominal_extent_m=unit['bounds_m'][1][i]-unit['bounds_m'][0][i],tolerance_m=None,measured_value_m=None) for i,axis in enumerate('xyz')],
        installed_survey=[dict(axis=axis,measured_coordinate_m=None,approved_tolerance_m=None) for axis in 'xyz'],
        status='unexecuted; serial, measured results and independent acceptance required',manufacturing_release=False)


def assess(unit,traveller,*,interface_revision=None):
    expected=requirements(unit)
    if traveller.get('unit_id')!=unit['id'] or traveller.get('unit_revision')!=unit['revision']:
        return dict(state='stale',retest=list(STAGES),reason='manufactured unit definition/revision changed',accepted=False)
    records=traveller.get('records',[]);coverage={};retest=[]
    for stage,tests in expected.items():
        matching={}
        for record in records:
            if record.get('stage')!=stage:continue
            if record.get('unit_revision')!=unit['revision'] or record.get('serial')!=traveller.get('serial'):continue
            if not traveller.get('serial') or not record.get('evidence_sha256') or not record.get('qualified_reviewer'):continue
            digest=record['evidence_sha256']
            if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):continue
            if stage in {'design','installed'} and record.get('interface_revision')!=interface_revision:continue
            matching[record.get('test')]=record.get('state')
        states=[matching.get(test,'unknown') for test in tests]
        coverage[stage]=dict(required=tests,states=dict(zip(tests,states)),complete=all(s=='passed' for s in states))
        if not coverage[stage]['complete']:retest.append(stage)
    state='failed' if any('failed' in r['states'].values() for r in coverage.values()) else 'passed-records' if not retest else 'hold'
    return dict(state=state,coverage=coverage,retest=retest,
        accepted=False,scope='Record consistency/coverage only; evidence hashes and reviewer claims still require authenticated external verification')
