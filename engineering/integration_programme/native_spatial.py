"""Six independent native Rust controllers exchange states with spatial dynamics.

The reference trajectory and original motor/thermal maps are research inputs.
Applied wheel torques enter the same monolithic equations. Converged wheel speed
returns mechanical power to the battery/thermal plant; states return next tick.
No target I/O, physical calibration or production authority is established.
"""
from copy import deepcopy
import hashlib,json,math,selectors,subprocess
from pathlib import Path
from .battery import Battery,power_ledger
from engineering.industrialisation.common import fingerprint


class NativeSpatialLoop:
    def __init__(self,model,pack,maps,request,binary,*,fault_after_s=.05,drive_torque_nm=100.):
        if not math.isfinite(fault_after_s) or fault_after_s<=0 or not math.isfinite(drive_torque_nm) or drive_torque_nm<0:
            raise ValueError('finite positive fault time and nonnegative drive torque required')
        ids=[car['id'] for car in model['family_definition']['cars']]
        if not ids or len(set(ids))!=len(ids):raise ValueError('unique configured car identities required')
        self.cfg=fingerprint(model);self.request=deepcopy(request);self.pack=deepcopy(pack);self.maps=deepcopy(maps);self.fault_after=fault_after_s;self.drive_torque=drive_torque_nm
        self.binary=Path(binary).resolve();self.binary_sha256=hashlib.sha256(self.binary.read_bytes()).hexdigest();self.controllers={};self.history=[]
        try:
            for body in ids:
                plant=Battery(self.pack,self.maps,temperature_c=35.)
                selector=selectors.DefaultSelector()
                try:
                    proc=subprocess.Popen([str(self.binary)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,bufsize=1)
                except BaseException:
                    selector.close();raise
                self.controllers[body]=dict(proc=proc,selector=selector,plant=plant,current_a=0.,voltage_v=pack['nominal_voltage_v'],cabin_c=30.,pending=None)
                selector.register(proc.stdout,selectors.EVENT_READ)
        except BaseException:
            self.close();raise

    def prepare(self,context):
        torques={};responses={}
        for body,c in self.controllers.items():
            wheels=[w for w in context['wheelsets'] if w['id'].startswith(body+'/')]
            if not wheels:raise ValueError('native spatial loop requires all configured car wheelsets')
            powered=[w for w in wheels if w['powered']];plant=c['plant'];r=deepcopy(self.request);r['configuration_sha256']=self.cfg
            r['now_ns']=round(context['time_s']*1e9);r['dt_ns']=round(context['dt_s']*1e9);r['plant_discharge_current_ma']=round(c['current_a']*1000);r['pack_voltage_mv']=round(c['voltage_v']*1000)
            r['cell_voltages_mv']=[round(c['voltage_v']*1000/r['bms_params']['cell_count'])]*r['bms_params']['cell_count'];r['cell_temps_dc']=[round(plant.temperature*10)]*r['bms_params']['cell_count']
            fault=context['time_s']>=self.fault_after
            r['thermal_inputs'].update(cabin_temp_dc=round(c['cabin_c']*10),battery_max_cell_temp_dc=round(plant.temperature*10),battery_pump_available=not fault)
            r['brake_inputs'].update(fire_emergency=fault,atp_command='Release',measured_speed_mmps=round(context['reference_speed_m_s']*1000),wheel_speed_mmps=round(sum(w['rolling_speed_m_s'] for w in wheels)/len(wheels)*1000))
            r['traction_inputs'].update(torque_setpoint_mnm=round(self.drive_torque*1000) if powered else 0,reference_speed_mmps=r['brake_inputs']['measured_speed_mmps'],wheel_speed_mmps=r['brake_inputs']['wheel_speed_mmps'])
            proc=c['proc'];proc.stdin.write(json.dumps(r)+'\n');proc.stdin.flush()
            if not c['selector'].select(timeout=10):raise TimeoutError('native spatial controller reply timeout')
            line=proc.stdout.readline()
            if not line:raise RuntimeError('native spatial controller stopped')
            out=json.loads(line)
            if out.get('error'):raise ValueError(out['error'])
            drive=out['traction']['commanded_torque_mnm']/1000
            friction=requested_friction=r['regen_full_effort_torque_mnm']/1000*out['brake']['friction_effort_ppt']/1000
            per_wheel={w['id']:(drive/len(powered) if w['powered'] else 0.)-friction/len(wheels) for w in wheels}
            # Track drive and friction separately for electrical/thermal work.
            c['pending']=dict(input=r,native_output=out,drive_nm={w['id']:drive/len(powered) if w['powered'] else 0. for w in wheels},friction_nm={w['id']:-requested_friction/len(wheels) for w in wheels},previous_omega={w['id']:w['angular_velocity_rad_s'] for w in wheels})
            torques.update(per_wheel);responses[body]=out
        return dict(wheel_torque_nm=torques,evidence=dict(producer='actual native Rust twin_controller_bridge',binary_sha256=self.binary_sha256,configuration_sha256=self.cfg,controller_outputs=responses,physical_validation=False))

    def observe(self,sample):
        omega={w['wheelset']:w['angular_velocity_rad_s'] for w in sample['wheelset_observations']};rows=[]
        for body,c in self.controllers.items():
            pending=c['pending'];out=pending['native_output'];r=pending['input'];dt=r['dt_ns']/1e9
            midpoint={w:(pending['previous_omega'][w]+omega[w])/2 for w in pending['drive_nm']}
            mechanical=sum(T*midpoint[w] for w,T in pending['drive_nm'].items());friction_heat=-sum(T*midpoint[w] for w,T in pending['friction_nm'].items())
            closed=out['bms']['contactor']=='Closed';thermal=out['thermal'];cabin_q=32000*thermal['cabin_compressor_ppt']/1000 if closed else 0.;pack_q=4000*thermal['battery_chiller_ppt']/1000 if closed else 0.
            motor=mechanical/.95 if mechanical>=0 else mechanical*.95
            ledger=power_ledger([dict(id=body+'/traction-inverter',power_w=motor),dict(id=body+'/shared-refrigerant-compressor',power_w=(cabin_q+pack_q)/2.5),dict(id=body+'/fans-pump-control',power_w=500. if closed else 0.)])
            P=ledger['total_terminal_power_w'];limit=(out['bms']['discharge_limit_ma'] if P>=0 else out['bms']['charge_limit_ma'])/1000
            state=c['plant'].step(P,dt,cooling_w=pack_q,ambient_c=45.,current_limit_a=limit);c.update(current_a=state['current_a'],voltage_v=state['terminal_voltage_v'])
            c['cabin_c']+=(9500+500*(45-c['cabin_c'])-cabin_q)*dt/1.2e6
            rows.append(dict(body=body,native_input=r,native_output=out,battery=state,power_ledger=ledger,mechanical_drive_power_w=mechanical,friction_brake_heat_w=friction_heat,cabin_temperature_c=c['cabin_c']))
        self.history.append(dict(time_s=sample['time_s'],cars=rows,source='converged monolithic wheel speeds; one-step explicit controller/plant exchange'))

    def close(self):
        for c in self.controllers.values():
            c['selector'].close();p=c['proc']
            if not p.stdin.closed:p.stdin.close()
            try:p.wait(timeout=5)
            except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
            p.stdout.close()
