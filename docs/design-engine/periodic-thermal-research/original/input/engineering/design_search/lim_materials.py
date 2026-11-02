"""Bounded reversible nonlinear reference laws, distinct from supplier evidence."""
from pathlib import Path
from bisect import bisect_right
from math import isfinite
import json
from engineering.station_rail.common import identity
DATA='engineering/design_search/data/getdp-steel-generic.json'


def material():
    p=Path(__file__).resolve().parents[2]/DATA;v=json.loads(p.read_bytes());validate(v)
    v['material_id']=identity(v);return v


def validate(curve):
    b=curve['B_T'];h=curve['H_A_m']
    if len(b)!=len(h) or len(b)<10 or b[0]!=0 or h[0]!=0:raise ValueError('Full tabulated origin-based relation required; sparse checkpoints are not a complete law')
    if any(not isfinite(x) or x<0 for x in b+h) or any(y<=x for row in (b,h) for x,y in zip(row,row[1:])):raise ValueError('Strictly increasing finite B and H required')


def _segment(curve,H):
    validate(curve)
    if not isfinite(H) or not 0<=H<=curve['H_A_m'][-1]:raise ValueError('Material field outside table; extrapolation refused')
    return min(len(curve['H_A_m'])-2,max(0,bisect_right(curve['H_A_m'],H)-1))


def B(curve,H):
    i=_segment(curve,H);h=curve['H_A_m'];b=curve['B_T'];return b[i]+(H-h[i])*(b[i+1]-b[i])/(h[i+1]-h[i])


def differential_mu(curve,H):
    i=_segment(curve,H);return (curve['B_T'][i+1]-curve['B_T'][i])/(curve['H_A_m'][i+1]-curve['H_A_m'][i])


def coenergy_density(curve,H):
    i=_segment(curve,H);h=curve['H_A_m'];b=curve['B_T'];total=sum(.5*(b[j]+b[j+1])*(h[j+1]-h[j]) for j in range(i))
    return total+b[i]*(H-h[i])+.5*differential_mu(curve,H)*(H-h[i])**2


def field_for_B(curve,target):
    validate(curve)
    if not isfinite(target) or not 0<=target<=curve['B_T'][-1]:raise ValueError('Flux density outside table; extrapolation refused')
    i=min(len(curve['B_T'])-2,max(0,bisect_right(curve['B_T'],target)-1));b=curve['B_T'];h=curve['H_A_m']
    return h[i]+(target-b[i])*(h[i+1]-h[i])/(b[i+1]-b[i])


def circuit(curve,NI,gap_m,core_m=.1,area_m2=.001):
    if min(NI,gap_m,core_m,area_m2)<=0:raise ValueError('Positive current MMF and dimensions required')
    mu0=4e-7*3.141592653589793
    if NI>curve['H_A_m'][-1]*core_m+curve['B_T'][-1]/mu0*gap_m:raise ValueError('Required current MMF outside tabulated law; no extrapolation')
    lo=0.;hi=curve['B_T'][-1]
    for _ in range(90):
        mid=(lo+hi)/2
        if core_m*field_for_B(curve,mid)+gap_m*mid/mu0>NI:hi=mid
        else:lo=mid
    flux=(lo+hi)/2;H=field_for_B(curve,flux)
    coenergy=area_m2*(core_m*coenergy_density(curve,H)+gap_m*flux*flux/(2*mu0))
    return dict(B_T=flux,H_core_A_m=H,coenergy_J=coenergy,attraction_N=area_m2*flux*flux/(2*mu0),source_flux_work_J=NI*flux*area_m2)


def supplier_readiness():
    return dict(selected_rail_steel_complete_BH_law=None,supplier_steel_gate='held',
        primary_supplier_graph='https://cms.sij.si/storage/336/SIWATT-M330-50A.pdf',
        primary_supplier_simulation_catalogue='https://www.voestalpine.com/isovac/Downloads/Datenblaetter',
        catalogue_access='Simulation-file request asks name/email/company; no form or message submitted',
        gap='Supplier full numerical law, temperature/direction/stress/hysteresis/loss and delivered-lot correlation remain unavailable',
        reference_curve_role='GetDP generic numerical benchmark only',physical_accepted=False)
