# OSR-BP-001: Source-backed component and system practice

Version 1.0.0 · adopted 2026-10-11 · internal OpenSourceRail research and
engineering-process standard.

This standard defines how OSR turns public industry examples and standards
discovery into original, open guidance. It supplements
[OSR-ENG-001](OSR-ENG-001.md), [OSR-ENG-002](OSR-ENG-002.md) and
[OSR-MFG-001](OSR-MFG-001.md). It governs research completeness and provenance;
it does not supply universal product acceptance values.

The [practice register](../../engineering/best_practice/data/practices.json)
and [source register](../../engineering/best_practice/data/sources.json) are the
authoring inputs. The existing
[Digital Standards Thread](../certification/digital-standards-adherence.md)
remains the authority for deployment applicability, adopted editions/clauses,
evidence and G0–G4 decisions. Each practice links to its existing STD-CTRL
objectives; those links do not close a gate.

| Rule | Mandatory internal requirement | Automated check |
|---|---|---|
| OSR-BP-01 | Every scoped product, assembly, reusable civil type, station variant, Rust workspace package and engineering template shall have explicit specialist guidance. | Exact inventory/mapping equality; no keyword fallback |
| OSR-BP-02 | Every shared template shall be classified as in scope or excluded with a reason. | New/deleted/ambiguous template detection |
| OSR-BP-03 | Guidance shall cover design, materials/dependencies, assembly/build, inspection, maintenance, verification and unresolved decisions, with a responsible role. | Required nonempty card fields |
| OSR-BP-04 | Technical research shall record a primary publisher, public URL, reviewed date, source kind, finding and limitation. | Source identity/type/date and reference validation |
| OSR-BP-05 | Standard scopes, regulatory scopes, manufacturer examples and method references shall retain distinct interpretations. | Source-kind checks and generated limitations |
| OSR-BP-06 | Public metadata shall not be represented as complete clause review, product qualification or achieved safety integrity. | Unsupported acceptance/physical/clause states rejected |
| OSR-BP-07 | Cross-system interfaces shall have guidance and verification tasks in addition to local part checks. | Vehicle/track, energy, boarding and safety-control practice allocations |
| OSR-BP-08 | Guidance shall use existing assurance control identities; project adoption shall resolve jurisdiction, edition, clauses, limits and authority. | Complete practice-to-STD-CTRL crosswalk with known IDs |
| OSR-BP-09 | Unperformed verification plans shall retain open acceptance criteria, procedures, results and evidence. | Generated task states remain open and unperformed |
| OSR-BP-10 | Kit contents, optional configurations, station variants and future scopes shall remain visible. | Preserved applicability records and explicit expansion backlog |
| OSR-BP-11 | Published guidance shall be reproducible from exact source bytes and an explicit assessment date. | SHA-256 inputs and regenerated JSON/CSV/Markdown comparison |
| OSR-BP-12 | Research shall be refreshed after source expiry or an applicability-changing revision. | Date-based refresh findings; stale outputs fail checking |

OSR research refresh intervals are 90 days for regulatory sources, 180 days for
manufacturer examples, 365 days for public standard scopes and 730 days for
method references. These are internal review policies, not ISO or IEC
requirements. A safety-relevant change triggers earlier review. Refreshing a
date requires reviewing the source and recording any changed finding or limit;
editing a date to make a check pass does not satisfy this rule.

Use ISO references where their scope applies, then applicable railway-specific
IEC/EN methods and local authority requirements. For example,
[ISO 19659-4:2026](https://www.iso.org/standard/85202.html) provides an HVAC-unit
design-input and test scope, while
[IEC 62928:2017](https://webstore.iec.ch/en/publication/31101) addresses onboard
traction batteries. Complete adopted clauses and installed-system evidence are
required before project acceptance. Supplier web pages support discovery and
method selection; they do not freeze a purchase specification.

Practice wording is original OSR synthesis and follows the repository's
[path-based licensing](../../LICENSE.md). References retain their publishers'
terms. Proprietary drawings, normative text and control algorithms are not
redistributed by this register. Portable data and supplier-neutral interfaces
support local manufacture, repair and independent assessment.
