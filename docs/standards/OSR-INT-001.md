# OSR-INT-001 — configuration-bound integration evidence

Revision 1, 11 October 2026. OpenSourceRail internal engineering policy.
This is an original open project standard. It is not an ISO standard,
a supplier qualification or a railway conformity certificate.

1. A design change shall compile into physical component identities, occupied
   geometry, material assumptions, mass, CG, inertia, installed datums and typed
   interfaces. Equivalent envelopes and residual allocations shall be identified.
   The same mass shall appear once in the assembled system.
2. Retained input, configuration, implementation and output checksums shall be
   exact. Recomputed floating-point results may use only a named reproduction
   tolerance, with units and magnitude stated. Reproduction tolerance shall not
   alter an engineering limit, source identity or acceptance decision.
3. A passage claim shall show every represented wheel on both sides crossing
   the infrastructure. A stopped braking case shall retain its different scope.
   Time and spatial refinement shall be separate comparisons. An unstable or
   unsupported profile, joint, material or operating case shall remain failed.
4. An optimisation candidate shall use the shared design compiler. Battery
   module counts, packaging, mass, inertia and energy shall remain linked.
   Research shortlists shall be separate from designs that satisfy all adopted
   limits. Unknown capacities, costs or operating limits shall remain unknown.
5. Mounting loads shall preserve simultaneous force and moment vectors and
   their time, part identity and load-history provenance. Compliance, clearance,
   preload, contact, member stiffness and fatigue shall state their represented
   domains. A coupon or elastic shank model shall not qualify an installation.
6. Flexible models shall contain material sections, openings, joints and mounting
   load paths appropriate to their stated fidelity. Rigid modes, mass, numerical
   convergence and work-conjugate attachment transfer shall be verified.
   Reduced beam verification and physical shell modal correlation shall remain
   separately identified.
7. Electrical and thermal coupling shall account for each physical load once.
   Current sign and units shall be explicit at controller boundaries. SOC,
   temperature and ageing maps shall have retained provenance and bounded
   interpolation domains. Missing calibration shall prevent a calibrated claim.
8. Installed condition shall bind a serial, manufactured revision, configuration,
   quantity, units, uncertainty, measurement record and instrument calibration
   valid at measurement time and across the measured range. Condition revisions
   shall be independent of manufactured revisions. Updating condition shall
   invalidate dependent analyses before any release decision.
9. Installed civil studies shall address each relevant component and limit state,
   including construction stages. Lifecycle comparisons shall share duration,
   route, traffic, access and service scope. Unpriced manufacture, transport,
   erection, temporary works, access, inspection, maintenance, replacement,
   disruption or decommissioning shall prevent complete-cost ranking.
10. Station verification shall combine boarding, route capacity, accessibility,
    equipment and power outages, fire scenarios and responder interactions.
    Queue conservation alone shall not establish evacuation/fire tenability.
11. Native manufacturing and ERP evidence shall use project-scoped work orders,
    inspections, materials, tools, timestamps, independent review and NCRs.
    Simulation records shall be labelled. Payroll examples shall not invent
    statutory policy; depreciation schedules shall not imply capitalisation
    journals were posted.
12. Controller qualification shall bind an actual target, wiring, I/O electrical
    characteristics, timing, watchdog, power-cut and storage evidence. Software
    execution shall remain distinct from hardware-in-loop and physical release.
    Formal proofs shall retain complete checks, source bounds and resource
    limits; timeouts, tool errors and memory exhaustion shall not become passes.
13. Recovery acceptance shall bind a separately hosted destination, identity
    migration, writer cutover, resumed controllers/jobs and measured RPO/RTO.
    A same-host fresh-volume rehearsal shall state its narrower scope.
14. Supplier selection and deployment closure shall require actual quotes,
    rights, support and authority records. Numerical, administrative and physical
    acceptance shall be reported separately. No generated template shall count
    as an executed test or approval.

15. Each displayed civil instance shall identify its analysed domain, geometry,
    mass, material and datum equivalence or an explicit unresolved association.
    Structural analysis domains absent from the display shall be reported.
    Homogenised springs shall not qualify discrete fasteners or anchorages.
16. Search methods and seeds shall receive equal declared evaluation and time
    allocations, with separate finalist-confirmation time. Shared cache use,
    incomplete trials and budget exhaustion shall be visible. Refined results
    shall satisfy all adopted limits before a numerical feasibility claim;
    physical and authority qualification remain separate.

ISO 10007 configuration-management, ISO 23247 manufacturing digital-twin and
ISO/IEC 17025 laboratory practices inform the existing project standards thread.
Applicability, purchased clauses, local law and independent acceptance remain in
that thread. The [reviewed method sources](../../engineering/integration_programme/data/research.json)
include [NASA verification/validation](https://www.nasa.gov/reference/2-0-fundamentals-of-systems-engineering/),
[GENSYS wheel-profile verification](https://www.gensys.se/examples/kpf_wheel_profs.html),
[DfT station accessibility](https://www.gov.uk/government/publications/accessible-railway-stations-design-standards),
and [native ERP asset accounting boundaries](https://docs.frappe.io/erpnext/asset-depreciation).
These references inform method selection, rather than asserting project conformity.
