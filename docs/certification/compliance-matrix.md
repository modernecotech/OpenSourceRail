# Standards and evidence crosswalk

Generated from [the source register](standards.toml). Each row records a project question, the evidence available in OpenSourceRail and the work required for deployment review.

Publisher metadata reviewed **2026-11-24**. Next review due **2027-02-24**.

## RAMS-01 · Railway lifecycle and hazards

Shared selection method and revised Baghdad Airport study. [IEC 62278-1:2025](https://webstore.iec.ch/en/publication/68933) · [IEC 62278-2:2025](https://webstore.iec.ch/en/publication/79793) · [ISO/IEC/IEEE 15288:2023](https://www.iso.org/standard/81702.html)

**Risk.** Scope or a design change invalidates an earlier safety or operating assumption.

**Control objective.** Carry an identified system, operating conditions, requirements and open risks into each design decision.

**OSR evidence (digital study).** Requirement policy and the Airport register distinguish obligations, assumptions and evidence holds. The verification record identifies the inputs evaluated. [requirement_policy.py](../../engineering/design_search/requirement_policy.py) · [audit_register.py](../../cities/Baghdad/engineering/simulation/audit_register.py) · [audit-verification.json](../../cities/Baghdad/engineering/simulation/audit-verification.json)

**Open work for the system integrator and independent safety assessor.** Set project RAMS targets and hazard ownership. Allocate safety and integrity requirements and review accepted residual risk for the installed system.

## SIG-01 · Train protection and command/control

Baghdad powered-wheel station controls and software bench. [IEC 62425:2025](https://webstore.iec.ch/en/publication/68909) · [IEC 62290-1:2025](https://webstore.iec.ch/en/publication/83773) · [IEC 62267:2009](https://webstore.iec.ch/en/publication/6681)

**Risk.** A train moves while passengers are boarding or after trusted feedback is lost.

**Control objective.** Verify the station cycle and degraded responses across train and wayside boundaries.

**OSR evidence (software and test procedure).** The station bench specifies signals and fault cases. Its trace tests cover replay validation with simulated inputs. [STATION-BENCH.md](../../cities/Baghdad/engineering/controls/STATION-BENCH.md) · [test_bench_trace.py](../../cities/Baghdad/engineering/controls/test_bench_trace.py) · [lib.rs](../../crates/osr-safety-case/src/lib.rs)

**Open work for the train control integrator and independent safety assessor.** Measure target hardware timing, position and brake feedback. Exercise loss of authority, degraded operations, rescue and evacuation with the operator.

## SW-01 · Safety-related software lifecycle

Current Rust ATP, TCMS and door software. [IEC 62279:2015](https://webstore.iec.ch/en/publication/22781) · [EN 50716:2023](https://www.dinmedia.de/en/standard/din-en-50716/378381071)

**Risk.** A changed binary or configuration invalidates tested interlocks.

**Control objective.** Tie verification to source, tests and the deployed configuration.

**OSR evidence (software and test procedure).** Crate boundaries and pinned dependencies identify the software scope. Source-level and CI checks exercise software contracts. [Cargo.lock](../../Cargo.lock) · [lib.rs](../../crates/osr-atp/src/lib.rs) · [lib.rs](../../crates/osr-tcms/src/lib.rs) · [lib.rs](../../crates/osr-door-control/src/lib.rs) · [v06-software-rust.yml](../../.github/workflows/v06-software-rust.yml)

**Open work for the software assurance lead.** Agree the applicable software route, software requirements and integrity allocation. Review independence, tool and target baselines and hardware-in-the-loop records.

## ACCESS-01 · Boarding and door interfaces

Baghdad fitted-vehicle and prototype platform interface studies. [EN 14752:2025](https://www.dinmedia.de/en/standard/din-en-14752/392372313) · [IEC 62267:2009](https://webstore.iec.ch/en/publication/6681)

**Risk.** Passengers can be trapped, encounter an excessive boarding gap or be exposed to movement.

**Control objective.** Review door permissives, movement clearances and accessibility across the complete train-platform interface.

**OSR evidence (digital study).** Platform sweeps and the fitted-train review expose nominal clearances and items awaiting evidence. Boarding permissions are exercised by the station bench. [PLATFORM-SWEEP.md](../../cities/Baghdad/engineering/prototype/infrastructure/PLATFORM-SWEEP.md) · [vehicle-audit-guide.md](../../cities/Baghdad/engineering/simulation/vehicle-audit-guide.md) · [STATION-BENCH.md](../../cities/Baghdad/engineering/controls/STATION-BENCH.md)

**Open work for the vehicle and station integrators.** Apply local accessibility requirements. Test loaded movements, obstacle response and egress on fitted equipment and the surveyed platform.

## POWER-01 · Traction power isolation and return

Revised Baghdad Airport paired-feed and radial traction studies. [IEC 62128-1:2013](https://webstore.iec.ch/en/publication/6496)

**Risk.** An isolated section remains energised or access exposes people to hazardous touch voltage.

**Control objective.** Identify the live paths, protection interfaces and evidence needed to isolate and maintain the railway.

**OSR evidence (digital study).** The audit maps outages to service and collects equipment return data. The voltage screen covers collectors, with electrical safety evidence still due. [AUDIT-RESULTS.md](../../cities/Baghdad/engineering/simulation/AUDIT-RESULTS.md) · [test_audit_power_return.py](../../cities/Baghdad/engineering/simulation/test_audit_power_return.py) · [audited-enquiry.receipt.json](../../cities/Baghdad/engineering/simulation/audited-enquiry.receipt.json) · [audited-enquiry-radial30.receipt.json](../../cities/Baghdad/engineering/simulation/audited-enquiry-radial30.receipt.json)

**Open work for the utility and traction protection engineer.** Obtain source and fault data. Verify earthing, return paths, touch voltage, protective clearing, isolation and emergency access at site.

## CIV-01 · Structural verification and erection

Baghdad viaduct family and erection comparison. [EN 1990 series (deployment edition)](https://eurocodes.jrc.ec.europa.eu/EN-Eurocodes/eurocode-basis-structural-design)

**Risk.** A girder, bearing, foundation or temporary lift fails under the governing site or train load.

**Control objective.** Carry governing loads and working-life assumptions into structural checks and construction methods.

**OSR evidence (digital study).** The family comparison tests span alternatives, vehicle loading, foundation assumptions and erection scope. [family_comparison.py](../../cities/Baghdad/engineering/mechanical/civil/family_comparison.py) · [SPAN-FAMILIES.md](../../cities/Baghdad/engineering/mechanical/civil/SPAN-FAMILIES.md) · [AUDIT-RESULTS.md](../../cities/Baghdad/engineering/simulation/AUDIT-RESULTS.md)

**Open work for the civil designer and independent checker.** Select the local structural basis, applicable action and material codes and National Annex. Verify geotechnical conditions, fatigue, detailed prestress and lift conditions.

## QMS-01 · Supplier, manufacturing and inspection records

Baghdad first-article planning and corrected supplier enquiry. [ISO 9001:2026](https://www.iso.org/standard/9001) · [ISO 22163:2023](https://www.iso.org/standard/79427.html)

**Risk.** An offer, manufactured part or inspection record applies to a different design issue.

**Control objective.** Carry quantity, revision, ownership and inspection points from the enquiry into purchasing and production.

**OSR evidence (process and sample records).** Factory routes, matched enquiry issues and the ERPNext handoff specify evidence for supplier comparisons, work orders and inspection. [FACTORY-SPECIFICATION.md](../../cities/Baghdad/engineering/prototype/FACTORY-SPECIFICATION.md) · [audit_packet_evidence.py](../../cities/Baghdad/engineering/simulation/audit_packet_evidence.py) · [audit_erpnext.py](../../cities/Baghdad/engineering/simulation/audit_erpnext.py) · [audited-enquiry.receipt.json](../../cities/Baghdad/engineering/simulation/audited-enquiry.receipt.json)

**Open work for the buyer and manufacturer quality leads.** Audit actual supplier controls, competence, special processes, nonconformance and production records. Agree how the railway standard's dated ISO 9001 reference applies.

## ASSET-01 · Asset history and renewal

ERPNext maintenance pilot and revised Baghdad Airport cost study. [ISO 55001:2024](https://www.iso.org/standard/83054.html)

**Risk.** An asset loses its identity or its required inspection, replacement or renewal funding.

**Control objective.** Keep the installed serial, maintenance history and lifecycle obligations accessible to the operator.

**OSR evidence (process and sample records).** The pilot demonstrates serial history. The corrected cost study identifies renewal scope and the timing of owner costs. [README.md](../../docs/operator-review/screens/README.md) · [field_operations.py](../../deployment/erpnext/apps/osr_erpnext/osr_erpnext/field_operations.py) · [audit_feeder_cost.py](../../cities/Baghdad/engineering/simulation/audit_feeder_cost.py)

**Open work for the operator asset manager.** Agree asset-management objectives, owner responsibilities, maintenance intervals and as-installed information. Demonstrate the process on operator records.

## BIM-01 · Information handover and IFC exchange

Operator review IFC4 model examples, each on its registered candidate. [ISO 19650-1:2018](https://www.iso.org/standard/68078.html) · [ISO 16739-1:2024](https://www.iso.org/standard/84123.html)

**Risk.** The buyer or maintainer imports the wrong model revision or misreads its quantities.

**Control objective.** Exchange a model with identifiable occurrences, source revisions and a declared information scope.

**OSR evidence (digital model).** The twin register identifies candidates, occurrence counts and export hashes. The showcased IFC4 exports are an exchange example within the ISO 16739 standards family. [model-register.json](../../docs/operator-review/twins/model-register.json) · [baghdad.ifc](../../docs/operator-review/twins/baghdad.ifc) · [core.ifc](../../docs/operator-review/twins/core.ifc)

**Open work for the project information manager.** Set information requirements and validation rules. Verify the required IFC edition, exchange view and as-built handover with the recipient.

## LAB-01 · Test evidence and calibration

Baghdad station bench and first-article qualification preparation. [ISO/IEC 17025:2017](https://www.iso.org/standard/17025)

**Risk.** A replay or measurement is attributed to the wrong article, instrument or test boundary.

**Control objective.** Record the tested article, approved method and limit, instrument calibration and raw results.

**OSR evidence (software and test procedure).** The bench procedure and ERPNext qualification gate specify evidence intake and reviewer responsibilities. [STATION-BENCH.md](../../cities/Baghdad/engineering/controls/STATION-BENCH.md) · [bench_trace.py](../../cities/Baghdad/engineering/controls/bench_trace.py) · [qualification.py](../../deployment/erpnext/apps/osr_erpnext/osr_erpnext/qualification.py)

**Open work for the test lead and competent laboratory.** Agree methods, uncertainty and acceptance limits. Obtain authenticated results for the exact article from a laboratory with the required scope.
