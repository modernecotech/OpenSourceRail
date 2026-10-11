# OpenSourceRail trainset improvement and industrialisation plan

Revision 1 · 2026-10-11 · implementation and verification programme.

The programme expands design, materials, assembly, production and quality using
the existing product tree, shared train definition and factory release packages.
It will deliver executable planning, inspection and commissioning tools with
retained evidence. Physical process qualification, supplier release and railway
approval remain separate deliverables requiring actual facilities and measurements.

## Evidence and interpretation

The requested [Railway-News article](https://railway-news.com/crrc-celebrates-production-of-first-fully-automated-train-for-hangzhou-metro/)
was published on 12 May 2026. [CRRC's primary account](https://www.crrcgc.cc/en/2026-04/29/article_2026042916024714810.html)
describes a Line 12 train completed on 17 April 2026. It identifies automated
lifecycle functions, redundant critical subsystems, obstacle/running-gear
monitoring, permanent-magnet traction and passenger comfort improvements.
Its reported energy-saving objective is a manufacturer/project claim; OSR will
require a defined duty cycle and measured baseline rather than adopt that number.
The AH specification and vendor implementation are not an open design recipe.

| Source | Practice to adapt | OSR interpretation |
|---|---|---|
| [Alstom smart manufacturing](https://www.alstom.com/sites/alstom.com/files/2025/04/24/Alstom_Whitepaper_SmartManufacturing_EN.pdf) | Skilled process teams, repeatable special processes, monitored equipment and lean flow | Qualified manual/semi-automatic work first; add robots only after repeatability, access and throughput justify them |
| [Alstom digital maintenance](https://www.alstom.com/press-releases-news/2024/4/different-and-smart-approach-maintaining-trains) | Digital instructions and connected torque records | Tool-neutral per-joint records and offline instructions, with revisions, calibrated tools and independent review |
| [Siemens railcar coating schedule](https://resources.sw.siemens.com/de-DE/case-study-increase-efficiency-and-productivity-with-digital-scheduling/) | Coordinate coating resources, drying and QA timing | Resource-constrained assembly planning; material-specific wait times must be explicit |
| [Siemens measurement quality](https://references.siemens.com/en/reference/32785?id=32785) | Associate dimensional inspection with measurement-room conditions | Retain temperature, calibration and uncertainty with measurements |
| [Alstom environmental design](https://www.alstom.com/company/sustainability/environment) | Consider energy, recyclability and lifecycle effects | Compare mass, stiffness, repair, fire/corrosion evidence and lifecycle data together |
| [NIST capability methods](https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc16.htm) | Capability requires suitable data and process assumptions | Calculate diagnostic statistics; withhold capability approval without stability, measurement-system and distribution evidence |
| [BIPM JCGM 106](https://www.bipm.org/en/doi/10.59161/jcgm106-2012) | Measurement uncertainty affects conformity decisions | Use an explicit project-approved decision rule; offer a conservative interval guard as an internal method |
| [ISO 22163](https://www.iso.org/standard/79427.html), [ISO 3834-2](https://www.iso.org/standard/81651.html) | Railway quality and welding quality requirements | Retain applicability, controlled editions, competence and qualification evidence; no certification inferred from generated records |

## OpenSourceRail constraints

Preserve the repository's [path-based licensing](../../LICENSE.md): Apache-2.0
software, CERN-OHL-S hardware and CC-BY-SA documentation. Manufacturer sources
remain references under their own terms. Do not redistribute proprietary CAD,
process recipes or AH train specifications as OSR designs.

Keep interfaces, part identity, inspection definitions and exports open in JSON,
CSV, Markdown and native CAD. Each supplier substitute must pass the same
functional interface and evidence requirements. Support local fixtures, common
fasteners, repairable modules, documented removal paths and offline work
instructions. Do not require a manufacturer's cloud or proprietary torque tool.

The detailed factory packages describe the LM3 reference. Transferring their
methods to another family requires its own length/datums, loading, drawing and
supplier compatibility checks; the six-car planning generator is not that release.
The existing 9.13 s contact-domain rejection remains an explicit operating gate.

## Execution packages

| ID | Work package | Repository implementation | Completion evidence |
|---|---|---|---|
| IM-01 | Source-backed design expansion | Feature/requirement register binds automation, redundancy, running-gear health, traction, HVAC, doors and acoustic interfaces to catalogue IDs | Every feature has source, limits, part/interface ownership, verification and unresolved evidence |
| IM-02 | Material and energy trade-offs | Material qualification passports; geometric mass/stiffness/thermal screening and energy balance tools | Independent formula tests; no qualified selection without fire, fatigue, corrosion, repair and supplier evidence |
| IM-03 | Assembly quality by design | Datum fixture constraint checks, tolerance stacks, per-instance assembly operations and hold points | Six independent fixture restraints; worst-case fit checks; cycles/unknown predecessors rejected |
| IM-04 | Production execution | Open travelers and resource scheduling with explicit cure/dry waits, competencies and process requirements | Capacity/predecessor tests; immutable work-order/configuration/evidence bindings |
| IM-05 | Quality at source | Calibration/uncertainty-aware measurement decisions, material genealogy, torque/process traces, NCR blocking and diagnostic capability statistics | Negative tests for stale revisions, expired tools, missing evidence, reused identities and unresolved defects |
| IM-06 | Automated commissioning contracts | Offline lifecycle/interlock/fault-injection model and commissioning protocols | Door/obstacle/brake/depot/washing/reset invariants tested; no live control or GoA4 qualification claimed |

The implementation will reuse the existing factory packages, manufacturing
controls, first-article inspection plan, product material/process specifications
and shared engineering instance IDs. Generated plans and blank travelers cannot
serve as execution evidence. Factory acceptance requires actual controlled
documents, physical records, independent quality review and the designated authority.

## Pilot sequence and physical work

1. **Battery installation and equipment mounts:** kit by joint/lot, verify mating
   datums, validate tolerance/thermal clearances, record fastener stacks and tool
   traces, inspect routing/isolation and perform approved load/leak/electrical tests.
2. **Representative bogie:** material receipt, qualified weld/fixture sequence,
   distortion and NDT, axlebox fit and bearing trace, suspension settings, brake
   and sensor installation, then an independently witnessed rolling/loaded test.
3. **Carbody/door/HVAC bay:** survey portals/curbs, qualify composite/bond/seal
   processes, verify doors and drains, assess heat/noise/fire evidence, and
   demonstrate sequential removal and interchangeable replacement.
4. **Full train:** close genealogy and configuration, execute integration/fault
   protocols, then complete supported wheel–rail/service, braking, thermal,
   comfort and safety qualification with physical holdouts.

Record first-pass yield, rework by defect cause, scrap/yield, calibration failures,
trace completeness, measured cycle time, WIP and replacement time. Establish
baselines before claiming savings. Automation investment follows repeatability
and measured production demand; avoid transferring another factory's robot count,
cycle times or quality claims to OSR.

## Acceptance and execution reporting

The repository implementation is complete when IM-01 through IM-06 are callable,
their generated products reconcile with existing identities, their tests and
demonstrations are retained, and the review states the remaining physical work.
Executable protocol/software completion is distinct from train or factory
qualification. Report each package as implemented, verified in software,
awaiting supplier/process data, or awaiting physical validation.
