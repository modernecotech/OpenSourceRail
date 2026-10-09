# Civil system exploration

This workbench investigates complete span–pier–foundation packages using the
existing component catalogue and native OpenSeesPy. Its first campaign compares
Pi20/Pi25 controls, a hollow deck, a hollow stepped tapered pier, and their
combination over **100 m of double-track viaduct**. Existing canonical designs,
costs, production records and engineering release statuses remain separate.

From the repository root, using the normal engineering Python environment and
native `ccx` installed for the existing reference replay:

```sh
tools/automation/osr-python tools/automation/civil-study.py run
tools/automation/osr-python tools/automation/civil-study.py verify \
  build/engineering/civil-studies/first-campaign
```

`run` freezes the input contract, copies governing source files, reproduces the
existing native beam/drainage reference, verifies independent new benchmarks,
executes isolated bounded workers and writes `comparison.md`, `comparison.csv`
and `comparison.json`. The repository commit and source hashes identify the
baseline even when the implementation has not yet been committed. Set
`--output` to a fresh directory for each campaign.

Use `run --resume` to reuse only hash-verified results from the same study,
code and native environment. `--retry-failed` creates another attempt while
retaining the failed one. A terminated attempt's job/log files remain in its
attempt directory. `verify --historical` checks retained artifact binding without
claiming that old dependencies are current. A checksum is not a reviewer signature.

## Full investigation programme

```sh
tools/automation/osr-python tools/automation/civil-study.py programme \
  --search-evaluations 96 --output build/engineering/civil-studies/programme
```

This executes numerical component benchmarks, eight registered deck families,
CAD/IFC quantity checks, commercial/equipment adapters, continuity/thermal cases,
a coupled sprung/unsprung train diagnostic, three-seed constrained optimisation
with an equal-budget random baseline, declared uncertainty scenarios, three
actual-section solid meshes per detailed shortlist, physical-test protocols,
artifact retrieval and a sealed promotion proposal. It also repeats the full
reference transient campaign. `--quick` omits that last repeat.

`programme.json` and `programme.md` audit C01–C14 separately from engineering
acceptance. Actual suppliers, measured materials/soil, physical tests and named
independent acceptance are still required; the software cannot manufacture them.

## More realistic response models

- Actual disjoint section regions drive CAD, quantities, area, centroid and both
  bending inertias. Solid end diaphragm regions are counted once and have their
  own stiffness/mass. The hollow deck is a research box, not a qualified product.
- Native elastic Timoshenko elements include shear deformation, consistent mass
  and rotary inertia. Each span retains its own rotations and finite horizontal
  and vertical bearings. Shared piers, rigid cap offsets, pier self-weight and
  foundation-cap mass complete the 2D load path.
- Two explicitly **uncalibrated** ground stiffness scenarios provide finite
  axial, lateral and rotational compliance. Illustrative pile-group dimensions
  support equal-scope takeoff; they do not establish geotechnical resistance.
- The actual retained **12-axle LM3 AW2 planning pattern** crosses both tracks
  synchronously. Static positions, Newmark moving-force histories at two speeds,
  modal shapes, acceleration and braking response are retained. The reference moving-force campaign does not include
  suspension feedback; the separate coupled-vehicle diagnostic does. Asymmetric
  loading and Baghdad six-car geometry need their actual supplier inputs.
  A mesh-independent 2 m triangular rail-distribution footprint avoids an
  instantaneous axle-load jump at model entry. The footprint is an explicit
  unverified track assumption; load and moment conservation are independently
  checked and its physical applicability needs validation.
- Handling models use the fabricated beam's nonuniform mass and overhanging
  supports at 20/80% span, rather than the service bearing arrangement. The
  complete suspended study mass includes a separate rigging allowance.

Three static/handling meshes and independent dynamic mesh/time refinements
check response sensitivity. Failure of a declared convergence tolerance remains
a failed numerical screen. Research lift limits are separate provisional
constraints. Null railway limits and quotations remain unresolved. Elastic fibre
stress is a gross-section response, not prestressed capacity or fatigue evidence.

Independent benchmarks cover Timoshenko UDL deflection/reactions, point loading
with support settlement, a flexible-base pier, Rayleigh-limit modal frequencies,
and moving-force histories against analytical modal superposition. See
[`benchmarks`](../analysis/benchmarks/civil/exploration.py). These verify equations
and implementation; they provide no physical validation.

## Contracts, history and resource limits

[`config/reference.json`](config/reference.json) owns the initial input values.
[`schemas`](schemas/) publish strict study and candidate contracts. Unknown keys,
wrong unit field names, booleans as measurements, nonfinite values, duplicate JSON
keys, incompatible geometry and stale input hashes fail closed.

Design IDs bind configuration and geometry. Evaluation IDs additionally bind
the complete study, scenario, analysis implementation and native library bytes.
Results and review state are separate records. Each attempt retains its job,
compressed native response fields, modal shapes, governing conditions, convergence checks,
logs, failures and output hashes. The append-only ledger is also hash-bound.

Modify a design by creating a definition containing only `deck` and `pier`, then:

```sh
tools/automation/osr-python tools/automation/civil-study.py derive \
  --parent build/engineering/civil-studies/first-campaign/candidates/CANDIDATE_ID.json \
  --definition my-revised-definition.json --output build/engineering/civil-studies/child.json \
  --reason 'Investigate a thicker bottom flange'
```

The child retains its parent ID and change reason; the parent is untouched. Put
the child definition, `parents` and `modification_reason` in a new campaign's
candidate row and the complete parent records in `lineage_records`. Ancestors
are validated and retained; missing parents and lineage cycles are rejected.
Result histories can
be inspected independently; native fields remain scratch artifacts under
`build/engineering/`. Compact intentional review evidence may be retained under
the [repository artifact policy](../../docs/repository-artifact-policy.md).

Workers run sequentially, use one numerical-library thread, have a 4 GiB address
space limit and a registered timeout. Candidate count is checked against the
campaign budget before outputs are created. Resume does not bypass source or
native-environment checks. An execution failure is not structural infeasibility.

## Remaining model and evidence work

The reference system is linear and planar. The programme additionally runs
nonlinear Concrete02/steel fibre sections, native PySimple1/TzSimple1/QzSimple1
piles, P-delta columns, Coulomb friction bearings, orthotropic coupons and actual
C3D20R solid sections. These have explicit, limited verification domains.
It does not qualify prestress losses, cracking, shear/torsional resistance,
connections, transverse cap bending, cyclic pier response, nonlinear pile/soil
behaviour, uplift, scour, fire, fatigue, track irregularity or actual lift
stability. Rayleigh damping and finite-domain entry/exit effects require further
study. Actual train supplier records, material tests, soil data, quotes and
independent review remain inputs to later phases.

Controlled evidence can be supplied through `evidence_refs`. A measured,
supplier-verified or site-calibrated flag requires its role's source and checksum;
those raw records are copied into the sealed study. Source currency is checked
again after execution. Such a flag does not itself grant engineering acceptance.

See the [implementation and acceptance backlog](../../docs/civil/design-exploration.md).
The [compact retained campaign review](examples/README.md) keeps numerical
summaries and exact provenance available without committing high-volume fields.
The constrained optimiser uses verified reduced models within a declared
hollow-deck/pier domain. It retains each mutation, failure, cache hit and source
identity. Different random seeds and equal evaluation budgets remain visible;
no global optimum or validated cost saving is asserted. No candidate belongs to a qualified
feasible Pareto set and no result triggers catalogue, procurement or ERP release.

The native formulations follow the official OpenSees documentation for
[Timoshenko elements](https://opensees.berkeley.edu/wiki/index.php/Elastic_Timoshenko_Beam_Column_Element)
and [transient analysis](https://openseespydoc.readthedocs.io/en/stable/src/Canti2DEQ.html).

## Individual tools

| Command | Purpose |
|---|---|
| `prepare` / `generate` | Strict study/candidate contracts and source snapshots |
| `benchmark` | Concrete/steel, nonlinear pile, P-delta, friction and orthotropic/coupled-vehicle verification |
| `optimise` | Multi-seed Pareto evolution and equal-budget random comparison |
| `detail` | Actual-section CalculiX solids at three mesh sizes |
| `cost` | Complete quantities, controlled rate sources, crane/transport and lifecycle scenarios |
| `export-ifc` | Full span–pier–foundation solids and stable IFC product/quantity IDs |
| `archive` / `restore` | Immutable multipart checksummed storage and safe retrieval |
| `validate-data` | Separate calibration/holdout specimens and measurement uncertainty |
| `test-plan` | Candidate-specific laboratory/field protocols and unresolved owners/limits |
| `promotion-check` | Sealed impact proposal; existing structural release inspection when supplied |

Use `--help` for each command. Search `--resume` verifies its checkpoint and
replays the deterministic trajectory using saved results; modified inputs/code
or tampered files cannot silently reuse it. Reference retries consume the
registered attempt budget. Commercial totals remain null unless every scope
item and currency conversion is priced; quoted sources are hash-checked.

Actual-section solids are linear elastic, with explicitly idealised supports
and a bulk steel mass allowance. Nonlinear sections, pile response and friction
are separate diagnostics; they do not confer full-system nonlinear or physical
qualification. Unmeasured material matrices and range scenarios are labelled
research inputs. Hybrid bond/slip, calibrated cyclic degradation, scour and 3D
vehicle lateral interaction need project data and model selection.
