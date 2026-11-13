# New CAD and mechanics tools

Three-dimensional models make a railway easier to inspect. A reader can
see how a door guide sits above an opening, how a bogie carries a body,
or how a precast beam reaches its bearing. The newer SolidCraft and
FieldCraft tools are being introduced to help generate geometry and run
bounded structural studies more directly from a candidate. Their value
depends on whether the model represents the physical question and whether
another method can challenge the answer.

## Geometry before a large solve

SolidCraft has generated a representative door-header stock blank and
reopened its exported solid. An independent FreeCAD import reproduced
the geometry. This demonstrates a useful interchange: a part definition
can leave one tool and be examined in another. It does not turn the blank
into a complete door operator. The carriage, belt, motor, sensors, body
mounts, tolerances and removal path still have to be mated.

One export format does not preserve every source property, such as material
or design provenance. That information must therefore travel with the
geometry in a companion record. A viewer should know whether it is seeing
a stock blank, an assembled proposal or a physically measured part. The
same visible shape can have quite different evidence maturity depending
on that context.

## What a structural comparison establishes

FieldCraft has been compared with CalculiX on shared meshes for a bounded
normal-load civil model. The methods agreed very closely on a roughly
ten-millimetre displacement in that model. A mesh refinement comparison
also met its declared diagnostic threshold. These are useful checks of
the computation, but they do not establish that the real rail seat,
bearing, reinforcement, pier and foundation will behave in the modelled
way. The fine result still needs convergence and the full physical
interfaces to be represented.

The study derives the reference formation's 24 axle positions and keeps
normal passenger and crowd structural cases distinct. Moving loads can
change the critical position of a beam response. Braking, thermal movement,
fatigue and construction loads can change the critical *type* of response.
A model that is excellent for one question may be unsuitable for another;
this is why the Workbench should display its load and geometry domain
beside its result.

## Keep an independent route

The tool migration is selective. SolidCraft is useful for light candidate
geometry and FieldCraft for a demonstrated mechanics domain. FreeCAD and
CalculiX remain valuable independent checks where they answer the same
question with a different implementation. Meshing and specialist tools
remain where the current workflow still needs them. Historical evidence
is preserved; older tools are retired from default use only when their
current role has a supported replacement or a deliberate verification
route remains.

For the next candidate, the better sequence is to resolve cheap geometric
and load-path questions before running finer models. The door's mating
datums, guide removal and installed mass are upstream of a useful detailed
door solve. The civil span's rail support, bearing, foundation and lift
configuration are upstream of a construction decision. New tools make
these studies faster and more accessible when they are asked the right
question. They cannot recover a missing physical interface from numerical
precision alone.

## Choosing a model for a decision

Consider a city asking whether two civil forms can be made in a local
precast yard. A coarse geometry and material take-off may be enough to
compare handling sizes, moulds and likely transport. A fine stress model
cannot answer whether the road can carry a beam to the site. When the
question becomes bearing stress or fatigue, the connection and support
details must be represented and the numerical model can become more
detailed. The amount of computation should follow the question, not
the visual sophistication of the model.

The same sequence applies to the door. A stock blank establishes a
fabrication envelope and tests whether geometry can be exchanged between
tools. A fitted operator study needs its actual joints and moving
parts. A qualification test needs manufactured samples and approved
limits. Each stage produces evidence that is useful within its boundary.
Showing those stages explicitly lets a non-specialist appreciate progress
without mistaking an impressive rendering for a finished component.
