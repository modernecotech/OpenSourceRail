# Population-led additional lines and country regeneration

The controlled route inventory now includes additional lines selected from residential gaps, rather than leaving all additions in a separate sensitivity map. Each added route connects to a retained corridor at an actual common grid cell. Near-ring diversions preserve selected residential sites and avoid new self-intersections, protected cells, unknown water and unapproved long crossings. Native crossing, platform, terminal and bounded-interchange checks still apply.

The [shared policy](../../design/network-planning/residential-expansion.json) uses retained native 2020 population counts, a working 80% station-circle target, a 1 km radius and a 1.6 km ordinary station-spacing cap. New line candidates have controlled length, incremental-population and route-budget screens. Country and city finance inputs remain local; Baghdad's indexed funding arrangements are not copied to other countries.

## Controlled revision and actual coverage

Each city retains `engineering/alignment/network-expansion-baseline.json.gz`, preserving the original design bytes and their hash. Its `residential-line-expansion.json` identifies added line IDs, priority cells, actual corridor connections, route quantities, controlled original-line junction changes and unresolved site/geometry reviews. Mandatory native geometry checks can reject a candidate; a failed diversion never creates a fictional transfer.

Selection credits retained baseline stops and explicit residential priority sites. Ordinary sampled stations are not credited as delivered coverage because native spacing and junction consolidation can remove them. The separate `residential-expansion-evaluation.json` audits the actual emitted station coordinates after generation, using the union of native population-count pixels. Remaining gaps and a missed target are reported. A target is never declared reached from a renderer, a routing-demand score or a sum of overlapping district circles.

Where population evidence is missing or contradicts the controlled source/jurisdiction finding, population-led additions remain unavailable. Those cities still receive the current route, junction, civil, fleet, depot and economic logic. No residents or coverage fraction are invented. Existing unsuitable geometry remains an explicit structural/profile/access review where a controlled replacement is infeasible.

## Complete regeneration

1. Rework controlled core geometry, connect reviewed junctions and add population-led routes; retain immutable baselines and constraints.
2. Emit actual native stations, bounded complexes, civil classifications, fleet/depot quantities, operating overrides and scenarios. New native spacing owns placement; the older infill overlay becomes a comparator and records unresolved gap reviews.
3. Refresh actual local civil costing before freezing the design and scenario inputs. Execute the full nominal day and degraded native software cases, retaining their actual source-bound outputs and receipts.
4. Regenerate SUMO/GIS/energy, desktop ground and site-evidence packages, timing references, operations, finance, depots, stabling, factory, delivery and deployment. Reconcile operations and finance in dependency order; a funding source mismatch stops publication.
5. Audit emitted-station population and connectivity, geography and clearance. Update city packages, country briefs, portfolio, construction/assembly, readiness, catalogue audits and publications from the final inventory.
6. Verify source/output hashes, complete archives, links, file limits, repository health and generated drift before merging.

Use `tools/automation/regenerate-all.sh --current-design-logic --prepare-only --jobs N` for the layout phase. The batch receipt explicitly says engineering refresh is required; it does not mark a planning package complete. The complete run uses actual engineering and native validation, or verified native CI artifacts from the exact frozen source revision.

## Finite construction plant

Two candidate erection fronts per line do not create two additional purchased machines. The connected construction study assigns fronts to a finite launcher pool, with the preceding assignment as a required dependency. Support-release teams also follow finite pool queues and working calendars. Optional ring transfers use only the final donor assignment; a machine cannot be taken from a queued line.

Per-line foundation, bay, beam and launcher records retain actual identities and directed installation order. Soil investigation, foundation selection, loading combinations, vertical profiles, access/property rights, temporary works, suppliers, prices and independent construction/operating acceptance remain required. Station-circle proximity is not current census, surveyed walking access, observed ridership or funded passenger service.
