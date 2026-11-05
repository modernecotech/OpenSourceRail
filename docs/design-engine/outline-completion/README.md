# Complete calculated city and design outlines

OpenSourceRail turns the registered design portfolios and mapped city networks into inspectable outline studies. Missing quotations and detailed equipment data use named, bounded engineering estimates. A calculated outline is a successful design-stage result; it is separate from independently verified engineering, manufacturing and operating approval.

<!-- BEGIN calculated outline coverage -->
## Current calculated coverage

**266 city networks**, **1565 lines** and **32,690.0 route-km** have complete fourteen-scope installed and 30-year cost scenarios.

15,227 retained map stop markers are represented by 13,580 operational station complexes. The campaign priced 623 original/revised alignment scenarios; 150 revised alignments are retained for further outline detailing under the declared access and cost assumptions.

Design coverage also includes **112 railway bundles**, **54 body outlines** and **18 civil spans**, each at its explicit component or system scope.

| City example | Network km | Lines | Operational stop complexes | Trainsets | Central installed US$m | Central US$m / route-km |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Samawah | 57.9 | 5 | 25 | 81 | 1,141.5 | 19.72 |
| Baghdad | 494.4 | 14 | 157 | 533 | 8,354.6 | 16.90 |
| Lyon | 296.5 | 9 | 109 | 337 | 4,754.0 | 16.03 |
| Agra | 158.5 | 5 | 54 | 191 | 2,709.5 | 17.09 |

Calculation `bf56f4726e6476b1936e7a3ea8d670ce7a3d8894d830685357d4fcd58af44607`; publication `c4d7b76b317dcb9b5f9e9959004d194629655d62c7caa0db785a417c095c9b0a`.
<!-- END calculated outline coverage -->

## Methods

Every city retains its own mapped route coordinates, stop markers, line topology, interchange identities and civil alignment classes. Each line is recalculated over its actual stop gaps, including ring closure. Close stop markers are assigned to compact operational station complexes, with standard 120 m platforms, nonoverlapping boarding intervals and priced access connectors. Transitive chains of nearby markers are retained as rejected diagnostics rather than creating long platforms or walks. Distinct access markers may share one boarding location. Source maps remain available unchanged.

The alignment portfolio compares the original, anchor-preserving straighter corridors and, where applicable, rounded square/rectangular rings with a station on each side and required transfer connections. Altered land, access, crossings and site risk have nonzero prices. Square proposals failing the declared access screen remain priced, visible alternatives; they do not win by dropping inconvenient passengers. Corners have an explicit radius and conservative speed hypothesis. Quieter running is not demonstrated by a different shape alone.

The common starting demand is **4,000 peak passengers/hour/direction per line**, 85% planning occupancy, 99% assumed availability and a maximum five-minute headway. These are editable planning hypotheses, not city-specific passenger forecasts. Empty origin–destination data is not reconstructed from historical train capacities. Population retained in the geographic source is not treated as an authenticated forecast. Service, fleet, reserve trains, dwell/charging and nominal energy balance are calculated for each network.

Station-only propulsion is retained where its conditional calculations fit. Where the reference coasting target fails, an explicitly identified powered-axle research configuration includes added equipment mass, drive power, collection/protection, continuous supply, energy and recovery scope. No alternative inherits the selected reference's physical evidence or silently replaces it. Available-force maps, adverse cases and protected operation still require independent engineering validation.

Costs cover all fourteen scopes: rolling stock, guideway, factory/tooling, construction, station power, land/utilities/depot, fleet, electricity, operations, maintenance, renewals, recovery, reliability and disposal. Committed fleet and civil quantities determine production capacity; shared factories, premises, yards, depot and access sites are counted once. Production and construction use two shifts; extended 24-hour operation uses three. Future replacements distinguish reused premises from renewed equipment and reset component ages when their parent is replaced.

All budgets use **US dollars and low/base/high Class C cases**. China-origin wholesale/manufacturer observations and calculated local production are coupled to explicit reference labour, concrete, land and site templates. Foreign-city rates have declared transfer sensitivities; they are not verified local bids. Sensitivity cases are not confidence intervals. No unresolved cost becomes zero. A scope that is physically absent, such as a tunnel in an entirely surface network, can have zero quantity while the complete system ledger still covers every applicable scope.

The 112 railway bundles retain their original synthetic-corridor requirements while selected material/process subcosts are recalculated. The 54 bodies retain stock prices and add estimated body hardware, joining, assembly, inspection, handling and separate tooling/setup. The 18 spans retain their own geometry, quantities and scoped installed/lifecycle budgets. A body or span price is not presented as a complete vehicle or city price.

## Inspect and reproduce

Open the [Workbench](../../workbench/current/index.html), select **Browse priced cities**, then inspect the map alternatives, station complexes, full cost scopes, assumptions and delivery drafts. Every city has a downloadable compressed record in `cities/` and compressed GeoJSON proposals in `maps/`. The Workbench loads these on demand; [summary.json](summary.json) is the small coverage/price index and [manifest.json](manifest.json) binds the exact sources and outputs. The local API returns ordinary JSON; static hosting uses the browser's gzip decompression.

```sh
.venv/bin/python -m engineering.outline complete --output build/my-completion --workers 2
.venv/bin/python -m engineering.outline complete-verify --output build/my-completion --replay
.venv/bin/python -m engineering.outline complete-publish --state build/my-completion --output build/my-compact-publication
```

The coordinator resumes unchanged requests, reuses completed city records and preserves failures. Source changes require a fresh state. Full ledgers and alternative experiments remain in private immutable execution packages, referenced by hashes; Git holds compact results and reviewable maps. Workers do not modify source or publish.

Delivery exports include calculated quantity takeoffs, purchasing/making routes, production resources, phased work packages and disabled business-system drafts. They do not submit transactions, assign named staff, certify factory schedules, approve construction or grant movement authority. Surveyed demand, land/utility/ground evidence, complete installed details, structural/fire/accessibility verification, actual propulsion/braking/protection and independent review remain separate qualification work.

## Edit a city and complete its delivery outline

Run `./osr workbench`, select a priced city and calculate a scenario. Demand, maximum wait, operating hours, access policy and manufacturing/purchasing basis are editable. Open **Edit this outline and recalculate** to move or join stops, change service/dwell or replace a route with explicit coordinates and stop positions. Edits use an immutable, verified planning base from that exact calculation; a new base is exported after each revision. Geographic context remains visible. An insufficient requested headway or failed access screen produces a priced proposal requiring revision, without silently changing the request.

Each study calculates all fourteen cost scopes, then generates a resource-constrained task programme, material receipts, production/civil workstations and workforce needs. It reuses the already priced factory capacity; two shifts do not imply duplicate free machinery. A missed programme target is reported with its time-dependent overhead and available contingency, rather than hidden by adding unpriced capacity. Production/civil use two shifts; 24-hour operation uses three. Operations retain the requested annual days and the relief allowance already included in their price.

```sh
./osr outline city --city samawah --output build/my-city
./osr outline city-verify --output build/my-city --replay
# Use --request scenario.json for bounded service/alignment/pricing options or typed edits.
```

Outputs include a summary, editable planning record, full cost ledger, relative-workday schedules and per-Doctype ERPNext/Frappe drafts. The drafts preserve source identities and existing active orders. They remain disabled/local and require company, warehouse, designation, actual working calendars and engineering review before any site import. No external transactions occur.

The loopback API runs one bounded worker at a time, with a 90 CPU-second/120 wall-second calculation budget, 3 GiB address-space limit, 64 MiB output allowance and 512 MiB total study store. Failed/interrupted requests and logs are retained. Identical verified requests reuse their results; changed sources invalidate reuse. Detailed studies and logs stay under `build/city-studies/`, outside Git. Published city records remain compact and load on demand.

## Validation and execution

The compact-station campaign completed all 266 cities and 623 alignment scenarios with no failed or pending records in 224.28 seconds on two bounded workers. The command recorded 382,496 KiB maximum resident set size and no swaps; this is not simultaneous whole-machine memory. No native FEA, CAD or hardware test was executed by this costing campaign.

An independent read-only service audit covered all 266 cities, 623 alignment alternatives and 3,936 line variants. It checked platform spacing/nonoverlap, retention of every access marker, connector walks, exact leg braking bounds, nominal charging, normal capacity and independently reconstructed fleet/reserve/platform arithmetic. The largest calculated connector was 119.99 m. Its sealed private receipt is `526ab62c508fa7c4d0dce0ef7d27d00cb3babd7ef0df6e43163a352805dc9a92`. Original city geography and route files remain unchanged. Shared-filesystem hashes and process resource limits were used; this is not an OS-enforced source sandbox or physical validation.

An independent no-edit planning round trip also passed every city: installed cost, whole-life cost, all fourteen scope totals, resources, civil quantities, platforms, dwell and access were exactly unchanged. All 266 revisions passed their declared functional checks, with no inherited access hold. The 220.96-second audit receipt is `3dddb085baaf0396dab42eb14f0f241ab8d97e3bbbc7f03b522597bec7db51e8`. An earlier audit exposed a one-ULP projection drift; unchanged headways now preserve exact train-km and departure values. Failed/interrupted audits remain archived.

The integrated controller tests cover real mapped-city calculation, exact editable-base custody, iterative pricing, insufficient requested capacity, child/export identities, stale sources, cache reuse, output tampering, bounded requests, concurrent ownership, interrupted workers and corrupt-status recovery. Operations tests distinguish two-shift production/civil from three-shift 24-hour operation, and retain a requested 330-day operating year. Python 3.12 and 3.13 regression runs are recorded in the private execution receipts. Per-Doctype draft fields were independently checked against pinned ERPNext/HRMS v15 schemas; no target site or real transaction was used.

Real loopback HTTP runs for Samawah, Baghdad and Lyon generated approximately 24.7, 47.0 and 39.9 MB of complete artifacts, below the 64 MiB job allowance. Their calculation times were 12.75, 24.50 and 23.32 seconds; verification and transfer add time. All three provisional base programmes exceeded the 750-workday planning target, while respecting their priced resources. The result reports that overrun and its contingency allocation. Actual dates, supplier capacity and engineering releases are not inferred from a task graph.

The published presentation is approximately 46 MB instead of the initial 217.4 MB; the index is approximately 2.3 MB. Detailed maps and city records load individually. Full execution ledgers, earlier publications, diagnostic attempts and source checkpoints remain outside Git and are bound by immutable hashes. Presentation compression has a separate source identity from the engineering calculations.
