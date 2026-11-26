# City planning proposals

The planning workspace edits route, stop, service and origin–destination proposals over the current city geography and map context. Open it from [`index.html`](index.html).

Export an edit bundle from the workspace, then compile and verify the handoff:

```sh
./osr plan compile edits.json --output build/my-plan
./osr plan verify build/my-plan
```

The immutable handoff is bound to the selected v0.6 candidate and the source identities used for the proposal. It carries route, stop, service and OD proposals only. It contains no vehicle, propulsion, fleet, civil quantity, cost, performance or cashflow results.

Missing unit prices can be covered in a separate candidate-specific low/base/high Class C estimate from calculated quantities and declared assumptions. Supplier quotes improve procurement readiness but are not required for design-stage cost comparison. A complete installed city estimate still needs route-specific quantities and site scope.

The [calculated city atlas](../../design-engine/city-atlas/README.md) provides current outline service, fleet, civil quantities, complete estimated costs and delivery studies for all 266 cities. A completed local study can be opened here for candidate-bound editing and recalculation. The ordinary planning handoff remains a proposal, while the calculated study carries its own result identities and assumptions. Verified physical performance, procurement approval, construction release and movement authority remain separate.

The automatic city study builds connected route combinations from an empty network using the city's mapped corridors and interchanges. It tests end-to-end services where two mapped termini meet and form a usable through alignment. It prices geometrically distinct proposals on the same scenario. Verified walking access, population coverage and journeys to named destinations are required for a metropolitan replacement. Where those inputs are missing, the study shows the local opportunities, holds and retained corridor comparison. [Shared metropolitan planning method](../../design-engine/current/METROPOLITAN-NETWORKS.md)

Baghdad opens its dedicated three-ring planning network and cost record in Workbench. Run `./osr design railway city-study --city baghdad --output build/baghdad-city-study` to export the same project. The older catalogue outline is available as an explicit comparison and uses its own vehicle and price assumptions. [Baghdad metropolitan network](../../../cities/Baghdad/METROPOLITAN-NETWORK.md)

For the connected candidate workflow, see the [coordinated railway design](../../design-engine/coupled-railway/README.md), [current platform capabilities](../../capabilities/README.md) and [current engineering dossier](../../design-engine/current/README.md).

## Civil scope for a fresh city calculation

A new mapped-city study in the Workbench or `./osr design outline city` prices elevated guideway and retains separately costed bridge crossings. It carries a catenary-free preference into the study record. The available city models use station launch or powered axles with protected conductor. A mapped tunnel proposed for replacement above ground needs an alignment survey and crossing scope before the option can be recommended.

Use `{"city_slug":"samawah","civil_policy":"mapped-mixed-comparison"}` as the JSON request for a separate calculation with the mapped conventional civil classes. The same request works through `POST /api/city-studies` and the CLI `--request` argument. Revisions of an existing study inherit its civil choice. For unchanged mapped inputs and old comparison figures, open the published atlas.

## Compare architecture and service

On a fresh study, the automatic propulsion screen retains station launch on a line if the passive coast calculation meets its bounds. If any leg fails, the study uses the powered-axle research model for that line and prices its added vehicle equipment, continuous protected conductor and substations. The planning screen uses level track and zero wind. The output records the actual propulsion choice and the original coast failures by line. The catenary-free preference covers both models.

To control the comparison, pass `service.propulsion_policy_by_line` in the study request with one entry for every exact line ID. The accepted choices are `station-launch-reference` and `powered-axle-continuous-research`. An explicit station-launch request that fails the coast bound returns a line-specific refusal. Keep civil policy, route, demand, occupancy, availability, operating hours, operating days and pricing basis fixed to compare propulsion. Change headway or dwell as a separate operating case and keep its calculated fleet, section capacity and costs with that case.

For an overhead comparison, the 30 km reference under `./osr reference v07` carries its own overhead collection, vehicles, guideway and service. Baghdad also prices overhead and protected conductor at equal offered service in each of its two network studies. The generic mapped-city calculation currently offers two catenary-free propulsion models. Transferring an overhead hypothesis to another city needs that city's vehicle and clearance interfaces, feeder sections, local installation rates, power and renewal studies. Use the existing overhead cases as separately identified references. [30 km overhead reference](../../reference-v07/README.md) · [Baghdad matched supply alternatives](../../../cities/Baghdad/PROPOSAL.md) · [Iraqi electricity sensitivity](../../../cities/Baghdad/IRAQ-POWER.md)

```sh
./osr design outline city --city samawah --output build/samawah-default
./osr design outline city --request build/samawah-alternative.json --output build/samawah-alternative
./osr design outline city-verify --output build/samawah-alternative --replay
```

Use `summary.json` to compare civil classes, headway, propulsion, fleet and the fourteen cost scopes. Use `result.json.gz` to inspect the detailed leg and capacity screens and the selected research configuration. A service that misses its declared demand or maximum headway can retain a cost for review with a requires-revision disposition. Surveyed grade and alignment, observed directional demand, supplier force and power limits, independent braking and train protection remain physical evidence requirements.

The [Baghdad connected-network decision](../../../cities/Baghdad/CITYWIDE-SERVICE.md) compares a 150-second peak offer and a 30-minute clockface arrangement on its own 700-place powered train. The [Airport first-article opening](../../../cities/Baghdad/engineering/prototype/README.md) carries a distinct 15-minute timetable and feeder evaluation. Each has a separate fleet, scope and operating evidence record.
