"""Executed independent SUMO timetable/berth cross-check on retained geography.

This is a railway kinematic/block comparison, not a magnetic force, power,
braking-hardware or GoA4 acceptance test. Raw independent outputs are retained.
"""
from hashlib import sha256
import gzip
import json
import math
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from . import model, delivery_platform as platform

ROOT=model.ROOT
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/operations-crosscheck'
CITY=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
SCHEMA='osr-independent-operations-crosscheck/1'
SOURCES=[dict(title='Eclipse SUMO railway models and custom dynamics',url='https://sumo.dlr.de/docs/Simulation/Railways.html'),
    dict(title='Eclipse SUMO installation and Python packages',url='https://sumo.dlr.de/docs/Downloads.php')]

def source_paths():return sorted({Path(__file__),ROOT/'engineering/analysis/tests/test_ferrite_maglev_operations_crosscheck.py',
    Path(platform.__file__),Path(platform.operating_plan.__file__),CITY/'city.json',CITY/'baghdad.corridor.geojson',CITY/'engineering/maglev/summary.json'})
def sources():return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in source_paths()}
def xml(value):ET.indent(value);return ET.tostring(value,encoding='utf-8',xml_declaration=True)+b'\n'

def free_running_time(distance_m,*,accel_m_s2=.7,decel_m_s2=.7,max_speed_m_s=20.):
    for v in (distance_m,accel_m_s2,decel_m_s2,max_speed_m_s):platform.finite(v,minimum=1e-9)
    speed=min(max_speed_m_s,math.sqrt(2*distance_m/(1/accel_m_s2+1/decel_m_s2)))
    cruise=max(0.,distance_m-speed**2/(2*accel_m_s2)-speed**2/(2*decel_m_s2))
    return speed/accel_m_s2+cruise/speed+speed/decel_m_s2

def binaries():
    import sumo
    base=Path(sumo.SUMO_HOME)/'bin'
    paths={name:base/name for name in ('sumo','netconvert')}
    if any(not p.is_file() for p in paths.values()):raise RuntimeError('Install pinned eclipse-sumo to execute independent operations')
    return paths

def input_files(line,*,train_mass_kg,scenario='nominal',headway_s=240.,services=4,dwell_s=60.):
    if scenario not in {'nominal','variable-dwell','receiver-failure','capacity-negative-control'}:raise ValueError('named SUMO scenario required')
    platform.finite(train_mass_kg,minimum=1000,maximum=1e7);platform.finite(headway_s,minimum=1,maximum=3600)
    if type(services) is not int or not 1<=services<=50:raise ValueError('bounded independent services required')
    stops=line['stops'];length=line['length_m'];train_length=6*17+5*.5
    if len(stops)<2 or abs(stops[0]['chainage_m'])>.1 or abs(stops[-1]['chainage_m']-length)>.1:raise ValueError('full endpoint passenger stops required')
    nodes=ET.Element('nodes');edges=ET.Element('edges');additional=ET.Element('additional');routes=ET.Element('routes');expected=[]
    # Custom Rail dynamics uses kN and kW, mass in kg. Setting traction to
    # (m*a + drag) isolates the stated kinematic comparison. It is not an LSM
    # force claim. Explicit blocks/berths exercise independent queueing.
    ET.SubElement(routes,'vType',id='candidate-kinematic',vClass='rail_urban',carFollowModel='Rail',trainType='custom',
        length=str(train_length),mass=str(train_mass_kg),massFactor='1',maxSpeed='20',accel='.7',decel='.7',emergencyDecel='1.0',
        maxPower='1000000000',maxTraction=str((train_mass_kg*.7+200)/1000),resCoef_constant='.2',resCoef_linear='0.000000001',resCoef_quadratic='0.000000001',
        sigma='0',speedFactor='1',speedDev='0',minGap='5',tau='1',startupDelay='0')
    for direction in ('forward','reverse'):
        positions=[s['chainage_m'] for s in stops] if direction=='forward' else [length-s['chainage_m'] for s in reversed(stops)]
        ids=[s['id'] for s in stops] if direction=='forward' else [s['id'] for s in reversed(stops)]
        chain=[-220.,*positions,length+220.];lane_y=0 if direction=='forward' else 20
        for i,x in enumerate(chain):ET.SubElement(nodes,'node',id=f'{direction}-n{i}',x=str(x),y=str(lane_y),type='rail_signal' if 0<i<len(chain)-1 else 'priority')
        edge_ids=[]
        for i,(first,last) in enumerate(zip(chain,chain[1:])):
            eid=f'{direction}-e{i}';edge_ids.append(eid);ET.SubElement(edges,'edge',id=eid,**{'from':f'{direction}-n{i}','to':f'{direction}-n{i+1}'},speed='20',numLanes='1',allow='rail_urban',length=str(last-first))
        ET.SubElement(routes,'route',id=direction,edges=' '.join(edge_ids))
        for j,station in enumerate(ids):
            edge_length=chain[j+1]-chain[j]
            ET.SubElement(additional,'busStop',id=direction+'-'+station,lane=edge_ids[j]+'_0',startPos=str(max(0.,edge_length-train_length-2)),endPos=str(edge_length-.1),friendlyPos='true')
        for i in range(services):
            depart=i*(10. if scenario=='capacity-negative-control' else headway_s)
            vid=f'{direction}-{i}';vehicle=ET.SubElement(routes,'vehicle',id=vid,type='candidate-kinematic',route=direction,depart=str(depart),departPos='219.9',departSpeed='0')
            reference=depart
            for j in range(1,len(ids)):
                runtime=free_running_time(positions[j]-positions[j-1]);reference+=runtime
                duration=0. if j==len(ids)-1 else dwell_s
                if scenario=='variable-dwell' and i==0 and j==1:duration+=30
                if scenario=='receiver-failure' and i==0 and j==1:duration+=300
                ET.SubElement(vehicle,'stop',busStop=direction+'-'+ids[j],duration=str(duration))
                expected.append(dict(vehicle=vid,station=ids[j],direction=direction,stop=direction+'-'+ids[j],free_running_arrival_s=reference,dwell_s=duration,scheduled_departure_s=depart,leg_distance_m=positions[j]-positions[j-1]));reference+=duration
    vehicles=routes.findall('vehicle')
    for vehicle in vehicles:routes.remove(vehicle)
    for vehicle in sorted(vehicles,key=lambda v:(float(v.get('depart')),v.get('id'))):routes.append(vehicle)
    return {'nodes.nod.xml':xml(nodes),'edges.edg.xml':xml(edges),'stops.add.xml':xml(additional),'services.rou.xml':xml(routes)},expected

def execute(directory,*,line=None,configuration_sha256=None,train_mass_kg=None,scenario='nominal',step_s=.1,services=4):
    if line is None:line=platform.baseline(CITY)['lines'][-1]
    if train_mass_kg is None or configuration_sha256 is None:
        from . import candidate_magnetics
        candidate=candidate_magnetics.definition();train_mass_kg=candidate['controlled_aw3_kg']*candidate['cars'];configuration_sha256=candidate['configuration_sha256']
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True);commands=[];tools=binaries()
    files,expected=input_files(line,train_mass_kg=train_mass_kg,scenario=scenario,services=services,headway_s=line['headway_s'])
    for n,b in files.items():(directory/n).write_bytes(b)
    def command(argv,log):
        result=subprocess.run(argv,cwd=directory,capture_output=True,text=True,timeout=300)
        (directory/log).write_text(result.stdout+result.stderr);commands.append(dict(command=[str(v).replace(str(directory),'$RUN') for v in argv],exit_code=result.returncode,log=log))
        if result.returncode:raise RuntimeError('Independent SUMO command failed: '+log)
    command([str(tools['netconvert']),'--node-files','nodes.nod.xml','--edge-files','edges.edg.xml','--output-file','network.net.xml','--no-turnarounds','true','--no-internal-links','true'],'netconvert.txt')
    command([str(tools['sumo']),'--net-file','network.net.xml','--route-files','services.rou.xml','--additional-files','stops.add.xml',
        '--step-length',str(step_s),'--step-method.ballistic','false','--begin','0','--end','3600','--time-to-teleport','-1','--no-step-log','true','--seed','7',
        '--tripinfo-output','tripinfo.xml','--stop-output','stop-output.xml','--collision-output','collisions.xml','--summary-output','summary.xml'],'sumo.txt')
    observations=ET.parse(directory/'stop-output.xml').getroot();trip_root=ET.parse(directory/'tripinfo.xml').getroot()
    lookup={(r['id'],r['busStop']):r for r in (e.attrib for e in observations.findall('stopinfo'))};comparisons=[]
    for e in expected:
        r=lookup.get((e['vehicle'],e['stop']))
        if r is None:comparisons.append(dict(**e,completed=False));continue
        arrival=float(r['started']);ended=float(r['ended']);comparisons.append(dict(**e,completed=True,arrival_s=arrival,departure_s=ended,
            free_running_difference_s=arrival-e['free_running_arrival_s'],actual_dwell_s=ended-arrival))
    collisions=list(ET.parse(directory/'collisions.xml').getroot());trips=[e.attrib for e in trip_root.findall('tripinfo')]
    nominal=scenario=='nominal';complete=all(r['completed'] for r in comparisons) and len(trips)==2*services
    max_diff=max((abs(r.get('free_running_difference_s',0)) for r in comparisons),default=0.)
    delayed=any(float(t.get('departDelay','0'))>1 for t in trips) or any(r.get('free_running_difference_s',0)>5 for r in comparisons)
    screens=dict(complete=complete,no_collisions=not collisions,dwell=all(r.get('actual_dwell_s',-1)>=r['dwell_s']-.11 for r in comparisons),
        nominal_free_running_agreement=max_diff<=5 if nominal else True,
        capacity_negative_control_exposes_delay=delayed if scenario=='capacity-negative-control' else True)
    version=subprocess.check_output([str(tools['sumo']),'--version'],text=True).splitlines()[0]
    result=dict(schema=SCHEMA,configuration_sha256=configuration_sha256,planning_line=line['id'],planning_line_sha256=platform.digest(line),train_mass_kg=train_mass_kg,
        scenario=scenario,step_s=step_s,integration_method='SUMO Rail supported semi-implicit Euler',tool_version=version,binary_sha256={n:sha256(p.read_bytes()).hexdigest() for n,p in tools.items()},commands=commands,
        comparisons=comparisons,trips=trips,collision_count=len(collisions),maximum_free_running_difference_s=max_diff,screens=screens,study_pass=all(screens.values()),
        sources=SOURCES,scope='Executed independent SUMO Rail custom kinematic/block/berth comparison. Prescribed kinematic traction is not the fixed-zone magnetic actuator model. No Rust-authority, charge, support/capture, curved magnetic behaviour or GoA4 acceptance is inferred.',**platform.FLAGS)
    (directory/'result.json').write_bytes(platform.encoded(result));return result

def publish(output=OUTPUT):
    from . import candidate_magnetics
    before={**sources(),**candidate_magnetics.sources()};candidate=candidate_magnetics.definition();output=Path(output);output.mkdir(parents=True,exist_ok=True)
    summaries=[];files={}
    with tempfile.TemporaryDirectory() as temp:
        for scenario in ('nominal','variable-dwell','receiver-failure','capacity-negative-control'):
            directory=Path(temp)/scenario;r=execute(directory,configuration_sha256=candidate['configuration_sha256'],train_mass_kg=candidate['controlled_aw3_kg']*candidate['cars'],scenario=scenario);summaries.append(r)
            for p in directory.iterdir():files[scenario+'/'+p.name+'.gz']=gzip.compress(p.read_bytes(),mtime=0)
    report=dict(schema=SCHEMA,configuration_sha256=candidate['configuration_sha256'],scenarios=summaries,study_pass=all(r['study_pass'] for r in summaries),**platform.FLAGS)
    files['study.json.gz']=gzip.compress(platform.encoded(report),mtime=0)
    files['README.md']=('\n'.join(['# Independent operations cross-check','',
        'Actual Eclipse SUMO executes the same four passenger stops, six-car length and current candidate mass in both directions. Nominal, delayed dwell, receiver-unavailable berth delay and deliberately overbooked headway cases retain raw network, routes, stops, logs and output.','',
        f'All declared kinematic/block screens passed: **{report["study_pass"]}**. The nominal comparison uses a separate closed-form acceleration/cruise/braking timing oracle with a fixed5s comparison tolerance. Differences are reported, never calibrated away.','',
        'SUMO uses a declared constant-acceleration traction hypothesis for this independent scheduling comparison. It does not evaluate fixed-zone LSM thrust, magnetic suspension, independent capture, hardware braking, charging or actual Rust authority. Those are separate coupled system evaluators. Receiver unavailability here is a berth delay, not a magnetic stopping test.','',
        *[f'[{r["title"]}]({r["url"]})' for r in SOURCES],'',
        'No physical or operational acceptance. Reproduce with `./osr design operations-crosscheck`.',''])).encode()
    if before!={**sources(),**candidate_magnetics.sources()}:raise ValueError('operations inputs changed during execution')
    for n,b in files.items():p=output/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    manifest=dict(schema=SCHEMA,source_sha256=before,files_sha256={n:sha256(b).hexdigest() for n,b in files.items()},**platform.FLAGS)
    (output/'manifest.json').write_bytes(platform.encoded(manifest));return manifest

def verify(output=OUTPUT):
    from . import candidate_magnetics
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes())
    if m.get('schema')!=SCHEMA or m.get('source_sha256')!={**sources(),**candidate_magnetics.sources()}:raise ValueError('independent operations inputs changed')
    if any(m.get(k) is not False for k in platform.FLAGS):raise ValueError('operations study asserted release')
    if {p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}!=set(m['files_sha256'])|{'manifest.json'}:raise ValueError('operations inventory differs')
    for n,h in m['files_sha256'].items():
        p=output/n
        if p.is_symlink() or sha256(p.read_bytes()).hexdigest()!=h:raise ValueError('operations output changed')
    r=json.loads(gzip.decompress((output/'study.json.gz').read_bytes()))
    if r['configuration_sha256']!=candidate_magnetics.definition()['configuration_sha256'] or r['study_pass']!=all(s['study_pass'] for s in r['scenarios']):raise ValueError('operations identity/eligibility differs')
    for scenario in r['scenarios']:
        retained=json.loads(gzip.decompress((output/scenario['scenario']/'result.json.gz').read_bytes()))
        if retained!=scenario:raise ValueError('raw SUMO result differs')
    return dict(verified=True,study_pass=r['study_pass'],scenarios=len(r['scenarios']),**platform.FLAGS)
