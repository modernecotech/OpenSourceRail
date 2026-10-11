"""Tabulated SOC/temperature OCV and resistance with conservative domain checks.

A constant current over each step uses the exact piecewise-linear OCV integral,
so chemical, terminal and Joule energies close independently of SOC step size.
Tables describe a configuration, not a chemistry-wide calibrated model.
"""
import math
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import brentq
from engineering.industrialisation.common import finite, fingerprint


class Battery:
    def __init__(self, pack, maps, *, soc=.8, temperature_c=25., soh=1.):
        self.pack=pack;self.maps=maps;self.soc=finite(soc,'SOC',0.);self.temperature=finite(temperature_c,'temperature');self.soh=finite(soh,'SOH',.5)
        self.reference_soh=finite(maps['capacity_reference_soh'],'capacity reference SOH',.5)
        if self.reference_soh>1:raise ValueError('capacity reference SOH outside domain')
        if self.soh>1 or not pack['soc_min']<=soc<=pack['soc_max']:raise ValueError('battery initial state outside domain')
        self.soc_grid=np.asarray(maps['soc'],float);self.temp_grid=np.asarray(maps['temperature_c'],float)
        for grid in (self.soc_grid,self.temp_grid):
            if len(grid)<2 or not np.isfinite(grid).all() or np.any(np.diff(grid)<=0):raise ValueError('strictly increasing finite battery map axes required')
        if self.soc_grid[0]>pack['soc_min'] or self.soc_grid[-1]<pack['soc_max']:raise ValueError('OCV map does not cover pack SOC bounds')
        self.functions={}
        for key in ('ocv_v','resistance_ohm'):
            table=np.asarray(maps[key],float)
            if table.shape!=(len(self.temp_grid),len(self.soc_grid)) or not np.isfinite(table).all() or np.min(table)<=0:raise ValueError('positive finite battery map required: '+key)
            self.functions[key]=RegularGridInterpolator((self.temp_grid,self.soc_grid),table,bounds_error=True)
        self.value('ocv_v',soc)

    def value(self,key,soc):
        return float(self.functions[key]([[self.temperature,soc]])[0])/(self.soh if key=='resistance_ohm' else 1.)

    def integral(self,start,end):
        if start==end:return self.value('ocv_v',start)
        grid=sorted([start,end,*[float(s) for s in self.soc_grid if min(start,end)<s<max(start,end)]])
        voltage=np.asarray([self.value('ocv_v',s) for s in grid])
        return float(np.trapezoid(voltage,grid))/abs(start-end)

    def step(self,terminal_power_w,dt_s,*,cooling_w=0.,ambient_c=25.,current_limit_a=None):
        P=finite(terminal_power_w,'terminal power');dt=finite(dt_s,'battery step',1e-9)
        if dt>30:raise ValueError('battery coupling step exceeds 30 s research bound')
        removed=finite(cooling_w,'cooling',0.);ambient=finite(ambient_c,'ambient');s0=self.soc;T0=self.temperature
        Q=3600*self.pack['capacity_ah']*self.soh/self.reference_soh
        dis=self.pack['discharge_current_limit_a'];chg=self.pack['charge_current_limit_a']
        if current_limit_a is not None:
            dis=min(dis,finite(current_limit_a,'current cap',0.));chg=min(chg,current_limit_a)
        low=max(-chg,(s0-self.pack['soc_max'])*Q/dt);high=min(dis,(s0-self.pack['soc_min'])*Q/dt)
        def values(I):
            s1=s0-I*dt/Q;v=self.integral(s0,s1);r=self.value('resistance_ohm',(s0+s1)/2)
            return v,r,v*I-r*I*I
        # Use only the stable low-current branch; voltage-collapse cases reject.
        high=min(high,self.value('ocv_v',s0)/(2*self.value('resistance_ohm',s0)))
        if P<values(low)[2]-1e-8 or P>values(high)[2]+1e-8:raise ValueError('requested power exceeds current/SOC/stable-voltage battery domain')
        I=0. if P==0 else brentq(lambda I:values(I)[2]-P,low,high,xtol=1e-11)
        v,r,_=values(I);s1=s0-I*dt/Q;heat=I*I*r*dt;chemical=v*I*dt
        C=self.pack['thermal_capacity_j_k'];H=self.pack['cooling_conductance_w_k'];eq=ambient+(I*I*r-removed)/H
        T1=eq+(T0-eq)*math.exp(-H*dt/C);passive=heat-removed*dt-C*(T1-T0)
        if not self.temp_grid[0]<=T1<=self.temp_grid[-1]:raise ValueError('battery temperature exits retained map domain')
        self.soc=s1;self.temperature=T1
        return dict(current_a=I,terminal_voltage_v=v-I*r,soc=s1,temperature_c=T1,terminal_energy_j=P*dt,
            chemical_energy_j=chemical,joule_heat_j=heat,active_heat_removed_j=removed*dt,passive_heat_removed_j=passive,
            electrical_residual_j=chemical-P*dt-heat,thermal_residual_j=heat-removed*dt-passive-C*(T1-T0),
            maps_sha256=fingerprint(self.maps),maps_basis=self.maps['basis'],calibrated=False,physical_validation=False)


def power_ledger(entries):
    """Every physical load appears once; aggregation is a view, never another load."""
    ids=set();total=0.
    for row in entries:
        if not isinstance(row['id'],str) or not row['id'] or row['id'] in ids:raise ValueError('duplicate or missing physical power identity')
        ids.add(row['id']);total+=finite(row['power_w'],'power ledger entry')
    return dict(entries=entries,total_terminal_power_w=total)
