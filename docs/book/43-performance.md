# Efficient repeated studies

An open design platform should make revision inexpensive enough that
engineers and cities can explore alternatives. If changing one station
requires rebuilding every train, remeshing every structure and republishing
every city, the workflow becomes slow and wastes storage. v0.7 therefore
works on a simple principle: recalculate what the changed input actually
affects, retain the rest with its verified identity, and refuse reuse when
the physical or numerical question has changed.

## Follow dependencies, not folders

In the Samawah midpoint example, the route geometry, selected vehicle and
most civil quantities remain unchanged. The station and access inputs
change, so the dependent service, energy, cost and dossier results must be
re-evaluated. A later change in a labour rate could alter factory or
construction cost without changing the map. A new bogie would have a much
wider effect: mass, dynamics, braking, beam loads, manufacturing and
whole-life cost would all need review.

The Workbench's project envelope now rejects mixed candidates and stale
upstream stages. It can show that a result is genuinely reused when the
relevant request is unchanged. This saves more time than accelerating an
unnecessary calculation. Reuse is not a shortcut around evidence. It
requires the applicable inputs, model domain and tool version to agree.

## Keep work within the computer's resources

City studies use a bounded queue with at most two analytic workers by
default and shared reservations for processor, memory and disk use. A
local comparison showed a pair of fresh studies completed sooner in
parallel than in a serial run, with matching numerical outputs. That is
a measured improvement for that case, not a promise that more workers
always help. Parallel jobs can use more total processor time and contend
for memory or storage. Heavy native analyses therefore need their own
admission budgets.

The project has also kept successful compressed results under a budget and
uses an explicit disk reserve before starting work. Failed or interrupted
studies retain useful evidence rather than disappearing into an automatic
cleanup. This distinction matters to researchers: a failed solve can show
an invalid model, a resource limit or a genuinely poor candidate. Such
records should not be silently recast as a green result or deleted as
mere waste.

## Use Rust where it wins on the whole task

Rust is already part of the control and city tooling, and a bounded
delivery scheduling kernel has a verified Rust implementation. In a
same-input comparison, the complete delivery compilation became modestly
faster with that optional backend, while the physical and policy outputs
matched. Python remains the default path. A separate experiment in
canonical encoding found only a small overall benefit, so it was not
promoted broadly. These findings support targeted migration rather than
a wholesale rewrite of already working engineering models.

A reader benefits when a warm city study responds quickly and when a
changed input receives a distinct, trustworthy answer. They do not need
to know which language ran a particular stage. The most useful performance
report therefore includes waiting time, resource use, verified reuse and
the scope of the result. For v0.7, speed is a means of making a more
complete and reviewable project, not a substitute for missing engineering.

## What should be measured next

The most useful performance measurements follow a representative task
from a user's click to a sealed result. They include the time spent
waiting in the queue, the calculation itself, verification, writing and
opening the report. A native structural run needs memory and temporary
disk peaks in addition to wall time. A city study needs to distinguish
new service work from reused geometry or unchanged price inputs. These
measurements reveal where an optimisation would actually help the reader.

One bottleneck can move after another is solved. Faster cost arithmetic
will not help much if the worker spends its time loading a large archive.
Parallelism may lower wait time for two small jobs but harm a large
finite-element solve on the same machine. A compact summary can make the
Workbench responsive while full numerical evidence remains available
on demand. The platform should report these trade-offs alongside
numerical agreement, so speed never hides a changed answer.
