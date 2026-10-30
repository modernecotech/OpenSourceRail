# Source-backed engineering revisions

[Project introduction](../../README.md) · [Current engineering](../../docs/design-engine/current/README.md)

This continuing research package uses exact manufacturer variants and published
experiments to replace selected placeholders. It preserves the selected v0.6
wheel/LIM reference and all earlier source-bound experiments. Compact wayside
roller drives are separate research architectures, with passive onboard contact
elements; they do not inherit LIM results or operating approval.

Install the packet's declared environment with
`python -m pip install -r engineering/sourced_case/requirements.txt` in the project
virtual environment. It pins the NumPy version used by these recorded runs in
addition to the shared numerical dependencies.

```sh
./osr design sourced plan
./osr design sourced run --state build/sourced-cell --max-cases 30
./osr design sourced verify --state build/sourced-cell
./osr design sourced publish --state build/sourced-cell
./osr design sourced publish-geometry --state build/sourced-cell
./osr design sourced verify-publication
./osr design sourced verify-geometry
./osr design sourced verify-methods
./osr design sourced dashboard --state build/sourced-cell
./osr design sourced serve --state build/sourced-cell --port 8772
```

For the complete published run, optionally supply its matching saved report with
`--closure-report docs/design-engine/sourced-case/closure.json.gz`. A different or
partial run needs its own report; the explorer rejects mismatched report identities.

The deterministic worker controller can generate and replay the same campaign
with three bounded subprocesses:

```sh
tools/automation/osr-python tools/automation/sourced-execute.py gen build/sourced-cell --workers 3 --audit var/sourced-audit
tools/automation/osr-python tools/automation/sourced-execute.py publish build/sourced-cell --workers 3 --audit var/sourced-audit --output docs/design-engine/sourced-case
tools/automation/osr-python tools/automation/sourced-archive.py split docs/design-engine/sourced-case
tools/automation/osr-python tools/automation/sourced-archive.py ensure docs/design-engine/sourced-case
tools/automation/osr-python tools/automation/sourced-verify.py docs/design-engine/sourced-case --workers 3 --audit var/sourced-verification
```

Refresh the source-bound closure report and its display projection after a full
run with:

```sh
python tools/automation/sourced-closure-package.py publish build/sourced-cell build/sourced-closure
python tools/automation/sourced-closure-package.py verify build/sourced-cell build/sourced-closure
```

The closure packager reopens the retained native-method archives, rebuilds the
report from the exact saved case state, and checks the summary against the
complete report. It writes only into a fresh or empty output directory. The
report remains a software-evidence summary; no physical or engineering acceptance
is inferred.

Parallel verification reconstructs all five registries and actually recomputes
every case. It preserves the original publication contract; it does not replace
semantic replay with hash checking. Source snapshots, failures, runtimes and
worker receipts remain in the separate audit directories.

The campaign propagates five equipped body families through two distances and
three source-conditioned propulsion contexts. Each cell receives nine load/fault
journeys, actual occurrence-linked production drafts and longitudinal civil load
transfer. The same candidate and evaluation identities bind every output.
Sources, conditions and versions are in `data/*-sources.json`; the immutable run
contains its actual source snapshot. Changing production code requires a new run
directory. Cached cases cannot cross source epochs.

`equipment.py`, `commerce.py`, `power_revision.py` and `drive.py` retain catalogue
conditions, ambiguous units, conflicting document revisions and missing values.
Published prices are scoped Class B subtotals; they are not supplier quotations
or installed whole-life estimates. `charging.py` proposes separately identified
hardware changes when the currently counted converters cannot restore energy.

The structural lineage deliberately retains unsuccessful evaluator versions:
`structure.py`/`whole_structure.py` contain the initially exposed width defect;
`layered_structure.py`/`whole_refinement.py` correct that defect and count repeated
physical connections. Later contact-integration corrections receive their own
producer and evaluation. A solver exit code of zero is distinct from residual
validity, kinematic domain, physical feasibility and qualification.

The operating solver limits source-conditioned torque, current, gearing and
speed; integrates actual force, energy, independent braking and faults; and
accounts for auxiliary energy. Its required quasi-static current is not measured
closed-loop current, and nominal pad friction is not a validated wet/temperature
brake map. It does not claim validated tyre contact, full inverter losses or
thermal equilibrium. Public experiments qualify only their own configurations.

Every manufacturing export remains a disabled research draft. No command submits
orders, changes live work orders, energises plant or grants movement authority.
Prototype, HIL, independent engineering assessment and site approvals remain
separate authenticated evidence tasks.
