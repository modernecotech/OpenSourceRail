# OSR-MFG-001: Open factory execution and quality evidence

Version 1.0.0 · adopted 2026-10-11 · internal OpenSourceRail process standard.

This standard supplements [OSR-ENG-001](OSR-ENG-001.md) and
[OSR-ENG-002](OSR-ENG-002.md). It governs generated manufacturing routes,
travelers, material traceability, measurement decisions and commissioning
protocols. It does not certify an ISO quality system, approve a manufacturing
process, release a product or authorise railway operation.

[ISO 22163:2023](https://www.iso.org/standard/79427.html) and
[ISO 3834-2:2021](https://www.iso.org/standard/81651.html) identify railway and
fusion-welding quality scopes. OSR-ENG-001 supplies the applicable measurement,
fastener, datum, welding-procedure, NDT and material test references. Full
controlled clause review, amendments, material/process applicability and national
requirements remain project responsibilities.

| Rule | Mandatory internal requirement | Executable control |
|---|---|---|
| OSR-MFG-01 | Work shall identify configuration, part revision, physical serial/lot, work order, operator and independent inspector. | Traveler and measurement identity checks |
| OSR-MFG-02 | Material grade, certificate, shelf life, substitution and repair compatibility shall be controlled. | Material passport and lot/expiry checks; unknown released grade stays open |
| OSR-MFG-03 | Functional datums shall be common to fixture, part and inspection; workholding capacity is assessed separately. | Six-restraint rank and native locator checks; rank does not qualify clamps/load capacity |
| OSR-MFG-04 | Tolerance chains shall include signed dimensions, bounded tolerances and declared thermal offsets. | Worst-case interval; RSS only for supplied independent standard uncertainties |
| OSR-MFG-05 | Special processes shall use qualified procedures, competent personnel, released windows and complete traces. | Process-window duration/sampling checks; blank windows cannot pass |
| OSR-MFG-06 | Critical fasteners shall have per-joint/tool/revision traces; rework requires authority. | Torque/angle sample ordering, calibrated-range and rework checks; no preload inference from torque alone |
| OSR-MFG-07 | Measurements shall use valid calibration, recorded environment, uncertainty and an explicit decision rule. | Conservative expanded-uncertainty interval containment for declared limits |
| OSR-MFG-08 | Open NCRs, unperformed holds, reused unscoped measurements and stale revisions shall block review readiness. | Traveler predecessor, evidence and NCR checks |
| OSR-MFG-09 | Production forecasts shall distinguish planning times from released cure/dry windows and observed capacity. | Resource scheduling with wait times; missing actual durations remain unplanned |
| OSR-MFG-10 | Capability statistics shall not replace stability, distribution, measurement-system or individual inspection evidence. | Diagnostic Pp/Ppk; conditional Cp/Cpk requires explicit study records; no automatic threshold |
| OSR-MFG-11 | Automated lifecycle recovery shall preserve critical lockout and movement interlocks. | Offline fault campaign; actual safety control and GoA4 qualification remain separate |
| OSR-MFG-12 | Interfaces and work instructions shall remain portable, supplier-neutral and revision/hash bound. | JSON/CSV/Markdown/native CAD exports and reproducible package verification |

The measurement decision rule is an OSR internal conservative interval rule,
informed by [JCGM 106](https://www.bipm.org/en/doi/10.59161/jcgm106-2012).
It does not define a universal ISO consumer/producer risk. Selected projects must
approve its uncertainty coverage and suitability. Overlap with a limit requires
review; an unknown acceptance limit is never a pass.

[NIST capability methods](https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc16.htm)
inform the diagnostic implementation. Fifty independent suitable samples is a
screening policy, not an ISO qualification rule. Confidence, stability and
distribution evidence and acceptance thresholds remain project-defined.

Generated operations, source claims, fixture studies and offline fault tests are
design/protocol evidence. Only actual controlled records and the designated
authority can disposition physical work. These tools perform no ERP submission,
product release or live train-control action.
