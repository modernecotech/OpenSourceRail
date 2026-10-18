"""Generated bounded packet receiver; offline communications research only.

Wire contract: u16 sequence, u32 observed milliseconds, u8 guard flags, CRC32
over the first seven little-endian bytes. Receipt age must be 0..100 ms.
Sequence advances modulo 65536 by 1..32767. Invalid input latches FAULT.
Only an explicit reset while stopped returns to BOOT. No live hardware I/O.
"""
import importlib.util
import itertools
import math
from pathlib import Path
import statistics
import sys
import time

DOMAINS=dict(decoder=["struct","bytes"],history_capacity=[1,4,8],
    sequence_policy=["modular","linear"],reset_policy=["standstill","unconditional"])


def validate(parameters):
    if set(parameters)!=set(DOMAINS) or any(type(v) is not type(DOMAINS[k][0]) or v not in DOMAINS[k] for k,v in parameters.items()):
        raise ValueError("receiver parameters outside the controlled implementation domain")


def source(parameters):
    validate(parameters)
    decoder=("struct.unpack('<HIB', packet[:7])" if parameters["decoder"]=="struct" else
        "(int.from_bytes(packet[:2], 'little'), int.from_bytes(packet[2:6], 'little'), packet[6])")
    sequence=("0 < ((sequence-self.sequence) % 65536) < 32768" if parameters["sequence_policy"]=="modular" else "sequence > self.sequence")
    reset=("stopped is True" if parameters["reset_policy"]=="standstill" else "True")
    return '''# Generated offline receiver; physical/manufacturing release remains false.
import struct
import zlib
class Receiver:
    CAPACITY = '''+str(parameters["history_capacity"])+'''
    def __init__(self):
        self.state = 'BOOT'
        self.sequence = self.observed = self.receipt = None
        self.history = []
    def reset(self, stopped):
        if not ('''+reset+'''):
            return False
        self.__init__()
        return True
    def receive(self, packet, receipt):
        if self.state == 'FAULT':
            return False
        valid = type(packet) is bytes and len(packet) == 11 and type(receipt) is int and 0 <= receipt <= 4294967295
        if valid:
            sequence, observed, flags = '''+decoder+'''
            valid = zlib.crc32(packet[:7]) == int.from_bytes(packet[7:], 'little')
            valid = valid and flags == 15 and 0 <= receipt-observed <= 100
            valid = valid and (self.sequence is None or ('''+sequence+'''))
            valid = valid and (self.observed is None or observed >= self.observed)
            valid = valid and (self.receipt is None or receipt >= self.receipt)
        if not valid:
            self.state = 'FAULT'
            return False
        self.state = 'READY'
        self.sequence, self.observed, self.receipt = sequence, observed, receipt
        self.history.append(sequence)
        del self.history[:-self.CAPACITY]
        return True
'''


def packet(sequence=1,observed=1000,flags=15):
    import zlib
    body=sequence.to_bytes(2,"little")+observed.to_bytes(4,"little")+bytes([flags])
    return body+zlib.crc32(body).to_bytes(4,"little")


def evaluate(parameters,output):
    from engineering.continuous_design.receiver_reference import Oracle, cases
    from engineering.twin_workflow import core
    validate(parameters);output=Path(output)
    path=output/"generated-receiver.py";path.write_text(source(parameters))
    spec=importlib.util.spec_from_file_location("generated_receiver",path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    failures=[];case_count=0;max_history=0
    for case_id,events in cases():
        actual,expected=module.Receiver(),Oracle();case_count+=1
        for event in events:
            if event[0]=="reset":
                got=actual.reset(event[1]);want=expected.reset(event[1])
            else:
                got=actual.receive(event[1],event[2]);want=expected.receive(event[1],event[2])
            max_history=max(max_history,len(actual.history))
            if (got,actual.state,actual.sequence,actual.observed,actual.receipt)!=(want,expected.state,expected.sequence,expected.observed,expected.receipt):
                if len(failures)<20:failures.append(dict(case=case_id,event_type=event[0],actual=got,expected=want,actual_state=actual.state,expected_state=expected.state))
            if len(actual.history)>parameters["history_capacity"]:
                raise ValueError("receiver exceeded its declared retained-state capacity")
    timings=[];receiver=module.Receiver()
    for index in range(1000):
        data=packet(index,index)
        started=time.perf_counter_ns();receiver.receive(data,index);timings.append(time.perf_counter_ns()-started)
    state_bytes=sys.getsizeof(receiver.__dict__)+sum(sys.getsizeof(v) for v in receiver.__dict__.values())+sum(sys.getsizeof(v) for v in receiver.history)
    checks=dict(independent_temporal_reference=not failures,bounded_history=max_history<=parameters["history_capacity"],
        bounded_packet_length=True,executable_generated=True)
    return dict(study_pass=all(checks.values()),checks=checks,failed_checks=[k for k,v in checks.items() if not v],
        metrics=dict(reference_sequences=case_count,history_capacity=parameters["history_capacity"],maximum_retained_history=max_history,
            observed_state_bytes=state_bytes,median_receive_ns=statistics.median(timings),p99_receive_ns=sorted(timings)[989],
            maximum_packet_bytes=11),counterexamples=failures,
        verification=dict(evaluated_level="executable_verification",levels=dict(executable_verification=dict(state="passed" if not failures else "failed",checks=list(checks))),
            independent_physics_rerun=False,scope=__doc__.strip()),
        scope="Generated offline receiver state machine against an independent transition oracle; wall-clock samples are host observations, not real-time guarantees",
        open_evidence=["full train protocol specification","target hardware timing","threaded concurrency beyond enumerated event interleavings","SIL/HIL","physical fault recovery"],**core.FLAGS)


def seeds():
    from engineering.continuous_design.tasks import task
    values=[dict(decoder=d,history_capacity=c,sequence_policy="modular",reset_policy="standstill") for d in DOMAINS["decoder"] for c in DOMAINS["history_capacity"]]
    values.extend([dict(values[0],sequence_policy="linear"),dict(values[0],reset_policy="unconditional")])
    return [task("software-receiver",p,"Bounded generated receiver implementation with independent temporal reference") for p in values]
