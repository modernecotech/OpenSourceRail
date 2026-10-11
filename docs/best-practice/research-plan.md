# Best-practice research and implementation plan

The [handbook](handbook.md) brings component, subsystem and railway-system
guidance together. Its source inputs are the
[practice cards](../../engineering/best_practice/data/practices.json),
[primary references](../../engineering/best_practice/data/sources.json),
[scope assignments](../../engineering/best_practice/data/scope.json) and
[assurance crosswalk](../../engineering/best_practice/data/assurance-links.json).
The [coverage audit](../../engineering/best_practice/coverage.json) reports the
actual inventory counts rather than a separately maintained headline total.

The approach follows OSR's open-hardware philosophy: use original designs,
supplier-neutral interface requirements, repairable modules, local production
where qualified, portable work records and retained failed results. A supplier
example is a candidate method to assess against OSR duty and hazards. It does
not establish a proprietary specification or guaranteed improvement.

## Research decisions

[CRRC's Hangzhou account](https://www.crrcgc.cc/en/2026-04/29/article_2026042916024714810.html)
supports studying lifecycle automation, redundancy and running-gear monitoring.
The existing [factory expansion](../rolling-stock/industrialisation-expansion-plan.md)
already translates these themes into offline commissioning contracts, modular
fixtures, travelers and open quality evidence. This research expands those
methods across infrastructure, stations, software and operation.

Braking guidance treats low adhesion and wheel-slide protection as an integrated
interface, informed by
[Knorr-Bremse's adhesion systems](https://rail.knorr-bremse.com/en/us/portfolio/products-and-systems/braking-systems/adhesion/).
Turnout guidance similarly joins geometry, actuation, locking, detection and
lifecycle care, informed by
[voestalpine's integrated turnout approach](https://www.voestalpine.com/railway-systems/en/company/news/turnout-systems-intelligent-networked-and-future-proof.-system-thinking-for-rail-infrastructure-excellence./?year=2025).
OSR adoption requires actual route-specific tests and released limits.

The ISO preference is applied by scope: thermal comfort and HVAC unit inputs use
[ISO 19659-2:2020](https://www.iso.org/standard/70232.html) and
[ISO 19659-4:2026](https://www.iso.org/standard/85202.html); building/access routes
use [ISO 21542:2021](https://www.iso.org/standard/71860.html); lifecycle decisions
use [ISO 55001:2024](https://www.iso.org/standard/83054.html) and
[ISO 14040:2006](https://www.iso.org/standard/37456.html). Railway battery,
automation and software scopes use relevant IEC references alongside the
existing standards thread. Public scope review leaves complete clause adoption
open.

## Work packages and acceptance

| Package | Deliverable and completion condition | Current state |
|---|---|---|
| BP-01 Inventory | Explicit guidance for every current catalogue definition, Rust package and engineering template; reasoned exclusions and optional/variant context retained | Implemented; automated drift checks |
| BP-02 Research | Primary-source register with dated findings, limits, source kinds and specialist lifecycle cards | Implemented; refresh and applicability remain continuing work |
| BP-03 Interfaces | Vehicle/track/bridge, energy/charging, accessible boarding/evacuation and safety-control guidance with existing assurance objectives | Implemented as recommendations and unperformed verification plans |
| BP-04 Open tooling | Deterministic handbook, component CSV, coverage audit and verification/backlog JSON; mutation tests and CI | Implemented; software validation only |
| BP-05 Project adoption | Complete adopted clauses, approved design basis, numerical limits, verification procedures, sampling and decision authority per configuration | Open; project inputs and competent review required |
| BP-06 Qualification | Supplier freeze, physical first articles, special-process qualification, integrated tests and independent acceptance | Open; research and generated records cannot substitute for tests |

Every practice card names a responsible role and unresolved questions. The
[verification plan](../../engineering/best_practice/verification-plan.json)
allocates each task to all relevant definitions without duplicating prose. Task
acceptance criteria, adopted clauses, procedures, results and evidence are
deliberately unfilled. Resolve them in the existing project assurance workflow,
not by changing an open research task into a passing result.

## Next technical priorities

1. **Wheel/rail/brake/signalling integration.** Freeze actual wheel/rail profiles,
   adhesion and braking envelopes, load cases and movement-authority interfaces.
   The [six-car contact-domain diagnosis](../civil/full-train-contact-domain.md)
   remains an unresolved numerical qualification limit. Complete the validated
   contact model and whole-passage campaign before service claims.
2. **Battery/charger/fire/energy integration.** Freeze chemistry, pack design,
   cooling and charging protection. The reference LTO geometry does not release
   the catalogue LFP pack. Obtain qualified pack data and physical isolation,
   propagation, charger and route-energy evidence.
3. **Structure/material/process release.** Use existing factory passports,
   drawings, inspection characteristics and travelers. Fill grade, process
   windows, calibration and installed build-up fire evidence through competent
   review. Validate fixtures for actual clamp and handling loads.
4. **Station/vehicle/access/evacuation integration.** Survey actual track and
   boarding envelopes for each station variant, confirm lift-outage routes and
   emergency supplies, then perform representative passenger and responder
   demonstrations.
5. **Software/wayside/operations integration.** Review target timing, hardware
   I/O, safety communications, security boundaries and rollback. Source-level
   tests, formal checks and declared SIL/GoA targets require actual target and
   independent integration evidence.
6. **Piece-level and new-architecture research.** Decompose kits into released
   fasteners, terminals, seals and fluids. Transfer guidance explicitly to other
   fleets. Add detailed tunnel and overhead/third-rail scopes if those
   architectures are adopted.

The scope is the current controlled catalogue and workspace. It does not claim
to enumerate every possible rail component, every city asset instance or every
piece inside a kit. Finance, appraisal and publication-only templates have
explicit exclusions; they do not become physical qualification evidence.

## Reproduction and contribution

```bash
python3 tools/automation/best-practice.py generate --as-of 2026-10-11
python3 tools/automation/best-practice.py check --as-of 2026-10-11
python3 tools/automation/best-practice.py review-sources --as-of 2026-10-11
tools/automation/osr-python -m pytest -q engineering/analysis/tests/test_best_practice.py
```

The explicit date makes historical reproduction possible. For a current review,
use the actual assessment date and review any overdue sources first. CI checks
the published assessment date for reproducibility and the current UTC date for
source expiry. It does not browse or silently refresh research. `review-sources`
checks current source age without rewriting a historical publication.

Edit authoring inputs first. Add source limitations and original OSR wording,
map each new definition explicitly, connect it to existing STD-CTRL objectives,
and regenerate all four outputs. A new catalogue item, crate, station variant or
template without a scope decision fails the checker. Changes to input bytes
invalidate the published audit even when item IDs are unchanged.
