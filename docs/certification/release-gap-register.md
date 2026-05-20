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
| Signed safety-log integration | RFC 0017 and crypto libraries exist; live consensus receive/apply path is not fully wired through signed envelopes | Integration tests showing forged, replayed, stale, and unknown-issuer entries are rejected before state derivation |
| Hardware release evidence | Board-level specs exist; KiCad, gerbers, board BOMs, and bench records are not released | KiCad projects, gerber zips, board BOMs, bring-up logs, safety-net bench tests, and DFM review |
| Rolling-stock structural evidence | Parametric envelopes and BOM exist; no production FEA or first-article structural tests | EN 15227 / EN 12663 / EN 13749 FEA reports plus weld/NDT records from first article |
| Door-system evidence | RFC 0023 defines the architecture; EN 14752 certification path remains open | Door operator drawings, actuator/lock/obstruction tests, EN 14752 notified-body route, integration tests |
| Obstacle/intrusion field evidence | Logic and simulations exist; no representative first-article sensor dataset | Calibration report, hot-weather/soiling/night/rain datasets, false-positive/false-negative analysis |
| Station charging and site energy | Planning-grade energy model exists | Site-specific solar yield, grid interconnect, charger thermal study, and utility approval package |
| Operations validation | Rulebook is drafted in English | Operator workshop minutes, translated deployment rulebook where needed, competence/training records |

These are not code-style TODOs. They are release gates for the first
deployment package.
