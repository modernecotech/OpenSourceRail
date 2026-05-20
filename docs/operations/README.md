# OpenSourceRail — Operations Rulebook

This directory holds the rule text referenced by
[RFC 0013](../rfcs/0013-operations-rulebook.md). Every rule sits
inside the one-sentence-one-decision style the RFC commits to.

**Target length, rendered PDF: ≤ 60 pages.** If the full compiled
book exceeds that, something gets cut before anything is added.

## Layout

| Path | Audience | RFC 0013 section |
|---|---|---|
| [`driver/`](driver/) | Train driver | §4.1 (D1–D8) |
| [`dispatcher/`](dispatcher/) | OCC dispatcher | §4.2 (S1–S7) |
| [`station-staff/`](station-staff/) | Station agent / inspector | §4.3 (T1–T5) |
| [`maintenance/`](maintenance/) | Depot + MOW worker | §4.4 (M1–M7) |
| [`control-centre/`](control-centre/) | OCC supervisor / engineer | §4.5 (C1–C3) |

Each subdirectory has one file per rule block, numbered per the RFC.
The rulebook now contains drafted one-decision rules with `Why:`
rationales across dispatcher, station-staff, maintenance,
control-centre, and legacy driver role families. Practising-operator
review is still a v0.2/v2.1 task.

## How to add a rule

1. Find the right block (e.g. D3 — In-service operation).
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
