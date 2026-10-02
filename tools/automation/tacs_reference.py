#!/usr/bin/env python3
"""Ten real processes, asynchronous signed messages, synthetic local sensor ports.

The coordinator supplies physics only to the train's own port and independent
wayside proving ports. Authority inputs are exclusively communicated committed
prefixes. It never edits consensus logs or interlocking state. Virtual time is
repeatable; filesystem persistence and SIGKILL/restart use the actual OS.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, os, select, subprocess, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'engineering/assurance/tacs'
DT = 100_000_000
IDS = (1001,1002,1003,900,901,902,101,102)
CASES = ('None','RadioPartition','RadioReconnection','ControllerRestart','VoterRestart',
         'FrozenOutput','IntegrityLoss','PositionUncertainty','PointsDetectionLost','ChargerStuck',
         'IncompleteCharge','ChargerMisaligned','EmergencyDepartureConnected','CivilClosure','CivilDataStale')

def validate_reference_model(model):
    """This physics fixture is deliberately bounded, not an arbitrary railway."""
    expected_paths=((1,'Forward',[0,2,4]),(2,'Reverse',[5,3,1]))
    if model['runtime']['voters']!=[1001,1002,1003] or len(model['resources'])!=7:
        raise ValueError('unsupported reference membership/resource geometry')
    for route_id,direction,resources in expected_paths:
        route=next(r for r in model['routes'] if r['id']==route_id)
        if route['direction']!=direction or [s['resource'] for s in route['segments']]!=resources:
            raise ValueError('unsupported reference route')
        if any(s['start_mm']!=n*100000 or s['end_mm']!=(n+1)*100000 or s['speed_limit_mmps']!=10000 or s['downhill_permille']!=(3 if n==1 else 0) for n,s in enumerate(route['segments'])):
            raise ValueError('unsupported reference extents/speed/grade; update and calibrate physics first')
        if [stop['at_mm'] for stop in route['stopping_locations']]!=[50000,270000] or any(stop['minimum_departure_energy_wh']!=500 for stop in route['stopping_locations']):
            raise ValueError('unsupported reference berth/energy profile')
    if sorted(t['config']['owner']['train'] for t in model['trains'])!=[101,102]:
        raise ValueError('unsupported reference fleet')
    for train in model['trains']:
        config=train['config']
        if config['length_mm']!=10000 or config['minimum_deceleration_mmps2']!=1000 or config['reaction_time_ms']!=500 or config['stop_margin_mm']!=1000 or config['maximum_position_uncertainty_mm']!=20000:
            raise ValueError('unsupported physical formation/braking/uncertainty profile')
        if train['permitted_route']!=(1 if config['owner']['train']==101 else 2) or config['owner']['session']!=1:
            raise ValueError('unsupported reference route/session')
    for index,resource in enumerate(model['resources']):
        expected_conflicts=[2,3] if index in (2,3) else [index]
        if resource['id']!=index or resource['section']!=100+index or resource['controller']!=900 or resource['conflicts']!=expected_conflicts:
            raise ValueError('unsupported physical resource identity/conflict domain')
    if model['protected_work_resources']!=[6] or len(model['controllers'])!=1 or model['controllers'][0]['id']!=900:
        raise ValueError('unsupported protection controller/possession profile')

class Process:
    def __init__(self, entity, directory, output=False):
        binary = 'osr-safety-output' if output else 'osr-train-agent' if entity < 900 else 'osr-wayside-agent'
        self.entity = entity
        self.proc = subprocess.Popen([str(ROOT/'target/release'/binary),'--model',str(BASE/'railway-model.json'),
            '--deployment',str(BASE/'deployment.json'),'--entity',str(entity),'--journal',str(Path(directory)/f'{entity}.journal')],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
        self.buffer = b''
    def call(self, data):
        encoded = json.dumps(data,separators=(',',':')).encode()+b'\n'
        remaining=memoryview(encoded)
        while remaining:
            remaining=remaining[self.proc.stdin.write(remaining):]
        while b'\n' not in self.buffer:
            if not select.select([self.proc.stdout],[],[],15)[0]:
                raise RuntimeError(f'process {self.entity} deadline exceeded')
            part = os.read(self.proc.stdout.fileno(),1024*1024)
            if not part:
                raise RuntimeError(f'process {self.entity} exited: {self.proc.stderr.read().decode()}')
            self.buffer += part
        line,self.buffer = self.buffer.split(b'\n',1)
        return json.loads(line)
    def stop(self):
        self.proc.kill(); self.proc.wait(timeout=5)
        for port in (self.proc.stdin,self.proc.stdout,self.proc.stderr): port.close()

class Installation:
    def __init__(self, directory, case):
        validate_reference_model(json.loads((BASE/'railway-model.json').read_text()))
        self.directory,self.case=directory,case;self.maxsteps=1400
        self.processes={i:Process(i,directory) for i in IDS}
        self.outputs={i:Process(i,directory,output=True) for i in (101,102)}
        self.output_sequence={i:0 for i in (101,102)}
        self.pids=[p.proc.pid for p in [*self.processes.values(),*self.outputs.values()]]
        self.queue=collections.deque(); self.now=1; self.status={}; self.leader=None
        self.ledger=None; self.sequence={r:0 for r in range(7)}; self.points=1
        self.positions={101:50000,102:50000}; self.speeds={101:0,102:0}
        self.charger_enabled={101:False,102:False}
        self.energy={101:400,102:400}; self.inputs={}; self.tick_outputs={}; self.arrivals=[]; self.entries=[]
        self.possession_sent=False
        self.fault=False; self.fault_at=None; self.recovered=False; self.retained=False
        self.rejections=0; self.bytes=0; self.max_queue=0; self.trace=[]; self.restored=False
    def close(self):
        for p in [*self.processes.values(),*self.outputs.values()]: p.stop()
    def accept(self,entity,answer, destination=None):
        if not answer['ok']:
            self.rejections+=1
            if self.rejections<8:print(f"rejected {entity}: {answer['error']}",flush=True)
            return None
        result=answer['result']; self.status[entity]=result
        if entity in (1001,1002,1003) and result['role']=='Leader':
            self.leader=entity
            if result.get('resources'):self.ledger=result['resources']
        for packet in result.get('packets',[]):
            if entity<900:
                to=0; envelope=packet
            else:to=packet['to'];envelope=packet['envelope']
            if destination is not None:to=destination
            self.queue.append((to,envelope));self.bytes+=len(json.dumps(envelope,separators=(',',':')).encode())
        self.max_queue=max(self.max_queue,len(self.queue))
        if len(self.queue)>256:raise RuntimeError('bounded transport queue exceeded')
        return result
    def call(self,entity,command, destination=None):
        return self.accept(entity,self.processes[entity].call(dict(command,now=self.now)),destination)
    def flush(self):
        # One finite network dispatch phase; responses are queued, never drive a
        # proposal synchronously until committed. Next phases advance virtual time.
        pending=self.queue;self.queue=collections.deque()
        for to,envelope in pending:
            if to==0:to=self.leader
            if to is None:continue
            issuer=envelope['issuer']
            isolated=self.fault and (self.case=='RadioPartition' or self.case=='RadioReconnection' and self.now-self.fault_at<4_000_000_000)
            if isolated and (to==101 or issuer==101):continue
            self.call(to,{'command':'receive','envelope':envelope})
    def publish(self,entity,payloads):
        if payloads:self.call(entity,{'command':'publish','payloads':payloads})
    def prefix(self):
        if self.leader is None:return
        for train in (101,102):
            index=self.status.get(train,{}).get('commit_index',0)
            self.call(self.leader,{'command':'observe','from_index':index},train)
    def records(self):
        return self.ledger['controller']['records'] if self.ledger else [dict(phase='Unknown',grant=None) for _ in range(7)]
    def proving(self, empty=False):
        rec=self.records();epoch=self.ledger['controller']['epoch'] if self.ledger else 1
        # Switch may change only once both physical paths and retained approach
        # locks are clear. No optimiser or timetable command can unlock it.
        if self.positions[101]-10100>200000 and all(rec[r]['phase']=='Available' for r in (2,3)):
            self.points=2
        payloads={900:[],901:[],902:[]}
        for r in range(7):
            entity={0:901,1:901,2:900,3:900,4:902,5:902,6:900}[r]
            owner=None
            if not empty:
                for train,path in ((101,[0,2,4]),(102,[5,3,1])):
                    for n,resource in enumerate(path):
                        if r==resource and self.positions[train]+100>n*100000 and self.positions[train]-10100<(n+1)*100000:
                            owner={'train':train,'session':1}
            held=rec[r]['grant'];old=held['owner'] if held else None
            no_reentry=empty or old is None
            if old:
                train=old['train'];path=[0,2,4] if train==101 else [5,3,1];n=path.index(r)
                no_reentry=(self.positions[train]-10100>(n+1)*100000 or
                    (rec[r]['phase'] in ('ReleasePending','Unknown') and self.speeds[train]==0 and self.positions[train]+100<n*100000))
            self.sequence[r]+=1
            integrity=not(self.fault and self.case=='IntegrityLoss' and owner and owner['train']==101)
            closed=self.fault and self.case=='CivilClosure' and r==2
            points_ok=not(self.fault and self.case=='PointsDetectionLost' and r in (2,3))
            proof={'resource':r,'controller':900,'epoch':epoch,'sequence':self.sequence[r],'observed_ns':self.now,
                   'clear':owner is None,'clearance_safe':no_reentry,'cleared_owner':old,'occupant':owner,
                   'occupancy_integrity_proved':integrity,'points_locked_and_proved':points_ok,
                   'proved_route':self.points if r in (2,3) else None,'restriction':'Closed' if closed else 'Open'}
            if self.fault and self.case=='CivilDataStale' and r==2: continue
            payloads[entity].append({'ResourceControl':{'LocalProof':proof}})
            if rec[r]['phase'] in ('Unknown','ReleasePending'):
                if owner is None and no_reentry:payloads[entity].append({'ResourceControl':{'Clear':r}})
                elif owner==old and integrity:payloads[entity].append({'ResourceControl':{'Reconcile':r}})
            # Existing intrusion contract is independently observed, not assumed
            # clear from resource ownership or a missing sensor message.
            payloads[entity].append({'SectionIntrusion':{'section':100+r,'state':'Clear','issued_by':entity,'observed_at_ns':self.now}})
        for entity,values in payloads.items():self.publish(entity,values)
    def station(self,train):
        p=self.positions[train];v=self.speeds[train];initial=p<51000 and v==0
        prior=self.tick_outputs.get(train,{}).get('station',{})
        if self.charger_enabled[train]:self.energy[train]+=20
        if self.fault and self.case=='IncompleteCharge' and train==101:self.energy[train]=400
        connected=prior.get('phase')=='Exchange'
        stuck=self.fault and self.case in ('ChargerStuck','EmergencyDepartureConnected') and train==101
        aligned=not(self.fault and self.case=='ChargerMisaligned' and train==101)
        observation=dict(stopped_and_berthed=initial or 268000<=p<=272000 and v==0,secured=v==0,aligned=aligned,
            doors_closed_and_locked=not connected,charger_isolated=not connected and not stuck,
            connector_clear=not connected and not stuck,charger_healthy=True,charge_complete=self.energy[train]>=500,
            energy_sufficient=self.energy[train]>=500,departure_requested=self.energy[train]>=500,
            emergency_departure_requested=self.fault and self.case=='EmergencyDepartureConnected',authority_valid=False)
        platform=([0,4] if train==101 else [5,1])[int(p>=200000)]
        entity=901 if platform in (0,1) else 902
        port=self.call(entity,dict(command='station_io',platform=platform,phase=prior.get('phase','Approach'),
            charge_requested=prior.get('charging_enable',False),inputs=observation))
        if port is None:raise RuntimeError('station equipment port rejected')
        self.charger_enabled[train]=port['charging_enable']
        return port['station_observation']
    def train_tick(self,train):
        integrity=not(self.fault and self.case=='IntegrityLoss' and train==101)
        uncertainty=25000 if self.fault and self.case=='PositionUncertainty' and train==101 else 100
        station=self.station(train)
        recovery=(not self.fault or self.case in ('None','RadioReconnection','ControllerRestart','VoterRestart'))
        result=self.call(train,dict(command='tick',front_progress_mm=self.positions[train],speed_mmps=self.speeds[train],
             uncertainty_mm=uncertainty,integrity=integrity,station=station,recovery_authorised=recovery))
        if result is None:raise RuntimeError('valid train tick rejected')
        self.tick_outputs[train]=result
        self.inputs[train]=station
        self.output_sequence[train]+=1
        if self.fault and self.case=='FrozenOutput' and train==101:
            reply=self.outputs[train].call(dict(command='sample',now=self.now,feedback_healthy=True))
        else:
            reply=self.outputs[train].call(dict(command='feed',now=self.now,request=dict(sequence=self.output_sequence[train],issued_ns=self.now,brake=result['brake'],torque_mnm=result['torque_mnm']),
                stopped=self.speeds[train]==0,source_valid=True,recovery_authorised=recovery and not result['recovery_required']))
        if not reply['ok']:raise RuntimeError('output port rejected')
        output=reply['result']['output']
        brake=output['brake'];speed=self.speeds[train]
        if brake=='Emergency':speed=max(0,speed-98)
        elif isinstance(brake,dict):speed=max(0,speed-max(1,100*brake['Service']//1000))
        elif output['torque_mnm']>0:speed=min(8000,speed+100)
        self.positions[train]+=speed//10;self.speeds[train]=speed
        if output['torque_mnm']>0 and not (station['doors_closed_and_locked'] and station['charger_isolated'] and station['connector_clear'] and station['energy_sufficient']):
            raise RuntimeError('unsafe departure')
        if 268000<=self.positions[train]<=272000 and speed==0 and train not in self.arrivals:self.arrivals.append(train)
        if self.positions[train]>=100000 and train not in self.entries:self.entries.append(train)
        if self.fault and train==101 and result['recovery_required'] and speed==0 and self.case=='RadioReconnection' and self.now-self.fault_at>=4_000_000_000:self.recovered=True
    def check(self):
        a=self.positions[101];b=self.positions[102]
        if 100000<a and a-10100<200000 and 100000<b and b-10100<200000:raise RuntimeError('conflicting physical occupancy')
        records=self.records()
        if records[6]['phase']!='Blocked':raise RuntimeError('maintenance possession was released by expiry/restart')
        # Test oracle only: moving/stopping bodies must remain inside retained
        # protection. This data never supplies an onboard authority input.
        for train,path in ((101,[0,2,4]),(102,[5,3,1])):
            if self.speeds[train]>0:
                for n,r in enumerate(path):
                    if self.positions[train]+100>n*100000 and self.positions[train]-10100<(n+1)*100000:
                        grant=records[r]['grant']
                        if grant is None or grant['owner']!={'train':train,'session':1}:
                            raise RuntimeError('moving footprint outside retained protected resources')
        if any(position>=300000 for position in self.positions.values()):
            raise RuntimeError('route end exceeded')
        ga,gb=records[2]['grant'],records[3]['grant']
        if ga and gb and ga['owner']!=gb['owner']:raise RuntimeError('conflicting retained approach locks')
        if self.fault and self.speeds[101]==0 and any(r['grant'] and r['grant']['owner']['train']==101 for r in records):self.retained=True
    def restart(self,entity):
        before=self.status[entity]['commit_index'] if entity in (1001,1002,1003) else 0
        self.processes[entity].stop();self.processes[entity]=Process(entity,self.directory)
        self.pids.append(self.processes[entity].proc.pid)
        if entity in (1001,1002,1003):
            restored=self.call(entity,{'command':'tick'})
            if restored['commit_index']<before:raise RuntimeError('committed occupancy lost on restart')
            self.restored=True
    def run(self):
        # Elect with actual RPCs through process ports.
        for _ in range(16):
            self.now+=DT
            for entity in (1001,1002,1003):self.call(entity,{'command':'tick'})
            self.flush();self.flush()
        if self.leader is None:raise RuntimeError('no leader')
        model=json.loads((BASE/'railway-model.json').read_text())
        config=json.loads((BASE/'deployment.json').read_text())['configuration']
        self.publish(self.leader,[{'ResourceControl':{'Bootstrap':{'configuration':config,'model':model}}}])
        # Initial empty-railway proof and controlled admission. No train runs
        # until the bootstrap and local proving have actually committed.
        for _ in range(20):
            self.now+=DT
            for entity in (1001,1002,1003):self.call(entity,{'command':'tick'})
            if self.ledger and not self.possession_sent:
                self.publish(900,[{'ResourceControl':{'Block':6}}]);self.possession_sent=True
            if self.ledger and _%4==0:self.proving(empty=True)
            self.flush();self.flush()
        if not self.ledger:raise RuntimeError('bootstrap did not commit')
        for step in range(self.maxsteps):
            self.now+=DT
            for entity in (1001,1002,1003):self.call(entity,{'command':'tick'})
            # Station faults start during exchange; running faults after A starts.
            threshold=50000 if self.case in ('ChargerStuck','IncompleteCharge','ChargerMisaligned','EmergencyDepartureConnected') else 75000
            if not self.fault and self.case!='None' and self.positions[101]>=threshold and step>(1 if threshold==50000 else 15):
                self.fault=True;self.fault_at=self.now
                if self.case=='ControllerRestart':
                    self.restart(900);self.publish(900,[{'ResourceControl':{'Restart':2}}])
                elif self.case=='VoterRestart':self.restart(self.leader)
            if step%4==0:self.proving()
            self.prefix();self.flush();self.flush()
            for train in (101,102):self.train_tick(train)
            self.flush();self.flush();self.check()
            if step%200==0:print(f"  {self.case} step={step} front={self.positions} commits={[self.status[t]['commit_index'] for t in (101,102)]}",flush=True)
            if step%20==0:self.trace.append({'now_ns':self.now,'front_mm':[self.positions[t] for t in (101,102)],
                'speed_mmps':[self.speeds[t] for t in (101,102)],'phase':[r['phase'] for r in self.records()],
                'brake':[self.status[t]['brake'] for t in (101,102)],'commit':[self.status[t]['commit_index'] for t in (101,102)]})
            nominal=self.case in ('None','RadioReconnection','ControllerRestart','VoterRestart')
            if nominal and len(self.arrivals)==2:break
            if not nominal and self.fault and self.now-self.fault_at>8_000_000_000 and self.speeds[101]==0 and self.speeds[102]==0:break
        passed=(len(self.arrivals)==2 if nominal else self.fault and self.speeds[101]==0 and self.speeds[102]==0)
        if self.case=='VoterRestart':passed=passed and self.restored
        if self.case=='RadioPartition':passed=passed and self.retained
        # Compact actual journal storage and keep complete logical log.
        self.call(self.leader,{'command':'compact'})
        return dict(id=self.case,passed=passed,steps=step+1,junction_entry_order=self.entries,station_arrivals=sorted(self.arrivals),
            final_speed_mmps=[self.speeds[t] for t in (101,102)],final_front_mm=[self.positions[t] for t in (101,102)],
            collision_or_conflicting_occupancy_count=0,unsafe_departures=0,retained_occupancy=self.retained,
            restored_committed_prefix=self.restored,protected_possession_retained=self.records()[6]['phase']=='Blocked',process_count=10,process_ids=self.pids,transport_bytes=self.bytes,
            maximum_queue=self.max_queue,rejected_packets=self.rejections,trace=self.trace)

def campaign(cases=CASES):
    results=[]
    for case in cases:
        with tempfile.TemporaryDirectory(prefix='osr-reference-') as directory:
            installation=Installation(directory,case)
            try:result=installation.run()
            finally:installation.close()
        print(f"{case}: passed={result['passed']} arrivals={result['station_arrivals']} front={result['final_front_mm']} rejects={result['rejected_packets']}",flush=True)
        results.append(result)
    return {'schema':'osr-tacs-process-reference/1','configuration':json.loads((BASE/'deployment.json').read_text())['configuration'],
        'all_cases_passed':all(c['passed'] for c in results),'physical_readiness':False,'operational_release_ready':False,
        'topology':{'train_agents':2,'voters':3,'point_interfaces':1,'station_charging_interfaces':2,'output_guard_processes':2},
        'limitations':['Synthetic independent detector/integrity/no-reentry sensor interfaces; hardware qualification pending',
        'No physical power-cycle, certified output channel, real radio or operational acceptance',
        'Crash-fault static Raft; authenticated member committed-prefix assertions are not Byzantine quorum certificates',
        'Reference queues use virtual time; delay/coverage/capacity require measured transports',
        'Depot and rescue topology protected but service missions are not exercised'], 'cases':results}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--case',choices=CASES);a=p.parse_args()
    subprocess.run(['cargo','build','--release','--locked','-p','osr-runtime','--bins'],cwd=ROOT,check=True)
    a.output.write_text(json.dumps(campaign((a.case,) if a.case else CASES),indent=2)+'\n')
if __name__=='__main__':main()
