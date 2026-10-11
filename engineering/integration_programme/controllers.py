"""Actual native Rust controller/plant loop with retained request and response."""
from copy import deepcopy
import json
import subprocess
import selectors
from pathlib import Path
from .battery import Battery,power_ledger
from engineering.industrialisation.common import fingerprint


def run(pack,maps,request,binary,*,ticks=60,fault_tick=40):
    if not 2<=ticks<=10000 or not 1<=fault_tick<ticks:raise ValueError('controller experiment budget invalid')
    plant=Battery(pack,maps,temperature_c=35.);rows=[];current=0.;cabin=30.;voltage=plant.value('ocv_v',plant.soc)
    process=subprocess.Popen([str(Path(binary).resolve())],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    selector=selectors.DefaultSelector();selector.register(process.stdout,selectors.EVENT_READ)
    try:
        for tick in range(ticks):
            r=deepcopy(request);r['now_ns']=(tick+1)*1_000_000_000;r['dt_ns']=1_000_000_000
            r['plant_discharge_current_ma']=round(current*1000);r['pack_voltage_mv']=round(voltage*1000)
            r['cell_voltages_mv']=[round(voltage*1000/r['bms_params']['cell_count'])]*r['bms_params']['cell_count']
            r['cell_temps_dc']=[round(plant.temperature*10)]*r['bms_params']['cell_count']
            r['thermal_inputs'].update(cabin_temp_dc=round(cabin*10),battery_max_cell_temp_dc=round(plant.temperature*10),battery_pump_available=tick<fault_tick)
            if tick>=fault_tick:r['brake_inputs']['fire_emergency']=True
            if ticks//3<=tick<ticks//2:
                r['brake_inputs']['atp_command']={'Service':500};r['traction_inputs']['torque_setpoint_mnm']=-1_000_000
            process.stdin.write(json.dumps(r)+'\n');process.stdin.flush()
            if not selector.select(timeout=10):raise TimeoutError('native controller did not respond within the experiment timeout')
            line=process.stdout.readline()
            if not line:raise RuntimeError('native controller stopped before responding')
            output=json.loads(line)
            if 'error' in output:raise ValueError(output['error'])
            closed=output['bms']['contactor']=='Closed';thermal=output['thermal'];traction=output['traction'];brake=output['brake']
            # Research drive map: no independent electrical actuator command.
            torque=traction['commanded_torque_mnm']/1000;omega=15./.38
            mechanical=torque*omega;motor=mechanical/.95 if mechanical>=0 else mechanical*.95
            cabin_cooling=32000*thermal['cabin_compressor_ppt']/1000 if closed else 0.
            battery_cooling=4000*thermal['battery_chiller_ppt']/1000 if closed else 0.
            loads=[dict(id='traction-inverter',power_w=motor if closed else 0.),dict(id='shared-refrigerant-compressor',power_w=(cabin_cooling+battery_cooling)/2.5),dict(id='fans-pump-control',power_w=500. if closed else 0.)]
            ledger=power_ledger(loads);P=ledger['total_terminal_power_w'];limit=(output['bms']['discharge_limit_ma'] if P>=0 else output['bms']['charge_limit_ma'])/1000
            state=plant.step(P,1.,cooling_w=battery_cooling,ambient_c=45.,current_limit_a=limit)
            current=state['current_a'];voltage=state['terminal_voltage_v'];cabin+=(9500+500*(45-cabin)-cabin_cooling)/1.2e6
            rows.append(dict(tick=tick,input=r,native_output=output,plant=state,power=ledger,cabin_temperature_c=cabin,
                mechanical_power_w=mechanical if closed else 0.,friction_brake_heat_w=request['regen_full_effort_torque_mnm']/1000*omega*brake['friction_effort_ppt']/1000,
                controller_current_estimate_error_a=traction['estimated_current_ma']/1000-current))
        return dict(schema='osr-native-controller-plant-execution/1',pack_sha256=fingerprint(pack),maps_sha256=fingerprint(maps),history=rows,
            fault_isolated=all(r['native_output']['bms']['contactor']!='Closed' and r['power']['total_terminal_power_w']==0 for r in rows[fault_tick:]),
            maximum_electrical_energy_residual_j=max(abs(r['plant']['electrical_residual_j']) for r in rows),
            physical_validation=False,hardware_in_loop=False,commissioned=False,
            open_domains=['supplier OCV/temperature/SOH and drive maps','mechanical braking feedback to full spatial solver','traction supervisor motor-current/pack-current calibration','target timing and wiring bench','cell hot spots and flow/refrigerant model'])
    finally:
        selector.close();process.stdin.close()
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
        process.stdout.close();process.stderr.close()
