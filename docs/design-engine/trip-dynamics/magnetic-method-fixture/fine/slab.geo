// Manufactured 3D nonlinear constitutive fixture, NOT train geometry.
SetFactory("OpenCASCADE");
DefineConstant[h = {0.012500000000000001}];
Box(1) = {0, 0, 0, 0.1, 0.1, 0.02};
Box(2) = {0, 0, 0.02, 0.1, 0.1, 0.08};
v()=BooleanFragments{ Volume{1,2}; Delete; }{};
Physical Volume("air",1) = {1};
Physical Volume("nonlinear_manufactured_material",2) = {2};
eps=1e-7;
bottom()=Surface In BoundingBox{-eps,-eps,-eps,0.1+eps,0.1+eps,eps};
top()=Surface In BoundingBox{-eps,-eps,0.1-eps,0.1+eps,0.1+eps,0.1+eps};
Physical Surface("bottom",101) = {bottom()};
Physical Surface("top",102) = {top()};
Mesh.MeshSizeMin=h;
Mesh.MeshSizeMax=h;
Mesh.MshFileVersion=2.2;
