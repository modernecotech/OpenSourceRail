# Network junction and residential integration

The [integrated network model](../../engineering/network-planning/baghdad/network-integration.json) coordinates line crossings, shared corridors, station complexes and underserved residential areas with [line-specific foundation/assembly packages](line-based-foundation-and-assembly-planning.md). A visually overlapping route is not automatically a rail junction, walkable transfer or completed civil connection.

## Crossing and overlap packages

| Situation | Required planning and design treatment |
|---|---|
| Two independent rail lines cross | Grade-separated structure with actual rail levels, gradients, clearances, support/cap and construction load paths; a passenger interchange is a separate access decision |
| Routes occupy a common XY corridor | Compare a coordinated four-track footprint with laterally separate guides and shared station/access structure, or reviewed separate vertical levels; do not duplicate coincident decks or footings |
| A line revisits the same location | Preserve distinct chainage legs, then choose a real grade-separated passage or reroute; do not collapse both visits into one node or imply a switch |
| A short A–B–A ring spur | Remove the spurious one-cell reversal without introducing a new land/water shortcut; regenerate route chainages, stations, civil quantities, scenario and dependent evidence |
| An apparent near-miss interchange | Preserve platform positions; identify the actual concourse/street/vertical connection, barriers, rights, walking distance and timing before acceptance |

The Baghdad ring repair removes its 20 m outward-and-return spur, shortening the planning route by 40 m. It does not erase a district-serving branch or insert an unreviewed chord. The source repair leaves longer excursions and supplied protected cells for explicit review.

Every [junction design package](../../engineering/network-planning/baghdad/junction-design-packages.json) identifies participating lines and chainage legs, affected spans and support packets, design alternatives and the J0–J3 arrangement/profile/site/stage/handover sequence. Upper/lower rail levels, vertical clearance and graded approaches stay unselected until a real profile and independent structural review exist. Ordinary member orders that touch the interface are held until J2; current drawings and existing route-km budgets cannot establish an accepted junction cost or final geometry.

## Bounded station complexes

Grouping uses the **maximum pairwise platform separation**, with a 600 m planning screen. A chain of nearby stations does not make its distant ends one complex, and an additional same-line amalgamation cannot silently enlarge the diameter. Original oversized groups remain in the review register with the bounded replacement concepts and their actual platform IDs. No platform is shifted to an averaged centre point.

The diameter is a geometry screen, not a walking path. Rivers, roads, walls, level changes, stairs/lifts and entry permissions need actual accessible routes and transfer times. A close pair can still fail. Concourse/platform capacity, outage operation, assisted rescue, fire, PSD/train interfaces and structural loading use the installed arrangement. The proposed grouping does not alter the native timetable or invent a physical track switch.

## Population-led coverage

Use retained native **2020 WorldPop count pixels** and count each person once in a union of distance circles. Keep the population year, bbox and nodata explicit; never multiply a routing-demand score by a current city-population headline. The [coverage model](../../engineering/network-planning/baghdad/network-integration.json) separates existing station proximity, corridor proximity, infill sensitivity and branch/feeder investigation.

Infill candidates sit on current lines and are ranked by incremental previously unserved retained population, subject to minimum same-line spacing and ring wraparound. Candidate stations require water/footprint, property, access, platform/approach, timetable/fleet/energy and complete installed-cost checks. A population-rich point is not a released station site.

Large residential gaps outside current corridors cannot be solved by infill alone. The [priority areas and expansion corridors](../../engineering/network-planning/baghdad/expansion-corridors.json) identify source-linked district/nearby place names, existing station connection, route/access gaps, and an arterial investigation path. Compare an engineered rail branch/extension with a frequent feeder and accessible transfer. Road vertices define an undirected preliminary graph; traffic direction, stopping sites, grade connections, bridge limits and permissions are unverified. Do not issue driver navigation or a rail alignment from this screen.

The combined 500 m feeder-stop and 1 km rail-station circle cases are **conditional sensitivities**, not measured walking coverage or funded service. Shared candidate road segments are counted once in the corridor-edge register. Priority-area circles can overlap and are never summed as unique residents. Actual travel-time/OD, affordability, service/headway, capacity, operating cost and finance remain required before selecting and adopting expansion.

[ITDP People Near Transit](https://itdp.org/pnt/) provides a population/proximity assessment reference; [ITDP physical integration](https://brtguide.itdp.org/branch/master/guide/multi-modal-integration/physical-integration) addresses interchange/access development. [WorldPop's model-method description](https://www.worldpop.org/methods/top_down_constrained_vs_unconstrained/) explains the constrained/unconstrained dataset assumptions. These references do not turn retained circles or road lines into accepted Baghdad walksheds.

## Catalogue review and adoption

The [266-city audit](../../engineering/network-planning/baghdad/catalogue-audit.csv) reports declared transfer components, self-intersecting lines, cross-line overlap pairs, oversized interchange groups and retained 1 km population fractions. Missing geometry/population stays unavailable. Audit findings require local geometry, site and service investigation; they are not automatically deployed changes to every city.

Use one controlled adoption revision for selected corridors, junctions and stations. Regenerate design/scenario, civil and mechanical quantities, foundation/assembly, geography/clearance, energy/service, finance, staffing, deployment and publication in dependency order. Execute actual native nominal/degraded cases for changed inputs, preserve source-bound receipts, and reopen affected independent/site gates. The original supporting archive and new companion planning archive keep the earlier comparator and new model accessible without exceeding the repository's per-file limit.
