# Independent linear static LIM field benchmark

Four bounded GetDP 3.5.0 comparisons use the exact 44,643-node motor mesh, 60 signed winding groups and imposed zero, archived-current, reversed-current and single-path basis sources. The linear steel permeability of 1000 is an unverified numerical hypothesis. Geometry is shared; GetDP independently assembles the field operator and source.

Research parent: `70eb0ba82c796bc3ec3c52dbdb1c64db15b0d337c64a021f5a5ed3956a28fdc5`; exact motor geometry: `be98f644c7c5117cb0423970c02501f234c3488689db8b0d017ef34dc6718dc5`. Execution took 51.43 seconds.

| Mathematical source | Static energy, J | Field comparison error | Energy comparison error |
|---|---:|---:|---:|
| zero | 0 | 0 | 0 |
| quarter-current | 0.033885498 | 1.07e-11 | 1.49e-12 |
| reversed-current | 0.033885498 | 1.07e-11 | 1.49e-12 |
| unit-path | 0.0037610686 | 2.11e-11 | 6.13e-12 |

**This is a static field subset, with no moving secondary, eddy-current, circuit, controller, thermal, force-map, journey or physical qualification.** The single-path mathematical source is not a permissible floating-neutral drive point. Moving-entry thrust remains negative and time convergence remains open in the [separate moving experiment](../moving-lim-method/README.md).

Potential, cell field, energy, source-work balance, boundary conditions, zero response, polarity and reciprocity are checked against the archived tables. Small comparison errors verify this shared-mesh numerical subset; they do not establish whole-domain convergence or actual material properties.

Portable verification reads recorded outputs without invoking GetDP or requiring the original executable path. The recorded tool checksum/version and producer epoch remain bound to the original receipts; executable availability is not rechecked. Derived diagnostics permit explicit floating-point verification tolerances of relative 1e-7 and absolute 1e-14, with absolute 1e-10 A for closed-source cancellation across reduction contexts; these are numerical checks, not physical acceptance limits.

[Assessment](assessment.json) · [Original inputs, outputs, logs and frozen sources](native-runs.tar.gz) · [Receipt](manifest.json)

Run `python -m engineering.design_search.lim_static_publication verify`.
