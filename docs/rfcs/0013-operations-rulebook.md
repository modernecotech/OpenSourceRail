# RFC 0013 — Operations Rulebook

**Status:** Draft — planning only
**Date:** 2026-04-22
**Depends on:** [RFC 0008 Rolling-Stock Reference Design](0008-rolling-stock-reference-design.md), [RFC 0009 Track Design Standard](0009-track-design-standard.md), [RFC 0010 Station Design Standard](0010-station-design-standard.md), [RFC 0011 Civil Infrastructure Design Standard](0011-civil-infrastructure-design-standard.md), [RFC 0012 Switches & Crossings](0012-switches-and-crossings.md)

## 1. Summary

Every OpenSourceRail deployment inherits one **baseline operations
rulebook** — the standing rules for drivers, dispatchers, station
staff, and maintenance workers. The rulebook is deliberately
*short* (target ≤ 60 pages in the rendered PDF) and *shared across
deployments*. Operators adapt it for national regulatory overlays
but do not re-invent it.

This RFC fixes the rulebook's **table of contents** and the
**governing rule-granularity principle**. The rule text itself
lives in markdown under `docs/operations/` and is owned by a
standing committee once the project has one; until then, the
project maintainer ratifies additions.

## 2. Non-goals

- **Not a national regulatory document.** Every country that
  adopts OSR has a national rail safety authority (NRSA or
  equivalent) that must accept the rulebook. This RFC produces a
  baseline that a deployment's local legal counsel adapts.
- **Not a driver training manual.** Training content comes from
  the rulebook, but the pedagogy (lesson plans, sim scenarios,
  exam questions) is a per-deployment deliverable handled by
  workforce materials ([`lib/templates/workforce.toml`](../../lib/templates/workforce.toml)).
- **Not a safety-case evidence file.** The rulebook is an
  operational artefact; the safety case ([`docs/safety-case/`](../safety-case/))
  references rules as supporting evidence, not the other way
  around.
- **Not an incident-response playbook.** Playbooks are scenario-
  specific and owned per-deployment (fires, passenger illness,
  derailment, signal failure); this RFC specifies the *categories*
  each playbook must exist for, not the specific response.

## 3. The simplicity principle

Every rule in the rulebook must pass this test:

> *A new driver who has never seen this system before can read
> the whole rulebook in one morning and have an accurate enough
> mental model to operate safely under supervision by the end
> of the day.*

This means:

- Every rule is one sentence, one decision. No compound rules.
- Every rule has exactly one author (the project maintainer
  until the standing committee exists).
- Every rule is numbered; operators cite rules by number in
  incident reports.
- Every rule has a *why*: a short justification paragraph. No
  rule is an unexplained ritual.

The target is a ≤ 60-page PDF. Rail industry rulebooks that hit
200 + pages are artefacts of 150 years of accretion — we're not
accruing that.

## 4. Table of contents — one section per role

The rulebook is organised by **role, not by scenario**. A driver
reads one section; a dispatcher reads another; the sections
overlap only where the roles interact.

### 4.1 Dispatcher rulebook (target ≤ 15 pages)

| Section | Scope |
|---|---|
| S1 | Shift start — OCC login, fleet inventory check, schedule ready |
| S2 | Routine dispatching — route grants, timetable adherence, headway maintenance |
| S3 | Incident handling — single-train fault, section unavailable, mass-casualty |
| S4 | Weather and environmental — dust storms, heatwave, flood warning |
| S5 | Maintenance interlock — work-on-track grants, blocking a section from revenue |
| S6 | Shift end — handover, outstanding-event log, system state summary |
| S7 | Intrusion response (RFC 0016) — track-patrol dispatch, return-to-service gating, sustained-Unknown escalation |

### 4.2 Station staff rulebook (target ≤ 10 pages)

| Section | Scope |
|---|---|
| T1 | Station opening — power up, PIS check, fare-gate test |
| T2 | Passenger boarding — platform supervision, PSD status, wheelchair assist |
| T3 | Passenger incidents — medical, fare dispute, unattended item |
| T4 | Fare enforcement — inspector on-board, non-payment, appeal |
| T5 | Station closure — evacuation, power down |

### 4.3 Maintenance worker rulebook (target ≤ 10 pages)

| Section | Scope |
|---|---|
| M1 | Depot safety — hazard awareness, PPE, lone-worker protocol |
| M2 | Work-on-track authorisation — formal blocks, protection signals, access to active ROW |
| M3 | Routine track inspection — walking the line, visual checks, GPM/RECD recording-car cadence (per RFC 0009 §9) |
| M4 | Switch maintenance — blade lubrication, detection-sensor cleaning, 30-day check |
| M5 | Fleet maintenance at depot — inspection intervals (daily / 7-day / 30-day / overhaul) |
| M6 | Incident site access — derailment response, fire site, crane operations |
| M7 | Wayside sensor maintenance (RFC 0016) — 30-day walkthrough, post-weather inspection, sensor replacement + calibration |

### 4.4 Control-centre rulebook (target ≤ 5 pages)

| Section | Scope |
|---|---|
| C1 | OCC watch roles — dispatcher, supervisor, engineer-on-call |
| C2 | Communications — radio discipline, PA authority, external-party notifications |
| C3 | Shift handover — written log, outstanding items, emergency-on-call list |

**Total target:** 40 pages across four sections.

## 5. Degraded-mode operations — the important part

Modern CBTC metros routinely run in "normal mode" (full ATO under
a fresh MA) and have short, mission-critical manual-restoration
procedures when the signalling degrades. OpenSourceRail keeps
exactly three degraded modes:

| Mode | Trigger | Operator action |
|---|---|---|
| **M1 — Automated restricted MA** | ATO is healthy and ATP can enforce a shortened MA | OCC authorises reduced-speed automatic movement; ATP remains fully active and speed is capped at 80 % of normal. |
| **M2 — Controlled stop** | Consensus cannot issue a trustworthy MA | Every affected train remains stopped while OCC establishes a work block and restores the signalling quorum. No written order may bypass ATP. |
| **M3 — Protected depot shunt** | Movement is required inside an isolated depot worksite | An authenticated local maintenance pendant requests automatic movement at ≤ 15 km/h under ATP, direct CCTV observation, and a locked work zone. |

No intermediate modes. No "sort-of-ATP" states. Either the safety
envelope holds (modes M1 / M3) or the train remains stopped (mode
M2). This is a forcing decision: ambiguous degraded modes are
the dominant cause of metro-world incidents.

## 6. Weather-dependent rules

Target regions routinely experience weather conditions that
challenge legacy rolling stock:

- **Dust storm (haboob):** visibility < 100 m → automatic
  speed cap at 50 % (`osr-ato` enforces). Dispatcher issues a
  network-wide speed restriction at the OCC. Passenger
  announcements via `osr-pis-onboard`. See also
  [`lib/templates/climate-adapters.toml`](../../lib/templates/climate-adapters.toml).
- **Heatwave (> 45 °C sustained):** rail-expansion risk triggers
  a pre-emptive 15 % speed cap on `mainline-mixed` and
  `standard-metro` presets with continuous-welded-rail. Switch
  detection sensors recalibrate at dawn.
- **Flooding:** any rainfall > 50 mm / h triggers immediate
  inspection of at-grade segments; the dispatcher can
  preventively block sections via `osr-interlocking`'s
  maintenance-override. Elevated segments per RFC 0011 §5 are
  unaffected by surface flooding — deliberate design bet.
- **Lightning:** nearest-strike distance < 2 km → Cat.22 5G
  backhaul and LoRa backhaul are both watched for outage; if
  both fail for > 10 s the operator notifies the OCC and
  cooperates with `osr-atp`'s default fail-restrictive MA.

## 7. Incident categorisation

Every incident fits one of six categories. This drives the
notification chain and the regulatory report:

| Category | Example | Dispatcher action |
|---|---|---|
| **I1 — fleet self-recovery** | Door interlock fault on a single train, resolved at next terminal | Log in event recorder; notify depot; no regulatory report. |
| **I2 — service disruption** | Single-train immobile; next train coupled to rescue it | Passenger PA, timetable recovery plan; 24h incident report. |
| **I3 — short safety event** | Emergency brake triggered by spurious trip; no injury | Log, investigate root cause, 72h report. |
| **I4 — passenger injury** | Slip, fall, medical emergency on board | Medical call, depot handover; formal incident report to NRSA within 7 days. |
| **I5 — collision / derailment** | Train-to-train, train-to-obstacle, train off-rail | Full network shutdown of affected line; NRSA notification within 2 hours; incident-site preservation. |
| **I6 — mass-casualty / fire** | Onboard fire not extinguished, large-scale passenger injury | Immediate evacuation protocol; emergency services; NRSA + national media escalation. |

The categories map directly to `osr-event-recorder` tags, so the
post-incident analysis starts from the same data the categories
describe.

## 8. Training and recurrent qualification

- **Initial driver qualification:** 4 weeks classroom + 2 weeks
  simulator + 4 weeks supervised revenue service. Final
  qualification exam in written + simulator + on-road segments.
- **Recurrent:** 2 days refresher every 12 months + 1 simulator
  session per quarter.
- **Degraded-mode drills:** every driver runs modes M1 / M2 / M3
  in the simulator every quarter. The `osr-sim` sim is the
  primary training platform.
- **Dispatcher qualification:** 8 weeks OCC-side classroom +
  simulator + supervised desk time.
- **Maintenance:** role-specific certification per EN 50126 / per
  national NRSA rules.

Training content is a deployment deliverable; this RFC fixes the
minimum hours + structure.

## 9. Auto-gen implications

The rulebook does not directly feed the corridor-generation
pipeline — but it does feed two outputs:

1. **Depot capacity:** `osr-sim`'s fleet-sizing needs to include
   enough spare trains for the rulebook's degraded-mode
   operations. A deployment with 10 trainsets on rostered revenue
   needs ≥ 1 spare in depot for maintenance (M5) and ≥ 1 cold-
   reserve for I-category incidents. See RFC 0014 §4 for the
   formula.
2. **Workforce sizing:** from
   [`lib/templates/workforce.toml`](../../lib/templates/workforce.toml),
   with the rulebook's shift-structure (§4.5) as the envelope.

Both are parametric in the rulebook, so changing the rulebook
updates both; the emitter v3 work wires this in.

## 10. Pitfalls and decisions

- **One rulebook across deployments is a big bet.** Legacy
  metros each have their own 200-page rulebook; consolidating to
  one is the simplicity gain. National NRSAs will initially
  resist. The counter: the *process* of NRSA approval works on a
  per-document basis, not per-system basis — a shorter document
  approves faster. The operator carries the regulatory overlay
  in a thin appendix.
- **Six incident categories, not more.** Operators unused to
  this regime sometimes want a I7 or I8 for niche scenarios. We
  absorb niche scenarios into the existing six rather than
  proliferate.
- **Paper written orders are allowed in mode M2.** This is not
  anti-digital — paper is explicitly the fallback when the
  digital system degrades. Written orders remove ambiguity about
  authority when the digital system can't issue it. Rare enough
  that the paperwork tax is tiny.
- **No "caution mode" between M1 and M2.** Legacy metros have
  a smorgasbord of half-ATP-half-manual modes; every one is a
  source of operator confusion. We commit to the hard boundary.
- **≤ 60 pages is a hard target.** The rulebook is reviewed on
  every minor-version bump; if it exceeds 60 pages, something
  gets cut. Adding text is easier than subtracting.

## 11. Rollout

| Phase | Deliverable | Dependencies |
|---|---|---|
| **v0** | This RFC ratified | — |
| **v1** ✅ | `docs/operations/` scaffold with per-role stub files for dispatcher, station staff, maintenance, and control-centre roles, each with scope + cross-refs + proposed rule outline (done 2026-04-22) | v0 |
| **v2** ✅ | Full unattended-operations rulebook drafted across all four role families. Every rule is one sentence + a `Why:` paragraph, cross-referenced to the relevant crate and safety-case solution. Practising-operator review is v2.1 per-deployment work. | v1 |
| **v3** | NRSA submission pack for Samawah (rulebook + safety case cross-reference) | RFC 0003 §5, v2 |
| **v4** | `osr-sim` scenario library covering every degraded-mode scenario for operator refresher training | v2 |

## 12. Relationship to existing work

- [`lib/templates/workforce.toml`](../../lib/templates/workforce.toml)
  — shift-structure + headcount inputs. v3 of this RFC aligns
  the two documents.
- [`lib/templates/service-hours.toml`](../../lib/templates/service-hours.toml)
  — service hours drive the rosterable workforce; the rulebook
  sets the rostering envelope.
- [`docs/safety-case/`](../safety-case/) — references specific
  rulebook rules as "solution" evidence for goals around fail-
  restrictive operation, evacuation readiness, and training
  competence. GSN goals for "operational fail-restrictive
  behaviour" land in v4.
- [`crates/osr-occ`](../../crates/osr-occ/) — the dispatcher's
  OCC UI embeds the dispatcher rulebook's decision-support
  prompts. Software change in v3.

## 13. Open questions

1. **Bilingual rulebooks.** Every target-region deployment
   operates in at least one local language plus English. Do we
   maintain both upstream? v2 commits on this: likely yes, with
   English as the canonical and translations as separate
   branches in `docs/operations/<lang>/`.
2. **Printable-PDF vs living-document.** Rail NRSAs typically
   want a static PDF they can archive. The project wants a live
   document. Compromise: every minor-version bump produces a
   sealed PDF, and the commit hash is the canonical reference.
3. **Simulator-based competence testing.** `osr-sim` can
   evaluate driver actions against MA envelope in software. Can
   NRSAs accept simulator certification in lieu of on-road
   supervised hours? Per-country, probably not at v1.

## 14. Done criteria

- [x] Table of contents per role (§4)
- [x] Degraded-mode operations (§5)
- [x] Weather rules (§6)
- [x] Incident categorisation (§7)
- [x] Training envelope (§8)
- [x] Auto-gen implications (§9)
- [x] Pitfalls (§10)
- [x] Rollout ordered (§11)
- [x] Relationship to existing work (§12)

The next session picks up at **v1 — `docs/operations/` scaffold**,
short editorial PR that seeds the per-role files. Actual rule
text lands in v2.
