# OpenSourceRail v0.5 primary infrastructure adapter

The selected architecture is ferrite PM-biased active maglev, with onboard
windings/electronics, passive guidebeams, local manufacturing and Rust controls
on off-the-shelf SBCs. The [migration decision](../../docs/rfcs/0035-v05-primary-ferrite-maglev.md)
separates this primary development direction from engineering acceptance.

```bash
./osr                         # primary architecture and migration status
./osr build                   # build the control package and publish the study
./osr design run               # regenerate bounded calculations and review images
./osr design check             # independently regenerate and compare every output
./osr design verify            # verify current source/file checksums
./osr design release-check     # intentionally exits 3 while acceptance remains open
cargo test -p osr-maglev-control --all-targets
cargo run -p osr-maglev-control --example sbc_replay
tools/automation/osr-python -m pytest engineering/analysis/tests/test_ferrite_maglev.py
```

[Open the generated report](../../docs/design-engine/ferrite-maglev/reference/index.html).
It includes 4 mass variants, 12 cost configurations, 2 additional local-manufacture
budget targets, 16 normal/hot load-duty cases, 3 additional no-regen/90 km/h cases,
27 guidebeam geometry/span combinations and the specification requirement register.
The 5% hot uphill steady power envelope is a separate calculation. Section and
duty images are generated from these data, not synthetic engineering renders.

`workbook.py` imports literal cells with source addresses and a workbook hash;
it does not execute spreadsheet code or trust cached formula outputs. `model.py`
independently recalculates the supplied budgets and physical screens. The exact
comparator cost inputs are checked before comparison. `delivery.py` binds source,
input, runtime version and output hashes. Its checksum verification establishes
integrity, while `check` repeats the calculations. Neither is physical validation.

The stage is a development study. It supplies no nonlinear magnetic force map,
released coil/rail design, native maglev manufacturing CAD, accepted 6-DOF
stabilisation, physical I/O, target WCET, qualified brake/capture, actual component
mass closure or maglev city fleet/cost compiler. Missing capabilities are explicit
holds. A cheap budget target does not make a physically eligible design.

Old physical generators can be invoked through explicit `legacy` launcher paths.
Direct standalone v0.4 scripts and retained city/CAD/book outputs are comparator
tools; they cannot produce evidence for the new architecture by renaming it.
