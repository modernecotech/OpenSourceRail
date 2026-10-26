"""Native conductive-fin diffusion benchmark and conditional travelling-field bounds.

This is a manufactured 2D secondary coupon, NOT a station motor force map.
An imposed travelling field cannot establish the current a real primary needs.
"""
from __future__ import annotations
import cmath
from math import pi,sqrt
from pathlib import Path
import json
import os
import shutil
import subprocess
from . import ROOT,FLAGS
from .common import encoded,identity,digest,source_map

MU0=4e-7*pi
PRODUCERS=('engineering/station_rail/native_drive.py',)


def exact_slab(*,field_peak_T=.2,wavelength_m=.5,slip_frequency_Hz=5.,
               conductivity_S_m=20e6,thickness_m=.015,height_m=.16,length_m=9.):
    """Infinite travelling wave, symmetric prescribed surface A, linear Al.

    Compare against the exact complex diffusion equation solution. Conductivity
    is a declared hot-material hypothesis, not a measured batch property.
    """
    import numpy as np
    if min(field_peak_T,wavelength_m,slip_frequency_Hz,conductivity_S_m,
           thickness_m,height_m,length_m)<=0:
        raise ValueError('Positive field, frequency and geometry required')
    k=2*pi/wavelength_m;w=2*pi*slip_frequency_Hz
    gamma=cmath.sqrt(k*k+1j*w*conductivity_S_m*MU0)
    a0=field_peak_T/k
    # Fixed high-order quadrature; no finite-element solver is called here.
    xi,wi=np.polynomial.legendre.leggauss(80)
    y=xi*thickness_m/2
    a=a0*np.cosh(gamma*y)/cmath.cosh(gamma*thickness_m/2)
    integral=sum(wi*(abs(a)**2))*thickness_m/2
    joule_per_length_height=.5*conductivity_S_m*w*w*integral
    force_per_length_height=.5*conductivity_S_m*w*k*integral
    return dict(field_peak_T_hypothesis=field_peak_T,wavelength_m_hypothesis=wavelength_m,
        slip_frequency_Hz=slip_frequency_Hz,conductivity_S_m_hypothesis=conductivity_S_m,
        thickness_m=thickness_m,height_m=height_m,length_m=length_m,
        gamma_real_m_inv=gamma.real,gamma_imag_m_inv=gamma.imag,
        skin_depth_m=sqrt(2/(w*conductivity_S_m*MU0)),
        Joule_W_per_m_length_per_m_height=float(joule_per_length_height),
        force_N_per_m_length_per_m_height=float(force_per_length_height),
        conditional_secondary_Joule_W=float(joule_per_length_height*length_m*height_m),
        conditional_longitudinal_force_N=float(force_per_length_height*length_m*height_m),
        useful_force_is_available=False,
        domain='Infinite travelling field and uniform infinitely tall secondary with imposed boundary flux; no primary, finite-height return current, steel, slots, lateral gap asymmetry or ends')


def conditional_map(required_force_N_per_car,*,speed_m_s=20.,length_m=9.,height_m=.16,
                    thickness_m=.015,airgap_each_side_m=.015,turns_hypothesis=80):
    rows=[]
    for slip in (.02,.05,.1,.15,.25):
        sync=speed_m_s/(1-slip)
        frequency=sync/.5
        for field in (.1,.2,.3):
            r=exact_slab(field_peak_T=field,slip_frequency_Hz=frequency*slip,
                length_m=length_m,height_m=height_m,thickness_m=thickness_m)
            # Optimistic gap-only flux MMF neglects all leakage and the real
            # steel reluctance; it is a lower bound, never a current prediction.
            mmf=field*(2*airgap_each_side_m+thickness_m)/MU0
            r.update(speed_m_s=speed_m_s,slip_hypothesis=slip,
                synchronous_speed_m_s=sync,primary_frequency_Hz=frequency,
                gap_only_MMf_Aturn_lower_bound=mmf,
                turns_hypothesis=turns_hypothesis,
                ideal_gap_only_current_A_lower_bound=mmf/turns_hypothesis,
                required_force_N_per_car=required_force_N_per_car,
                conditional_force_ratio=r['conditional_longitudinal_force_N']/required_force_N_per_car,
                actual_current_to_force_map=None,actual_terminal_voltage_V=None,
                actual_station_input_power_W=None,
                primary_copper_core_converter_losses_W=None,
                inverter_current_and_voltage_screen='unknown',
                longitudinal_force_screen='unknown')
            rows.append(r)
    return dict(schema='osr-LIM-conditional-bound-map/1',cases=rows,
        required_force_N_per_car=required_force_N_per_car,
        available_force_N_per_car=None,
        acceptance='not a motor force map; conditional boundary-field thought experiment',**FLAGS)


def _files(case,nx,ny):
    t=case['thickness_m'];length=.5
    k=2*pi/.5;w=2*pi*case['slip_frequency_Hz']
    g=complex(case['gamma_real_m_inv'],case['gamma_imag_m_inv'])
    inv=1/cmath.cosh(g*t/2)
    a0=case['field_peak_T_hypothesis']/k
    geo=f'''// Manufactured conducting slab, periodic-wave exact Dirichlet boundary.
Point(1)={{0,{-t/2},0,1}};Point(2)={{{length},{-t/2},0,1}};
Point(3)={{{length},{t/2},0,1}};Point(4)={{0,{t/2},0,1}};
Line(1)={{1,2}};Line(2)={{2,3}};Line(3)={{3,4}};Line(4)={{4,1}};
Curve Loop(1)={{1,2,3,4}};Plane Surface(1)={{1}};
Transfinite Curve{{1,3}}={nx+1};Transfinite Curve{{2,4}}={ny+1};
Transfinite Surface{{1}};
Physical Surface("Al_hypothesis",1)={{1}};
Physical Curve("exact_boundary",101)={{1,2,3,4}};
Mesh.MshFileVersion=2.2;
'''
    pro=f'''// Complex magnetic diffusion benchmark, following official GetDP
// Lib_Magnetodynamics2D_av_Cir: curl(nu curl A) + j omega sigma A = 0.
mu0=4.e-7*Pi;sigma={case['conductivity_S_m_hypothesis']};Freq={case['slip_frequency_Hz']};
k={k};gr={g.real};gi={g.imag};ur={inv.real};ui={inv.imag};A0={a0};
Group {{ Plate=Region[1]; Boundary=Region[101]; }}
Function {{
 r[]=Cosh[gr*Y[]]*Cos[gi*Y[]]*ur-Sinh[gr*Y[]]*Sin[gi*Y[]]*ui;
 i[]=Cosh[gr*Y[]]*Cos[gi*Y[]]*ui+Sinh[gr*Y[]]*Sin[gi*Y[]]*ur;
 exact[]=A0*Complex[r[]*Cos[k*X[]]+i[]*Sin[k*X[]],i[]*Cos[k*X[]]-r[]*Sin[k*X[]]];
}}
Constraint {{ {{ Name Exact; Case {{ {{ Region Boundary; Value exact[]; }} }} }} }}
Jacobian {{ {{ Name Vol;Case {{ {{ Region All;Jacobian Vol; }} }} }} }}
Integration {{ {{ Name Gauss;Case {{ {{ Type Gauss;Case {{ {{ GeoElement Triangle;NumberOfPoints 7; }} }} }} }} }} }}
FunctionSpace {{ {{ Name Aspace;Type Form1P;
 BasisFunction {{ {{ Name sn;NameOfCoef an;Function BF_PerpendicularEdge;Support Plate;Entity NodesOf[All]; }} }}
 Constraint {{ {{ NameOfCoef an;EntityType NodesOf;NameOfConstraint Exact; }} }}
}} }}
Formulation {{ {{ Name Diffusion;Type FemEquation;
 Quantity {{ {{ Name a;Type Local;NameOfSpace Aspace; }} }}
 Equation {{
  Integral {{ [1/mu0*Dof{{d a}},{{d a}}];In Plate;Jacobian Vol;Integration Gauss; }}
  Integral {{ DtDof [sigma*Dof{{a}},{{a}}];In Plate;Jacobian Vol;Integration Gauss; }}
 }}
}} }}
Resolution {{ {{ Name Solve;System {{ {{ Name S;NameOfFormulation Diffusion;Type ComplexValue;Frequency Freq; }} }}
 Operation {{ Generate[S];Solve[S];SaveSolution[S]; }}
}} }}
PostProcessing {{ {{ Name Result;NameOfFormulation Diffusion;
 Quantity {{
 {{ Name Joule;Value {{ Integral {{ [.5*sigma*Re[CompZ[Dt[{{a}}]]*Conj[CompZ[Dt[{{a}}]]]]];In Plate;Jacobian Vol;Integration Gauss; }} }} }}
 {{ Name ForceX;Value {{ Integral {{ [.5*sigma*Re[CompZ[Dt[{{a}}]]*Conj[CompY[{{d a}}]]]];In Plate;Jacobian Vol;Integration Gauss; }} }} }}
 {{ Name PotentialError;Value {{ Integral {{ [Re[(CompZ[{{a}}]-exact[])*Conj[CompZ[{{a}}]-exact[]]]];In Plate;Jacobian Vol;Integration Gauss; }} }} }}
 }}
}} }}
PostOperation {{ {{ Name Result;NameOfPostProcessing Result;Operation {{
 Print[Joule[Plate],OnGlobal,File "joule.txt",Format Table];
 Print[ForceX[Plate],OnGlobal,File "force.txt",Format Table];
 Print[PotentialError[Plate],OnGlobal,File "error.txt",Format Table];
}} }} }}
'''
    return geo,pro


def run(output,root=ROOT,*,getdp=None,gmsh='gmsh'):
    root=Path(root);output=Path(output)
    if output.exists():raise ValueError('Retain immutable previous run; choose a fresh output directory')
    output.mkdir(parents=True)
    getdp=Path(getdp) if getdp else root/'build/trip-dynamics/tools/getdp-3.5.0-Linux64/bin/getdp'
    gmsh=shutil.which(gmsh) or str(root/'.venv/bin/gmsh') if gmsh=='gmsh' else gmsh
    source=source_map(root,PRODUCERS)
    inp=exact_slab()
    (output/'inputs.json').write_bytes(encoded(dict(benchmark=inp,source_sha256=source)))
    cases=[]
    for nx,ny in ((40,4),(80,8),(160,16)):
        folder=output/f'mesh-{nx}x{ny}';folder.mkdir()
        geo,pro=_files(inp,nx,ny)
        (folder/'slab.geo').write_text(geo);(folder/'slab.pro').write_text(pro)
        commands=[[str(gmsh),'slab.geo','-2','-format','msh2','-o','slab.msh'],
                  [str(getdp),'slab.pro','-msh','slab.msh','-solve','Solve','-pos','Result','-v','4']]
        logs=[]
        for index,command in enumerate(commands):
            result=subprocess.run(command,cwd=folder,capture_output=True,text=True,timeout=180,
                env={**os.environ,'PATH':str(root/'.venv/bin')+os.pathsep+os.environ.get('PATH','')})
            log=result.stdout+result.stderr;(folder/f'command-{index}.log').write_text(log)
            logs.append(dict(argv=command,exit_code=result.returncode))
            if result.returncode:raise RuntimeError(f'Native diffusion run failed; retained {folder}/command-{index}.log')
        def scalar(name):
            lines=[x for x in (folder/name).read_text().splitlines() if x and not x.startswith('#')]
            # GetDP table has time/frequency followed by real and imaginary.
            row=[float(x) for x in lines[-1].split()]
            return row[1]
        joule=scalar('joule.txt');force=scalar('force.txt');error=scalar('error.txt')
        expected_joule=inp['Joule_W_per_m_length_per_m_height']*.5
        expected_force=inp['force_N_per_m_length_per_m_height']*.5
        cases.append(dict(nx=nx,ny=ny,commands=logs,
            Joule_W_per_m_height=joule,force_N_per_m_height=force,
            exact_Joule_W_per_m_height=expected_joule,
            exact_force_N_per_m_height=expected_force,
            relative_Joule_error=abs(joule-expected_joule)/expected_joule,
            relative_force_error=abs(force-expected_force)/expected_force,
            integrated_squared_A_error=error))
    result=dict(schema='osr-native-LIM-secondary-diffusion/1',
        execution='completed',native_solver='GetDP complex harmonic magnetic diffusion',
        geometry='0.5m long x15mm thick manufactured conducting slab, per metre height',
        candidate_force_map=False,actual_primary_current_map=False,
        exact_boundary_solution=inp,cases=cases,
        convergence_screen='pass' if cases[-1]['relative_Joule_error']<.01 and cases[-1]['relative_force_error']<.02 and cases[-1]['relative_Joule_error']<cases[0]['relative_Joule_error'] else 'fail',
        source_sha256=source,**FLAGS)
    (output/'result.json').write_bytes(encoded(result))
    manifest=dict(schema='osr-native-secondary-package/1',source_sha256=source,
        files_sha256={p.relative_to(output).as_posix():digest(p) for p in sorted(output.rglob('*')) if p.is_file()},**FLAGS)
    manifest['manifest_id']=identity(manifest);(output/'manifest.json').write_bytes(encoded(manifest))
    return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path);parser.add_argument('--root',type=Path,default=ROOT)
    args=parser.parse_args()
    print(json.dumps(run(args.output,args.root),indent=2))
