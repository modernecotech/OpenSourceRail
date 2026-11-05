# Complete calculated city and design outlines

OpenSourceRail turns the registered design portfolios and mapped city networks into inspectable outline studies. Missing quotations and detailed equipment data use named, bounded engineering estimates. A calculated outline is a successful design-stage result; it is separate from independently verified engineering, manufacturing and operating approval.

<!-- BEGIN calculated outline coverage -->
## Current calculated coverage

**266 city networks**, **1565 lines** and **32,688.9 route-km** have complete fourteen-scope installed and 30-year cost scenarios.

15,227 retained map stop markers are represented by 12,725 operational station complexes. The campaign priced 623 original/revised alignment scenarios; 153 revised alignments are retained for further outline detailing under the declared access and cost assumptions.

Design coverage also includes **112 railway bundles**, **54 body outlines** and **18 civil spans**, each at its explicit component or system scope.

| City example | Network km | Lines | Operational stop complexes | Trainsets | Central installed US$m | Central US$m / route-km |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Samawah | 57.9 | 5 | 25 | 81 | 1,142.1 | 19.73 |
| Baghdad | 494.4 | 14 | 157 | 533 | 8,356.0 | 16.90 |
| Lyon | 296.5 | 9 | 96 | 327 | 4,689.8 | 15.82 |
| Agra | 158.5 | 5 | 54 | 191 | 2,709.5 | 17.09 |

Calculation `94dae218fef5964e77c6dd9b5998f1e8d919634f8bfdf05cf3006628a370ea68`; publication `26c934acb8e3bca3205c8a1603f0819c1d55d7b24e5caccd2b3572d430347dff`.
<!-- END calculated outline coverage -->

## Methods

Every city retains its own mapped route coordinates, stop markers, line topology, interchange identities and civil alignment classes. Each line is recalculated over its actual stop gaps, including ring closure. Close stop markers are joined into operational station complexes with explicit access distances, platform and walkway provisions. Source maps remain available unchanged.

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

## Validation and execution

The 5 November run completed all requested cities with zero pending or failed city records. A two-city checkpoint verified before the remaining 264 cities resumed on two bounded workers in 217.07 seconds. The command recorded 369,780 KiB maximum resident set size and no swaps; this is not a measurement of simultaneous whole-machine memory. No native FEA, CAD or hardware test was executed by this costing campaign.

An independent read-only audit reconciled every city's three-case capital/lifecycle ledger, fourteen scopes, service/fleet bounds, station repairs and eligible alignment minimum. It independently replayed all 184 scoped design prices and reproduced Baghdad, Samawah and Lyon byte-for-byte on Python 3.12 and 3.13. All 532 original city geography/route files remained unchanged. The audit used shared-filesystem integrity checks, not an OS-enforced isolated environment. Its private sealed receipt is `b7c26126e3602a0cc47b8f8d525c2ab7adf47c41b268a1bc94f649d883ee9999`.

The published presentation is approximately 43.9 MB instead of the initial 217.4 MB; the index is approximately 2.3 MB. Detailed maps and city records load individually. Full execution ledgers, earlier publications, diagnostic attempts and source checkpoints remain outside Git and are bound by immutable hashes. Presentation compression has a separate source identity from the engineering calculations.
