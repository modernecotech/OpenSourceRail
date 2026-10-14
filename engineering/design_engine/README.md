# Shared Design Engine

The common engine connects existing physical definitions and solvers through
one scoped problem, candidate, job, verification matrix and review package.
Legacy studies retain their formats and record ownership. Computation is local;
GitHub Actions remains disabled.

```bash
./osr design problems
./osr design run --problem clipped-side-bay --city samawah
./osr design refine --problem clipped-side-bay --city samawah --evaluations 256
./osr design jobs --city samawah
./osr design verify run-0123456789abcdef
./osr design verify run-0123456789abcdef --historical
./osr design compare run-0123456789abcdef run-fedcba9876543210
./osr design export run-0123456789abcdef --output build/review/my-fresh-package
```

Candidate JSON is a list of complete variable maps supplied with `--candidates`.
Function, units, variable domains, load cases, model limits and mandatory checks
are declared before execution. Side and roof bays are separate problems; a
smaller roof cannot win a side-panel comparison. Missing complete installed
mass, prices, lifecycle scope, carbon and calibration stay unknown.

Jobs use an indexed local store at `var/design-engine`. Each attempt retains
its request, outputs, failures and manifest. Resume requires unchanged source
and solver environment and appends an attempt. Cancellation never erases the
original attempt. Native input, evaluation, time and memory budgets remain
separate from the engineering checks.

Screening and detailed confirmation have separate rankings and evidence.
The panel adapter calls the existing mapped plate/rail solver, mesh comparison,
all individual clip-loss cases and combined pressure/fault holdouts. It retains
adverse results. Curved geometry cannot use that flat plate model. Assembly
adapters preserve unresolved supplier inventories, site calibration, full
passage/contact domains and independent decisions.

Review exports preserve exact source and attempt bytes, quantities, mandatory
checks, RFQ scopes and licensing for offline review. They prepare drafts;
they cannot overwrite adopted finance, production or railway baselines.
Local hashes do not authenticate an executor, establish physical correlation
or appoint an independent assessor. See [licensing](LICENSE.md).

For the fixed-function side-panel pilot, pass `--candidates engineering/design_engine/data/panel-pilot.json --shortlist 4` to `refine`. Add `--native` to `export` for bounded shortlist CAD/STEP/unissued drawings and available IFC. The UI downloads hashed review chunks and original attempt logs, including failed runs.

Future record verification uses independently authenticated Ops Core accounts (existing `approver` or `admin` roles), rather than the appointed-role text. Cost scope completeness and finite-resource schedules are available in the common UI. See the [acceptance status](../../docs/design-engine/plan-status.md) for incomplete engineering packages.

Current physical candidates accept scoped manufacturing/site/prestress input drafts in the inspector. Original definitions remain immutable; failed geometry, clearance and conditional stress checks are retained. Public converter/PV candidates are previews with no installed credit. Searches retain charged finite sensitivity; vehicle confirmation conserves separate equipment/modal mass and checks actual whole-assembly coverage. Independent numerical benchmarks include `electrical-balance`, `prestress-reference` and `vehicle-conservation` through `tools/automation/design-benchmark.py`.
