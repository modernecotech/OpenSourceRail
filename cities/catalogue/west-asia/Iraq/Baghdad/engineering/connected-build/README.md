# Baghdad connected construction and battery study

Generated from RFC 0034; 2026-10-06. These are unquoted, conditional sensitivities, with no accepted supplier capacity or structural/access releases.

The package has 186 stations, 238 physical platforms and 411 boarding faces. Elevated islands use individually identified lifts, escalators, stairs and shafts; their flow/evacuation/one-lift-out approvals remain open. [Station quantities and access costs](stations.json), [track-spreading approaches](station-approaches.geojson) and [proposed entrances](entrances.geojson) derive from the same layout. Coverage from accepted accessible entrances remains unknown; the existing centroid-based archive cannot close that assessment.

[Running civil quantities and conditional deployment](civil.json) exclude station and spreading-approach zones. The 18 independent fronts initially use two launchers per line where running work exists. The 18-machine/two-shift 1.5, 1.8 and 2.0 bays/day sensitivities retain 54, 64.8 and 72 beams/day as average fleet demands. Integer daily schedules are in `schedule-*.json.gz`. The initial case completes its running bays in 773 days under its explicit hypothetical supply/readiness inputs; special crossings, station structures, rolling stock and permits remain separate opening gates. The evidence-backed schedule reads the supplier and route registers and completes zero bays because accepted supplier capacity and released supports are absent.

[Supplier register](suppliers.json) records the sourcing basis that Iraq already has many precast facilities and production expertise. No named facility, available beam capacity or assumed contract is adopted. The [logistics plan](logistics.json) now feeds casting, acceptance holds, dispatch limits, gross vehicle/bridge loads, journeys, shared fleets and factory/front buffer limits into the same erection schedule. Rejected components require replacement; blocked storage pauses production. Each front reports days limited by casting, acceptance, transport, foundations or erection. The assumed pool is a resource requirement, not an identified supplier or confirmed spare capacity; real routes and contracts remain in separate registers.

[Costs and cash sensitivities](costs.json) keep the $9m launcher purchase allowance and exclusions visible. Embedded erection in installed civil rates is unverified, so no net saving or complete financing total is claimed. Gross access equipment, maintenance, replacement, factory scope and night-shift sensitivities remain separate; rolling-stock/electronics factory allowances are retained. Payment dates are conditional cash planning, not purchase orders.

[Energy comparisons](energy.json) use explicit pack identities, mass-adjusted traction, shared chargers, setup time, temperature/SOC limits, seasonal solar/cleaning, hot auxiliaries, missed charges, outage/reserve duties and degradation. All three matched chemistry cases report minimum SOC and service shortfalls. The small onboard pack is a separate option. The full-network chronology uses declared stations, fleets, headways, dwell and site capacities with an explicit average-speed screen; it requires timetable qualification and makes no supplier chemistry claim.

The planning duty schedules 772 trainsets and 164 energy sites. There are 118 dispatches without a ready trainset. All matched cases below have service shortfalls under the selected hot-weather assumptions; none qualifies the declared service.

| Case (lower-solar duty) | Minimum SOC | Unserved traction kWh | Shortfall events |
| --- | ---: | ---: | ---: |
| lfp-throughout | 0.0% | 7,196 | 68,942 |
| sodium-stationary | 0.0% | 7,251 | 69,346 |
| sodium-both | 0.0% | 804,918 | 870,023 |

[ERP planning drafts](erp-drafts.json) identify reusable machines and distinct front/shift crews, with purchase, commissioning, inspection, maintenance, competence and transfer gates. No live ERP purchase/allocation is approved by this package. Cash purchase, project allocation and residual value are distinct.

[Manifest](manifest.json) hashes every source and output and identifies the source revision and assumption register. Existing finance/proposal packages are retained comparators pending scope-matched adoption; this study is the current connected scenario, not an accepted replacement budget. Regenerate with `.venv/bin/python tools/automation/connected-build-study.py --city baghdad`; verify using `--check`.
