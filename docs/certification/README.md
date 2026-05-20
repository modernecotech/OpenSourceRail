# OSR type-certification pre-submission pack

**Target standard:** EN 62267 — Railway applications — Automated
urban guided transport (AUGT) — Safety requirements, GoA 4
(Unattended Train Operation).

**Complementary standards referenced:**

- EN 50126 — RAMS process for rail applications
- EN 50128 — Software for railway control and protection systems
- EN 50129 — Safety-related electronic systems for signalling
- EN 50657 — Software on board rolling stock (SIL-4 on T-ECU/S)
- EN 15227 — Crashworthiness requirements for rail vehicle
  bodies (Cat C-II, referenced from RFC 0008 §3)
- EN 45545 — Fire protection on railway vehicles (referenced from
  RFC 0008 §3)
- IEC 62443-4-2 — Cybersecurity, component-level (referenced from
  RFC 0017)
- CENELEC EN 50701 — Rail cybersecurity (referenced from RFC 0017)

**Scope of this pack:** establish that an OSR deployment — taking
the Samawah reference ([RFC 0003](../rfcs/0003-samawah-reference-deployment.md))
as the first-article instantiation — meets the GoA 4 requirements
of EN 62267 with sufficient evidence that a national safety
authority can review and (with deployment-specific additions)
grant type approval.

## Audience

- A national safety authority reviewing a type-approval
  submission for an OSR deployment.
- The deployment partner's safety assessor, preparing the
  deployment-specific dossier that wraps this pack.
- OSR project contributors, as the definition of "done" for
  the GoA 4 safety claim.

## Not in scope (deployment-partner responsibility)

- Deployment-specific RAMS targets (headway, availability,
  on-time performance — site dependent).
- Integration with the national regulator's own submission format
  (some authorities require specific document templates;
  translation from this pack is a per-deployment effort).
- Field-test evidence from the actual pilot (generated once the
  pilot line is commissioned).
- Operating-entity organisational competence (SIL management,
  safety-culture audit) — the deployment partner holds that
  evidence.

## Reading order

1. **[system-description.md](system-description.md)** — what the
   system is, its boundaries, operational envelope, and
   interfaces to the outside world.
2. **[safety-requirements.md](safety-requirements.md)** — the
   safety-requirements specification (SRS) derived from the
   EN 62267 functional scope.
3. **[hazard-log.md](hazard-log.md)** — hazards, their severity,
   frequency assumption, and mitigating controls.
4. **[evidence-register.md](evidence-register.md)** — complete
   inventory of verification evidence produced by the OSR
   project, indexed to the requirements + hazards it covers.
5. **[evidence-status.md](evidence-status.md)** — concise status
   matrix separating implemented, simulated, specified, and
   deployment-partner evidence.
6. **[release-gap-register.md](release-gap-register.md)** — release
   gates still open before a revenue-service type-approval submission.
7. **[compliance-matrix.md](compliance-matrix.md)** — EN 62267
   clause-by-clause traceability to OSR implementation.

## How this pack relates to the rest of the repository

Most of this pack is **synthesis**, not new engineering. Every
claim here is anchored to artefacts that already exist:

- SIL-4 safety properties → Kani harnesses in `crates/osr-*/src/kani_proofs.rs`
- SIL-4 safety properties → proptests in `crates/osr-*/tests/proptest_*.rs`
- GSN argumentation → TOML files in `docs/safety-case/gsn/`, closed
  against evidence by the `osr-safety-case` compiler CI gate
- Operational controls → per-role rules under `docs/operations/`
- RFCs (0001–0017) carry the design rationale
- Rust workspace + Python sidecars carry the implementation and
  generated-design verification gates

If any claim here cannot be traced to one of those artefacts, it's
a gap; file it as an issue against the evidence register.

## Document status

| Phase | Status |
|---|---|
| v1 — initial structure + SRS + hazard log + evidence register + compliance matrix | ✅ 2026-04-23 |
| v1.1 — per-clause compliance prose | next-iteration deliverable |
| v1.2 — reviewed by an independent safety assessor | deployment-partner scope |
| v2 — first-article field evidence | Samawah commissioning per [RFC 0027](../rfcs/0027-brownfield-pilot-asset-recovery.md) |

The open release gates are tracked in
[`release-gap-register.md`](release-gap-register.md). A gap is closed
only when the named evidence is in-tree or explicitly handed over to a
deployment partner's controlled safety dossier.

## Open questions for the reviewer

- **Residual-risk acceptance criterion.** EN 62267 does not fix a
  single numeric target; national authorities set thresholds. This
  pack presents the evidence; the reviewer sets the tolerance.
- **Historical-data equivalence argument.** Our safety case uses
  deterministic formal methods (Kani) and parameterised proptests
  rather than the several-million-revenue-hours approach of legacy
  fleets. This is the standard SIL-4 argument for software-
  intensive systems, but the reviewer may request additional
  sim-based evidence; see §5 of [evidence-register.md](evidence-register.md).
- **Wayside-intrusion gating on un-instrumented sections.** The
  v2 `section_available_to` gate permits sections with no
  `SectionIntrusion` verdict on record (RFC 0016 §5.2). For type
  approval of a fully-instrumented deployment, the reviewer may
  require the gate be tightened to fail-restrictive.
