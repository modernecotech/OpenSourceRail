// 3D scalar magnetic potential, Picard nonlinear constitutive solve.
// Reference: official GetDP3.5 Lib_Magnetostatics_a_phi.pro formulation.
// Manufactured law B(H)=mu0*H+Js*tanh(H/Hs), not a measured steel grade.
mu0=4.e-7*Pi; Js=1.5; Hs=1500.; Hstar=1000.; gap=0.02;
Bstar=mu0*Hstar+Js*Tanh[Hstar/Hs];
potentialDrop=gap*Bstar/mu0+0.08*Hstar;
Group { Air=Region[1]; Steel=Region[2]; Domain=Region[{1,2}]; Bottom=Region[101]; Top=Region[102]; }
Function {
  mu[Air]=mu0;
  mu[Steel]=mu0+Js*Tanh[Norm[$1]/Hs]/(Norm[$1]+1.e-30);
}
Constraint { { Name Boundary; Case {
  { Region Bottom; Value 0.; }
  { Region Top; Value -potentialDrop; }
} } }
Jacobian { { Name Volume; Case { { Region All; Jacobian Vol; } } } }
Integration { { Name Quadrature; Case { { Type Gauss; Case {
  { GeoElement Tetrahedron; NumberOfPoints 4; }
} } } } }
FunctionSpace { { Name Potential; Type Form0;
  BasisFunction { { Name sn; NameOfCoef phin; Function BF_Node; Support Domain; Entity NodesOf[All]; } }
  Constraint { { NameOfCoef phin; EntityType NodesOf; NameOfConstraint Boundary; } }
} }
Formulation { { Name Magnetostatic3D; Type FemEquation;
  Quantity { { Name phi; Type Local; NameOfSpace Potential; } }
  Equation {
    Integral { [ -mu0*Dof{d phi},{d phi} ]; In Air; Jacobian Volume; Integration Quadrature; }
    Integral { [ -mu[-{d phi}]*Dof{d phi},{d phi} ]; In Steel; Jacobian Volume; Integration Quadrature; }
  }
} }
Resolution { { Name Solve;
  System { { Name S; NameOfFormulation Magnetostatic3D; } }
  Operation {
    InitSolution[S]; Generate[S]; Solve[S];
    Generate[S]; GetResidual[S,$initial];
    Evaluate[$res=$initial,$iter=0];
    While[$res>1.e-10 && $res/$initial>1.e-10 && $iter<100] {
      Solve[S]; Generate[S]; GetResidual[S,$res]; Evaluate[$iter=$iter+1];
      Print[{$iter,$res,$res/$initial},Format "PICARD %g %.15e %.15e"];
    }
    SaveSolution[S];
  }
} }
PostProcessing { { Name Results; NameOfFormulation Magnetostatic3D;
 Quantity {
  { Name B; Value { Term { [-mu[-{d phi}]*{d phi}]; In Domain; Jacobian Volume; } } }
  { Name BzAir; Value { Integral { [-mu0*CompZ[{d phi}]/(0.1*0.1*gap)]; In Air; Jacobian Volume; Integration Quadrature; } } }
  // Air Maxwell stress Tzz, averaged over the gap's parallel planes.
  { Name AirPressureForce; Value { Integral {
    [ mu0*(CompZ[{d phi}]^2-0.5*SquNorm[{d phi}])/gap ];
    In Air; Jacobian Volume; Integration Quadrature;
  } } }
 }
} }
PostOperation { { Name Results; NameOfPostProcessing Results;
 Operation {
  Print[BzAir[Air],OnGlobal,File "mean-Bz.txt",Format Table];
  Print[AirPressureForce[Air],OnGlobal,File "air-force.txt",Format Table];
  Print[B,OnElementsOf Domain,File "field.pos"];
 }
} }
