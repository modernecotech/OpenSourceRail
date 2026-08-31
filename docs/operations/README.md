# OpenSourceRail — Operations Rulebook

This directory holds the rule text referenced by
[RFC 0013](../rfcs/0013-operations-rulebook.md). Every rule sits
inside the one-sentence-one-decision style the RFC commits to.

**Target length, rendered PDF: ≤ 60 pages.** If the full compiled
book exceeds that, something gets cut before anything is added.

## Layout

| Path | Audience | RFC 0013 section |
|---|---|---|
| [`dispatcher/`](dispatcher/) | OCC dispatcher | §4.1 (S1–S7) |
| [`station-staff/`](station-staff/) | Station agent / inspector | §4.2 (T1–T5) |
| [`maintenance/`](maintenance/) | Depot + MOW worker | §4.3 (M1–M7) |
| [`control-centre/`](control-centre/) | OCC supervisor / engineer | §4.4 (C1–C3) |

Each subdirectory has one file per rule block, numbered per the RFC.
The rulebook now contains drafted one-decision rules with `Why:`
rationales across dispatcher, station-staff, maintenance, and
control-centre role families. Practising-operator
review is tracked in
[`validation-checklist.md`](validation-checklist.md) and remains a
deployment release gate.

Maintenance intervals across rolling stock, stations, track/civil,
structures, energy, signalling/comms, depots, and production-plant
tools are consolidated in
[`../rfcs/0029-maintenance-schedule-system.md`](../rfcs/0029-maintenance-schedule-system.md)
and the machine-readable
[`../../lib/templates/maintenance-schedule.toml`](../../lib/templates/maintenance-schedule.toml)
template.

Manufacturing scheduling for trains, waypoints/W-SBCs, track, switches,
stations, depots, energy sites, and production plant tasks is documented
in
[`../rfcs/0030-manufacturing-schedule-system.md`](../rfcs/0030-manufacturing-schedule-system.md)
and the machine-readable
[`../../lib/templates/manufacturing-schedule.toml`](../../lib/templates/manufacturing-schedule.toml)
template.

The browser front door for those generated city operations records is
[`../operations-portal/`](../operations-portal/). It combines the asset
register, manufacturing schedule, QA actions, maintenance schedule, and
launch panels for the existing OCC/simulator/back-office crates.

The integrated [Workbench](../workbench/README.md) can generate this complete
delivery twin for any catalogue city without a shell. Its Project Twin tab
shows the resource-loaded critical path, budget work packages, order-by dates,
supplier-anchor/local-equivalent basis, controlled manufacturer candidate IDs,
selection states and monthly local/imported cash needs.
Actual purchase orders, deliveries, invoices, payments and progress remain
separate persisted Ops Core records; a generated plan never becomes an issued
commercial record by itself.

Healthy trainsets use distributed overnight stabling at powered passenger
stations under [`dispatcher/s6-shift-end.md`](dispatcher/s6-shift-end.md).
The main depot remains responsible for defects, inspections beyond the
platform release check, wheel work, battery exchange, and heavy maintenance;
station stabling is not distributed maintenance.

## How to add a rule

1. Find the right block (e.g. S3 — Incident handling).
2. Append a numbered rule at the bottom of that file in the
   template:

   ```
   ### D3.4 — <short title>

   <one sentence, one decision>

   **Why:** <one short paragraph>
   ```

3. The numbering is `<block>.<n>`; next `n` = the last +1.
4. Every rule has exactly one author — credit in the commit
   message, not the rule body.

## Non-mission-critical reminders for contributors

- **One sentence per rule.** Compound rules break testability
  and become accretion. Split.
- **Every rule has a `Why:`.** An unexplained rule rots. The
  `Why:` block is a contract with the future driver who must
  follow the rule.
- **Cite the RFC / safety-case solution the rule supports.**
  This is how the rulebook feeds the GSN safety case
  (`docs/safety-case/gsn/`).

## Language policy (RFC 0013 §13)

- English is the canonical rulebook.
- Per-country translations land under
  `docs/operations/<iso-lang>/` as a parallel tree once the first
  deployment needs one. Until then, only English is authoritative.
