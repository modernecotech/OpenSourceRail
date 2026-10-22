# Qualification and design closure worklist

179 applicable requirements, 100 supplied specification items, 8 obligation groups, 53 system IDs and six gates have explicit task/protocol coverage. 15 protocols and 576 dependency-ordered tasks are prepared. Accepted requirements and physical gates remain zero.

Every requirement retains its exact text/digest, dimensioned design deliverable, applicable measurement procedures and separate independent-review task. This register makes the remaining work actionable; it does not complete a train or qualify a physical test.

| Protocol | Gate | Evidence | Required cases |
|---|---|---|---:|
| Configuration, hazard, route and equal-service baseline | G0 | independent-review | 2 |
| Survey, ground, utilities, water and route-specific landing verification | G0 | site-record | 3 |
| Six-axis magnetic force, loss, R/L and thermal map | G1 | physical-rig | 6 |
| Hot/wet GFRP, adhesive, inserts and representative joints | G1 | physical-rig | 6 |
| Shared support/thrust, phase handover and repeated braking | G2 | physical-rig | 6 |
| Target SBC/MCU sensor-to-power timing and independent protection | G2 | physical-rig | 6 |
| Loaded multi-module support and fault containment | G2 | physical-rig | 6 |
| Precast transfer, lifting, transport, erection and connection proof | G3 | physical-rig | 7 |
| Sled/guideway moving-gap, joint and loss correlation | G3 | physical-rig | 6 |
| Hot/EOL support reserve, services, charging and containment | G4 | physical-rig | 6 |
| Complete vehicle mass/CG/inertia, joints, doors and structural proof | G4 | physical-rig | 6 |
| Full-load immobilisation, winch/tow, access and reopening | G4 | physical-rig | 5 |
| Full-scale accessible evacuation, chute and route landing demonstration | G5 | physical-rig | 7 |
| Six-car equal-capacity route and sustained fault/recovery demonstration | G5 | physical-rig | 6 |
| Supplier origin/price and manufactured first article process qualification | G5 | supplier-record | 4 |

Approved limits remain null until the responsible designer/operator/assessor derives and authenticates them before a run. Numerical study targets, manufacturer claims and open-map site estimates cannot be imported as qualified limits. Each protocol includes specimen definitions, real test steps, required channels/units, case coverage, criterion derivations and raw-data schema.

The importer checks serial/batch identity; source/configuration/procedure revisions; exact raw bytes and digest; finite, synchronised channels; calibration validity and uncertainty; case coverage; pre-approved guarded limits; independent witness and prerequisite dispositions. A trusted external signature verifier is required. Reviewer names, local hashes and self-reported success confer no acceptance. Simulated or synthetic data cannot impersonate physical rig records.

`passed-records` means an authenticated, internally consistent measurement screen is ready for an independent decision. All release flags remain false, and this package has no authority to issue physical or manufacturing release.

[Complete task graph and procedures](study.json.gz) · [Unexecuted evidence template](evidence-template.json) · [Unexecuted raw template](raw-template.json) · [Source and payload receipt](manifest.json)

References:

- [npl-force](https://www.npl.co.uk/products-services/force-pressure-mass-density/force-calibrations): Traceable force calibration and uncertainty, not a magnetic module pass limit
- [npl-composites](https://www.npl.co.uk/products-services/composites): Independent mechanical, thermal and nondestructive composite characterisation; no material allowables imported
- [npl-adhesive](https://eprintspublications.npl.co.uk/2423/1/MGPG28.pdf): Specimen preparation, conditioning, static/cyclic/creep adhesive test practice; actual process and Baghdad conditioning must be qualified
- [fhwa-pbes](https://www.fhwa.dot.gov/bridge/prefab/framework.cfm): Handling, access, transport, connection and erection planning; highway guidance is not railway load approval
- [fhwa-abc](https://www.fhwa.dot.gov/bridge/abc/docs/abcmanual.pdf): Prefabricated construction-stage and connection planning; project prestress, lifting and soil limits unresolved
- [linux-rtla](https://kernel.org/doc/html/latest/tools/rtla/rtla.html): IRQ/thread timing and hardware/OS noise diagnostics; application GPIO/sensor-to-power latency requires separate physical capture
- [thoms-chute](https://escape-chute.net/en/stationary-escape-chute/): Commercial application precedent only; no OpenSourceRail qualification, throughput or height approval
- [osaka-egress](https://www.osaka-monorail.co.jp/info/detail/434): Operator describes onboard chute/descender use under staff instruction after rescue transfer is difficult; no driverless evacuation equivalence
