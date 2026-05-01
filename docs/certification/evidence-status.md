# Evidence Status Matrix

This matrix separates what is already evidenced in the repository from
what remains deployment or assessor work. It is not a safety approval;
it is a coherence map for the pre-submission pack.

| Area | Current repository evidence | Status | Next action |
|---|---|---|---|
| Movement authority non-overlap | `osr-interlocking` unit/proptest/differential tests; RFC 0004 | Implemented + tested | Add assessor-reviewed trace from hazards to tests |
| Consensus log safety | TLA+ model, `osr-consensus` simulation/proptests | Implemented + modeled | Refinement argument from TLA+ spec to Rust harness |
| Onboard obstacle detection | RFC 0015, `osr-obstacle-detect`, sim fault injection | Implemented + simulated | First-article sensor dataset and calibration report |
| Wayside intrusion detection | RFC 0016, interlocking gate, sim integration | Implemented + simulated | Pilot installation evidence on representative sections |
| Message authentication | `osr-crypto`, RFC 0017 design | Library implemented | Wire every consensus entry through signed envelopes |
| Hardware safety nets | RFC 0007 v2 specs and hardware docs | Specified | KiCad/Gerber/BOM release and bench test records |
| Rolling-stock mechanical concept | RFC 0008/0021/0022, `mechanical-py` STEP catalogue | Parametric reference | FEA, crashworthiness simulation, supplier drawings |
| Station charging energy | RFC 0002, generated city energy feasibility tables | Planning-grade | Site-specific solar yield, grid-tie, and charger thermal study |
| Operations rulebook | RFC 0013 and `docs/operations/` | Drafted | Operator review and local authority adaptation |
| Certification pack | `docs/certification/` and GSN claims | Pre-submission scaffold | Independent assessor review and evidence freeze |

The repo health gate (`scripts/repo-health.py`) guards generated design
coherence. It is deliberately not a substitute for EN 50126/50128/50129
assessment evidence.
