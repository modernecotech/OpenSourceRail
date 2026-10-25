"""Explicit finite 3D scalar-potential Newton/load-continuation formulation.

The geometry, B(H), PM recoil and output sampling match finite_coupon.py.
Only the low-H tangent branch is corrected; no source text is extracted/edited.
"""
STAGES=10
ITERATIONS=30
ABS_TOL=1e-9
REL_TOL=1e-7
COUNTS=(64,24,12)


def formulation(value,mesh,contours):
    grade=value['materials'][value['grade_id']];steel=value['materials']['steel'];mu_r=grade['recoil_relative_permeability'];scale=1+grade['br_temperature_coefficient_per_k']*60
    pairs=','.join(f'{x:.17g},{y:.17g}' for x,y in zip(steel['h_a_m'],steel['j_t']));pm_groups=','.join(str(x) for x in mesh['physical_pm'])
    if len(mesh['physical_pm'])!=len(mesh['pm_regions']):raise ValueError('PM region/source inventory differs')
    br='\n'.join(f'br[Region[{pg}]]=$load*Vector[0,{r["Br_y_T"]*scale:.17g},{r["Br_z_T"]*scale:.17g}];\n dir[Region[{pg}]]=Vector[0,{r["Br_y_T"]/grade["br_20c_t"]:.17g},{r["Br_z_T"]/grade["br_20c_t"]:.17g}];' for pg,r in zip(mesh['physical_pm'],mesh['pm_regions']))
    prints=[]
    for index,(lo,hi) in enumerate(contours):
        for axis in range(3):
            others=[i for i in range(3) if i!=axis]
            for side in (0,1):
                a=list(lo);a[axis]=hi[axis] if side else lo[axis];b=a.copy();b[others[0]]=hi[others[0]];d=a.copy();d[others[1]]=hi[others[1]]
                pts=' '.join('{'+','.join(f'{x:.17g}' for x in p)+'}' for p in (a,b,d))
                prints.append(f'Print[B,OnPlane{{{pts}}}{{{COUNTS[others[0]]},{COUNTS[others[1]]}}},File "face-{index}-{axis}-{side}.txt",Format SimpleTable];')
    return f'''// Explicit continuation formulation; unchanged physical coupon; no material validation.
mu0=4.e-7*Pi;
Group{{Air=Region[300];Steel=Region[200];PM=Region[{{{pm_groups}}}];Domain=Region[{{Air,Steel,PM}}];Outer=Region[400];}}
Function{{
 j[] = InterpolationLinear[Min[Norm[$1],100000.]]{{{pairs}}};
 dj[] = Norm[$1]>100000. ? 0. : dInterpolationLinear[Norm[$1]]{{{pairs}}};
 mu[Air]=mu0;mu[PM]={mu_r:.17g}*mu0;
 mu[Steel]=Norm[$1]<1.e-6 ? mu0+0.0025 : mu0+j[$1]/Norm[$1];
 dbdh[Steel]=Norm[$1]<1.e-6 ? (mu0+0.0025)*TensorDiag[1,1,1] : mu[$1]*TensorDiag[1,1,1]+(dj[$1]-j[$1]/Norm[$1])/SquNorm[$1]*SquDyadicProduct[$1];
 br[Air]=Vector[0,0,0];br[Steel]=Vector[0,0,0];
 {br}
}}
Constraint{{{{Name Zero;Case{{{{Region Outer;Value 0.;}}}}}}}}
Jacobian{{{{Name V;Case{{{{Region All;Jacobian Vol;}}}}}}}}
Integration{{{{Name I;Case{{{{Type Gauss;Case{{{{GeoElement Tetrahedron;NumberOfPoints 4;}}}}}}}}}}}}
FunctionSpace{{{{Name Potential;Type Form0;BasisFunction{{{{Name sn;NameOfCoef pn;Function BF_Node;Support Domain;Entity NodesOf[All];}}}}Constraint{{{{NameOfCoef pn;EntityType NodesOf;NameOfConstraint Zero;}}}}}}}}
Formulation{{{{Name Magnet3D;Type FemEquation;Quantity{{{{Name p;Type Local;NameOfSpace Potential;}}}}
Equation{{
 Integral{{[-mu[]*Dof{{d p}},{{d p}}];In Region[{{Air,PM}}];Jacobian V;Integration I;}}
 Integral{{[br[],{{d p}}];In PM;Jacobian V;Integration I;}}
 Integral{{[-mu[-{{d p}}]*{{d p}},{{d p}}];In Steel;Jacobian V;Integration I;}}
 Integral{{[-dbdh[-{{d p}}]*Dof{{d p}},{{d p}}];In Steel;Jacobian V;Integration I;}}
 Integral{{[dbdh[-{{d p}}]*{{d p}},{{d p}}];In Steel;Jacobian V;Integration I;}}
}}}}}}
Resolution{{{{Name Solve;System{{{{Name S;NameOfFormulation Magnet3D;}}}}Operation{{
 InitSolution[S];Evaluate[$load=0.,$stage=0,$ok=1];
 While[$stage<{STAGES} && $ok]{{
 Evaluate[$stage=$stage+1,$load=$stage/{STAGES}.];
 Generate[S];GetResidual[S,$initial];Evaluate[$res=$initial,$iter=0];
 Print[{{$load,$initial}},Format "LOAD %.3f INITIAL %.15e"];
 While[$res>{ABS_TOL:.17g} && $res/Max[$initial,1.e-30]>{REL_TOL:.17g} && $iter<{ITERATIONS}]{{
 Solve[S];Generate[S];GetResidual[S,$res];Evaluate[$iter=$iter+1];
 Print[{{$load,$iter,$res,$res/Max[$initial,1.e-30]}},Format "CONTINUATION %.3f %g %.15e %.15e"];
 }}
 Print[{{$load,$iter,$res,$res/Max[$initial,1.e-30]}},Format "STAGE-END %.3f %g %.15e %.15e"];
 Evaluate[$ok=($res<={ABS_TOL:.17g} || $res/Max[$initial,1.e-30]<={REL_TOL:.17g})];
 }}
 SaveSolution[S];
}}}}}}
PostProcessing{{{{Name Results;NameOfFormulation Magnet3D;Quantity{{
 {{Name B;Value{{Term{{[-mu[-{{d p}}]*{{d p}}+br[]];In Domain;Jacobian V;}}}}}}
 {{Name Hparallel;Value{{Term{{[-{{d p}}*dir[]];In PM;Jacobian V;}}}}}}
 {{Name SteelB;Value{{Term{{[Norm[mu[-{{d p}}]*{{d p}}]];In Steel;Jacobian V;}}}}}}
}}}}}}
PostOperation{{{{Name Results;NameOfPostProcessing Results;Operation{{
 {' '.join(prints)}
 Print[Hparallel,OnElementsOf PM,Depth 0,File "PM-H.txt",Format SimpleTable];
 Print[SteelB,OnElementsOf Steel,Depth 0,File "steel-B.txt",Format SimpleTable];
}}}}}}
'''
