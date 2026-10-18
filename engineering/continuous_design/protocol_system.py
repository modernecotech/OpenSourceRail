"""Offline receiver-to-precharge interface and end-to-end fault propagation.

This is an explicit experimental interface, not an adopted train protocol.
It links actual receipt-bound generated executables; no hardware I/O occurs.
"""
from copy import deepcopy
import runpy
from pathlib import Path

from .tasks import FACTS
from . import receiver_reference

INTERFACE_ID='osr-precharge-link/1'
REMOTE=('train_stopped','hvil_closed','insulation_ok','main_feedback_open')
CONTRACT=dict(id=INTERFACE_ID,wire='11 bytes: little-endian u16 sequence, u32 observed ms, u8 flags, CRC32',
    remote_guard_bits={name:i for i,name in enumerate(REMOTE)},
    valid_flags=15,maximum_age_ms=100,sequence='modulo 65536; forward distance 1..32767',
    local_guards='All twelve named facts remain independent local vetoes; remote flags cannot override them',
    failure_action='Invalid receiver state or guard failure inhibits modeled closure and latches until explicit standstill reset',
    voltage_ramp='Low voltage alone inhibits closure without latching a fault',
    status='proposed offline research interface; no safety integrity, timing or physical qualification')


class Link:
    def __init__(self,receiver,policy):
        self.receiver,self.policy=receiver,policy
        self.locked=False

    def reset(self,stopped):
        accepted=self.receiver.reset(stopped)
        if accepted and stopped is True:
            self.locked=False
        return False  # reset never requests contactor closure

    def receive(self,packet,receipt,local):
        accepted=self.receiver.receive(packet,receipt)
        facts=dict(local)
        for bit,name in enumerate(REMOTE):
            facts[name]=facts[name] and accepted and bool(packet[6] & (1<<bit))
        for name in ('data_valid','age_valid','sequence_valid','clocks_valid'):
            facts[name]=facts[name] and accepted
        if not all(value for name,value in facts.items() if name!='voltage_ready'):
            self.locked=True
        return bool(accepted and not self.locked and self.policy(**facts))


def scenarios():
    healthy={name:True for name in FACTS}
    frame=receiver_reference.frame
    def event(data=None,receipt=1000,**local):
        return ('frame',frame() if data is None else data,receipt,dict(healthy,**local))
    good=frame();corrupt=bytearray(good);corrupt[0]^=1
    yield 'healthy', [event()], [True]
    yield 'voltage-ramp', [event(voltage_ready=False),event(frame(2,1001),1001)], [False,True]
    yield 'crc-fault-persists', [event(bytes(corrupt)),event(frame(2,1001),1001)], [False,False]
    yield 'reset-moving-denied', [event(bytes(corrupt)),('reset',False),event(frame(2,1001),1001)], [False,False,False]
    yield 'reset-stopped-recovers', [event(bytes(corrupt)),('reset',True),event(frame(2,1001),1001)], [False,False,True]
    yield 'sequence-wrap-valid', [event(frame(65535,1000)),event(frame(0,1001),1001)], [True,True]
    yield 'duplicate-packet', [event(),event()], [True,False]
    yield 'age-expired', [event(receipt=1101)], [False]
    yield 'future-timestamp', [event(receipt=999)], [False]
    for bit,name in enumerate(REMOTE):
        yield 'remote-'+name+'-veto',[event(frame(flags=15^(1<<bit)))],[False]
    for name in FACTS:
        yield 'local-'+name+'-veto',[event(**{name:False})],[False]


def replay(receiver_class,policy,*,link_class=Link):
    rows=[]
    for name,events,expected in scenarios():
        link=link_class(receiver_class(),policy)
        actual=[]
        for event in events:
            actual.append(link.reset(event[1]) if event[0]=='reset' else link.receive(event[1],event[2],event[3]))
        rows.append(dict(id=name,expected_permissions=expected,actual_permissions=actual,passed=actual==expected))
    # Compose with independent receiver state transitions, including long replay
    # and event interleavings. The reference never calls the generated policy.
    healthy={name:True for name in FACTS}
    for name,events in receiver_reference.cases():
        link=link_class(receiver_class(),policy);oracle=receiver_reference.Oracle();locked=False
        expected=[];actual=[]
        for event in events:
            if event[0]=='reset':
                reset=oracle.reset(event[1])
                if reset and event[1] is True:locked=False
                want=False;got=link.reset(event[1])
            else:
                valid=oracle.receive(event[1],event[2])
                if not valid:locked=True
                want=valid and not locked;got=link.receive(event[1],event[2],healthy)
            expected.append(want);actual.append(got)
        rows.append(dict(id='composed-'+name,expected_permissions=expected,actual_permissions=actual,passed=actual==expected))
    return rows


def evaluate(children):
    receiver=children['software-receiver'];logic=children['software-logic']
    receiver_class=runpy.run_path(str(Path(receiver['folder'])/'output/generated-receiver.py'))['Receiver']
    policy=runpy.run_path(str(Path(logic['folder'])/'output/generated-controller.py'))['closure_request']
    rows=replay(receiver_class,policy)
    return dict(interface=deepcopy(CONTRACT),study_pass=all(row['passed'] for row in rows),
        executable_children=[dict(key=child['key'],kind=kind) for kind,child in children.items() if kind.startswith('software-')],
        checks=dict(receiver_faults_inhibit_modeled_closure=all(r['passed'] for r in rows),
            explicit_local_and_remote_interface=True),cases=len(rows),
        counterexamples=[row for row in rows if not row['passed']][:20],
        explicit_scenarios=rows[:sum(1 for _ in scenarios())],
        scope=__doc__.strip(),physical_release=False)
