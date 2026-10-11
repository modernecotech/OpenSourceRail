"""Offline lifecycle/interlock contract, not an onboard safety controller."""
from __future__ import annotations
from copy import deepcopy
from .common import finite

HEALTH={'brakes','doors','active_obstacle_sensor','passive_obstacle_sensor','running_gear','hv_isolation','control_channels','communications'}


class CommissioningContract:
    def __init__(self):
        self.state='sleep';self.events=[];self.noncritical_resets=0

    def command(self,event,signals):
        required=HEALTH|{'speed_m_s','doors_locked','obstacle_clear','depot_authority','platform_authority',
            'wash_authority','service_envelope_verified','configuration_released','reset_authority','fault_cause_cleared'}
        if set(signals)!=required or any(type(signals[k]) is not bool for k in required-{'speed_m_s'}):
            raise ValueError('complete explicitly boolean interlock inputs required')
        speed=finite(signals['speed_m_s'],'observed speed',0.)
        previous=self.state;allowed=False;reason='command precondition not met'
        critical=all(signals[k] for k in HEALTH)
        if event not in {'wake','self-test','depot-exit','mainline','station-stop','door-open','door-close','depot-entry','wash','sleep','reset-noncritical','clear-lockout','tick'}:
            raise ValueError('unknown commissioning contract command')
        if not critical or not signals['obstacle_clear']:
            self.state='locked-out';reason='critical fault or obstacle requires stop/inspection; no automatic reset'
        elif speed>0 and (not signals['doors_locked'] or self.state not in ('depot-moving','mainline')):
            self.state='locked-out';reason='observed movement conflicts with door/state interlock'
        elif self.state in ('depot-moving','mainline') and (not signals['configuration_released'] or not signals['service_envelope_verified']):
            self.state='locked-out';reason='movement qualification/authority withdrawn'
        elif event=='wake' and self.state=='sleep' and speed==0:
            self.state='self-test';allowed=True
        elif event=='self-test' and self.state=='self-test' and speed==0:
            self.state='standby';allowed=True
        elif event=='depot-exit' and self.state=='standby' and signals['depot_authority'] and signals['doors_locked'] and signals['configuration_released'] and signals['service_envelope_verified']:
            self.state='depot-moving';allowed=True
        elif event=='mainline' and self.state=='depot-moving' and signals['doors_locked'] and signals['configuration_released'] and signals['service_envelope_verified']:
            self.state='mainline';allowed=True
        elif event=='station-stop' and self.state=='mainline' and speed==0:
            self.state='platform';allowed=True
        elif event=='door-open' and self.state=='platform' and speed==0 and signals['platform_authority']:
            self.state='doors-open';allowed=True
        elif event=='door-close' and self.state=='doors-open' and speed==0 and signals['doors_locked']:
            self.state='platform';allowed=True
        elif event=='mainline' and self.state=='platform' and signals['doors_locked'] and signals['configuration_released'] and signals['service_envelope_verified']:
            self.state='mainline';allowed=True
        elif event=='depot-entry' and self.state in ('mainline','platform') and signals['depot_authority'] and signals['doors_locked']:
            self.state='depot-moving';allowed=True
        elif event=='wash' and self.state=='depot-moving' and speed==0 and signals['wash_authority']:
            self.state='washing';allowed=True
        elif event=='sleep' and self.state in ('standby','washing') and speed==0:
            self.state='sleep';allowed=True
        elif event=='reset-noncritical' and self.state=='standby' and speed==0 and signals['reset_authority'] and self.noncritical_resets<1:
            self.noncritical_resets+=1;allowed=True;reason='one bounded auxiliary reset; critical functions excluded'
        elif event=='clear-lockout' and self.state=='locked-out' and speed==0 and signals['reset_authority'] and signals['fault_cause_cleared']:
            self.state='self-test';allowed=True;reason='authorised clear requires a fresh self-test'
        movement=self.state in ('depot-moving','mainline') and critical and signals['doors_locked'] and signals['obstacle_clear'] and signals['configuration_released'] and signals['service_envelope_verified']
        row=dict(command=event,previous_state=previous,state=self.state,command_allowed=allowed,movement_permitted=movement,
            reason='preconditions satisfied' if allowed and reason=='command precondition not met' else reason)
        self.events.append(deepcopy(row));return row


def reference_signals():
    return {**{k:True for k in HEALTH},'speed_m_s':0.,'doors_locked':True,'obstacle_clear':True,
        'depot_authority':True,'platform_authority':True,'wash_authority':True,
        'service_envelope_verified':True,'configuration_released':True,'reset_authority':True,'fault_cause_cleared':True}


def fault_campaign():
    records=[]
    for fault in sorted(HEALTH):
        machine=CommissioningContract();signals=reference_signals()
        for event in ('wake','self-test','depot-exit','mainline'):machine.command(event,signals)
        signals[fault]=False;response=machine.command('tick',signals)
        records.append(dict(case='fault-'+fault,passed=response['state']=='locked-out' and not response['movement_permitted'],response=response))
    for key in ('doors_locked','obstacle_clear','service_envelope_verified','configuration_released'):
        machine=CommissioningContract();signals=reference_signals();machine.command('wake',signals);machine.command('self-test',signals)
        signals[key]=False;response=machine.command('depot-exit',signals)
        records.append(dict(case='inhibit-'+key,passed=not response['movement_permitted'],response=response))
    machine=CommissioningContract();signals=reference_signals();cycle=[]
    for event in ('wake','self-test','depot-exit','mainline','station-stop','door-open','door-close','depot-entry','wash','sleep'):
        cycle.append(machine.command(event,signals))
    records.append(dict(case='conditional-lifecycle',passed=all(r['command_allowed'] for r in cycle),events=cycle))
    return dict(schema='osr-offline-commissioning-campaign/1',cases=records,contract_checks_passed=all(r['passed'] for r in records),
        actual_train_configuration_released=False,service_envelope_qualified=False,goa4_qualified=False,physical_validation=False,
        limits=['hypothetical released interlock inputs in test fixtures; current train gates remain open',
            'no actual ATP/ATO/TCMS, network redundancy timing, sensor coverage or independent safety assessment'])
