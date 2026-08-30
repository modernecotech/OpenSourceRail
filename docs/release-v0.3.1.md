# OpenSourceRail v0.3.1

v0.3.1 is the corrective patch for clean-checkout failures discovered after
v0.3.0 was published. It does not change the product or certification boundary.

## Corrections

- Python and browser jobs install one pinned IFC runtime, including the
  schedule and EXPRESS-validation dependencies used at runtime.
- All 266 acceptance reports link only to tracked compact asset registers and
  manifests; reproducible high-volume local outputs are named without broken
  GitHub links.
- CI checks that the report links and IFC dependency source cannot drift.
- Kani CI proves explicit fast ATP and interlocking properties. Larger
  topology-backed proofs remain controlled open evidence instead of repeatedly
  timing out while appearing to be a release gate.

The complete Rust, Python/generated, browser and bounded Kani workflows passed
before tagging. Physical qualification, supplier freeze, independent safety
assessment and deployment approval remain external gates.
