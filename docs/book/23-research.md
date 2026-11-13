# Research choices and independent checks

The wheel-supported railway is a development reference, not the end of
exploration. The project keeps earlier maglev work as historical research
and allows new candidates to test propulsion distribution, train formation,
running gear, speed, station spacing and civil form. The purpose is to
find a useful, affordable system under real constraints. An attractive
isolated result should lead to a fuller comparison, not silently replace
the reference design.

## Compare the service that a city receives

A lighter carbody, shorter train or different drive may save capital
while changing seats, frequency, power, platform length, repair effort and
failure response. The comparison is fair only when each candidate is asked
to deliver the same defined transport service and mandatory passenger
protection. If a concept offers less capacity, takes longer or needs more
vehicles, those differences belong in the result. Local manufacture and
repair capability are also part of the objective, because a system that
cannot be supported locally may become expensive or unreliable later.

Different questions need different models. A quick analytical calculation
can reject an impossible geometry or expose a missing mass account before
a large numerical study. A coarse structural model can identify important
load paths. Fine models are useful when their mesh, material, supports and
loads represent the decision at hand. Physical tests are needed when a
model cannot establish a critical interface or material behaviour. Moving
up this ladder costs time and storage, so the most valuable question is
often what evidence would change the choice between two candidates.

## Agreement is useful, with a boundary

Two independent solvers that agree on a span's displacement give confidence
that the numerical implementation of that particular model is consistent.
They do not prove that the real rail seat, bearing, pier and foundation
have the same behaviour. Repeating a mesh at greater resolution can reveal
numerical sensitivity. It does not introduce a missing bolt, fatigue case
or construction load. A physical measurement, with an approved test
method and independently reviewed limit, has a different role again.

The civil work already contains comparisons between newer SolidCraft and
FieldCraft methods and independent FreeCAD and CalculiX checks. The new
tools can help agents generate geometry and evaluate alternatives, while
the older independent route remains valuable where it tests the same
physical question through another implementation. A tool should be retired
only when its role is either replaced with evidence or clearly preserved
for historical reproduction. Convenience alone is a weak reason to lose
an independent check.

## Keep failures useful

A failed design can teach the project where a load path, interface or model
is inadequate. A solver that does not converge, a candidate that exceeds
a thermal limit and a mechanism that cannot carry the declared axial load
are different findings. Each should retain its inputs, conditions and
reason for failure. A rejected pin-jointed mechanism does not reject a
bonded shell unless the shell is tested under an appropriate model. An
unsupported material law should remain unsupported rather than be replaced
quietly by a convenient substitute.

Research alternatives also need ancestry. A change in magnetic-flux
hypothesis may be a new evaluation of the same physical geometry. A new
bogie or door layout is a physical revision and should propagate through
mass, braking, civil loads, manufacturing and cost. A selection records why
one candidate is preferred for a stated purpose; it is not a claim that
the railway has passed physical acceptance. This discipline lets an open
community explore boldly while keeping each conclusion understandable.
