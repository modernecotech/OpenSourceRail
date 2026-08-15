# Certification Release Gap Register

This register is the release-facing list of evidence still needed
before the current repository package can support a revenue-service
GoA 4 type-approval submission. It complements
[`evidence-status.md`](evidence-status.md): that page summarises
status by area; this page names the closure evidence expected for each
gap.

| Gap | Current in-tree state | Closure evidence |
|---|---|---|
| Independent safety assessment | Pre-submission pack is structured and traceable, but not assessor-reviewed | Named assessor review report, action log, and accepted residual-risk statement |
| Residual-risk acceptance | Hazards and mitigations are listed, but no national-authority threshold is applied | Deployment-specific ALARP / tolerability criterion signed by authority or assessor |
| Consensus refinement | TLA+ spec and Rust proptests exist, but no formal refinement proof connects them | Refinement argument or tool-backed proof from `SMRaft.tla` to `osr-consensus` behavior |
| Signed safety-log deployment evidence | Authenticated consensus ingress/commit verification and simulator fault-injection tests reject forged, altered, replayed, stale/future, unknown-issuer, metadata-mismatched, and category-downgraded proposals | Frozen deployment key registry, secure-element provisioning/rotation procedure, production-transport capture, and hardware-in-the-loop evidence showing only verified entries reach state derivation |
| Pilot hardware integration evidence | RFC 0019 COTS/SBC path and board-level specs exist; controlled pilot integration evidence is not frozen | Exact SKU BOMs, wiring/harness maps, connector maps, enclosure/mounting notes, power/thermal margins, SD-card image checksums, bring-up logs, safety-net bench tests, and commissioning records |
| Custom-board release evidence | Custom boards are optional for a first pilot and required only when a deployment chooses OSR-specific carrier, power, safety-I/O, or sensor-interface boards; KiCad, gerbers, and board BOMs are not released | For any custom-board deployment: KiCad projects, gerber zips, board BOMs, bring-up logs, safety-net bench tests, and DFM/DFT review |
| Rolling-stock structural evidence | Parametric envelopes and BOM exist; no production FEA or first-article structural tests | EN 15227 / EN 12663 / EN 13749 FEA reports plus weld/NDT records from first article |
| Door-system evidence | RFC 0023 defines the architecture; EN 14752 certification path remains open | Door operator drawings, actuator/lock/obstruction tests, EN 14752 notified-body route, integration tests |
| Obstacle/intrusion field evidence | Logic and simulations exist; no representative first-article sensor dataset | Calibration report, hot-weather/soiling/night/rain datasets, false-positive/false-negative analysis |
| Station charging and site energy | Planning-grade energy model exists | Site-specific solar yield, grid interconnect, charger thermal study, and utility approval package |
| Operations validation | Rulebook is drafted in English | Operator workshop minutes, translated deployment rulebook where needed, competence/training records |

These are not code-style TODOs. They are release gates for the first
deployment package.
