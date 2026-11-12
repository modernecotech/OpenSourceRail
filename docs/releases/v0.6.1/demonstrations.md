# v0.6.1 demonstrations

The published software verification examples use one fresh city calculation and two
existing source-pinned evidence sets. The physical and operational release
flags remain false in every example.

## Journey A — Samawah (fresh calculation)

1. Open the Workbench and load the mapped Samawah outline.
2. Record the displayed source packet, demand, headway and access assumptions.
3. Submit one baseline service request and inspect its fleet, energy assumptions,
   civil quantity classes and 14-scope cost result.
4. Repeat the identical request and confirm the same sealed result is reused.
5. Change peak demand from 4,000 to 9,000 passengers/hour/direction and confirm a distinct
   evaluation identity and visible cost/service differences.
6. Open the summary, result, manifest, performance, delivery-plan and disabled
   business-draft exports; run the independent result replay.

Run the browser verifier twice as described in the [quickstart](quickstart.md).
It writes machine-readable evidence outside the checkout, checks the bounded
artifact size and clean source tree, and invokes no native solver.

## Journey B — Baghdad (precomputed comparison)

Open the published Baghdad city atlas in the Workbench and inspect its
source-bound route/service and cost comparison. The frozen packet contains 14
lines and a calculated route sensitivity; keep generic demand, right-of-way
allowances and unsurveyed site inputs visible. Do not describe allowances as
survey quantities or vendor prices. Download the existing source-bound result
without recalculating Baghdad. The editable RustGIS ZIP endpoint is currently
held because its GIS and outline publication epochs differ; it is not part of
this release journey.

## Journey C — candidate research (precomputed evidence)

Open the declared passive steel-wheel development reference in the Workbench.
At the frozen v0.6.1 source commit, the Workbench candidate-portfolio selector is held and
hidden because its current dossier binding reports
`Current source changed: .github/workflows/development-baseline.yml`. Do not
describe the hidden selector as an available interactive comparison.

For the source-pinned research comparison, inspect the precomputed
[coupled-railway packet](../../design-engine/coupled-railway/README.md), its
`comparison.json.gz` and `manifest.json`. Compare the declared P1 station-LIM
case with P6 onboard-wheel-traction research as separate physical candidates.
This packet is verified only in its recorded historical source epoch; the
current `./osr design railway verify` command holds with
`Coordinated source epoch changed`.
The P6 record is definition research: it has no available-force map, its
propulsion model reports `model-development-required`, and its additional
installed mass and price remain unknown. Confirm candidate and evaluation IDs,
source epoch, tools and numerical limits in the packet. Do not transfer results
between candidates or promote either alternative to the integrated reference.

Verify the coupled comparison with
`python -m engineering.station_rail.retired_station_reference verify` from a
clean full-history checkout of the same commit. The verifier reads retained
packet bytes from their original Git source epoch; a blob-filtered sparse
evaluation checkout does not include those historical blobs. It does not
replay the calculation. The published braking source belongs to the
retained historical epoch recorded in
[`docs/archives/coupled-railway-source-epochs`](../../archives/coupled-railway-source-epochs/README.md);
the verifier checks retained source-pinned packets, but does not admit them as
current evaluations or braking evidence. No campaign or native solver is run
for this demonstration.

## Export and evidence locations

Journey A writes `journey-a.json`, screenshots and result artifacts under the
external output directory. Baghdad and candidate research records remain
source-bound to their committed manifests. Record their exact manifest,
candidate and evaluation IDs, plus the visible Workbench holds, for the frozen
candidate. A source-pinned archive check is not a fresh engineering evaluation.
