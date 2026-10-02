# Evidence Status Matrix

This matrix separates what is already evidenced in the repository from
what remains deployment or assessor work. It is not a safety approval;
it is a coherence map for the pre-submission pack.

The [all-component assurance register](component-assurance-register.md) is the
authoritative item-level view: its generated passports use the same G0–G4
lifecycle while retaining route-specific evidence. This page summarises
system-level evidence without duplicating a count that can drift.

For closure criteria on each open item, see
[`release-gap-register.md`](release-gap-register.md).

| Area | Current repository evidence | Status | Next action |
|---|---|---|---|
| All-component assurance | The generated register covers every current engineering inventory item and configured business/supervision platform; every identity/source baseline is recorded | G0 baselined; G1–G4 open | Freeze deployment use, jurisdiction, classification, standards applicability, assessor and evidence plan item by item |
| Movement authority non-overlap | `osr-interlocking` unit/proptest/differential tests; RFC 0004 | Implemented + tested | Add assessor-reviewed trace from hazards to tests |
| Three-source onboard routing | `osr-onboard-routing` two-of-three selector, unit/proptests and simulator execution; selection cannot create authority | Implemented + simulated | Independent-source/common-cause analysis, HIL and network-loss field trials |
| Consensus log safety | TLA+ model, `osr-consensus` simulation/proptests | Implemented + modeled | Refinement argument from TLA+ spec to Rust harness |
| Consensus persistence and recovery | Versioned/checksummed stable-state envelope, atomic disk-full/partial-write behavior, fail-closed restore and deterministic crash/partition/clock/telemetry trace | Implemented + tested in process | Repeat on selected storage, processor, network and clock hardware; add power-cut/endurance/WCET evidence |
| Onboard obstacle detection | RFC 0015, `osr-obstacle-detect`, sim fault injection | Implemented + simulated | First-article sensor dataset and calibration report |
| Wayside intrusion detection | RFC 0016, interlocking gate, sim integration | Implemented + simulated | Pilot installation evidence on representative sections |
| Message authentication | `osr-crypto`, `osr-secbus`, authenticated `osr-consensus` ingress/commit consumer, simulator integration, and adversarial integration tests | Implemented + simulated | Freeze deployment key registry/provisioning and verify on the selected production transport/hardware |
| Hardware safety nets | RFC 0007 v2 specs, RFC 0019 DIY path, and hardware docs | Specified | Pilot integration pack, bench test records, and custom-board KiCad/Gerber/BOM only where custom boards are used |
| Rolling-stock mechanical concept | RFC 0008/0021/0022, `design/component-catalogue` source plus FreeCAD review artifacts | Parametric reference | FEA, crashworthiness simulation, supplier drawings |
| Integrated cabin/battery thermal control | `osr-hvac::integrated_thermal`, property tests and rolling-stock thermal template prioritise battery protection while isolating air/coolant circuits | Implemented + tested model | Supplier sizing, calorimeter/thermal-chamber, leakage, EMC and vehicle integration evidence |
| Cross-domain FMEA | `system-fmea.toml` supplies component/subsystem/system scenarios across mechanical, electrical, thermal, embedded software, civil and operations; the generator screens every current controlled train, station, civil and Rust inventory entry | Baseline + complete inventory screen | Close each deliberately open item-specific analysis with accountable owners/actions, supplier data, tests and field feedback |
| Digital Standards Thread | `digital-assurance.py` validates publisher-review deadlines, applicability inputs, control coverage, evidence paths/hashes and change impacts and emits Markdown/JSON on every build/test | Evidence-coherence gate | Freeze deployment clauses and close technical, physical, assessor and authority evidence without converting coherence into conformity |
| Engineering interchange gate | Seven analytical references plus LandXML/OSR-ALN, IFC identity/envelope and duty-cycle solver projections run deterministically | Implemented regression gate | Repeat live solver suite on a second controlled machine and retain signed environment manifest |
| Single track and recovery | Planner emits constrained segment track counts, passing loops and every-third-station recovery sites; corridor template constrains protected shunt operation | Planning implementation | Site alignment, operations proof, turnout/occupancy HIL, tow tests and recovery drill |
| Station charging energy | RFC 0002, generated city energy feasibility tables | Planning-grade | Site-specific solar yield, grid-tie, and charger thermal study |
| Operations rulebook | RFC 0013 and `docs/operations/` | Drafted | Operator review and local authority adaptation |
| Certification pack | `docs/certification/` and GSN claims | Pre-submission scaffold | Independent assessor review and evidence freeze |

The repo health gate (`tools/automation/repo-health.py`) guards generated design
coherence. It is deliberately not a substitute for IEC 62278-1,
EN 50716/50129
assessment evidence, hardware bench records, structural FEA, or
deployment-specific field evidence.
