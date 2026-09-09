# Peshawar deployment gaps

3 closed checks; 13 open gates. Status follows the linked evidence; generating a receipt template does not count as receiving field data.

[Soil inputs](../soil/README.md) include a route/station investigation plan.

| Gate | Status | Responsible function | Closure work |
|---|---|---|---|
| [soil-desktop-inputs](../soil/summary.json) | closed | civil/geotechnical designer | Sample current station and civil geometry from the pinned soilDB source and retain means, uncertainty and nodata. |
| [soil-coverage](../soil/civil-investigation-plan.json) | closed | geotechnical investigator | Fill mapped coverage gaps through local records and targeted sampling; keep estimated and measured records distinct. |
| [control-processing](../survey/control-processing-readiness.json) | open | survey team | Receive survey control observations; process and check the project CRS, datum and residuals. |
| [ground-model](../survey/ground-model-readiness.json) | open | survey team | Receive and inspect the terrain, point cloud and ground-model deliveries against independent control. |
| [surveyed-alignment](../survey/surveyed-alignment-readiness.json) | open | alignment designer | Replace or confirm generated geometry with checked survey alignment and platform reconciliation. |
| [route-station-fit](../survey/route-station-fit-readiness.json) | open | civil/station designer | Resolve utilities, land/access, flood levels, station access and construction staging against the current route. |
| [drainage-ground](../survey/drainage-ground-readiness.json) | open | civil/geotechnical designer | Use the soil investigation plan to collect local geotechnics and groundwater, size foundations/treatment, and check drainage with local rainfall and surveyed levels. |
| [structural-release](../survey/structural-release-readiness.json) | open | structural designer and checker | Complete route-specific support/span, foundation, movement and erection calculations and close checking comments. |
| [model-timing-comparison](../simulation/operations-crosscheck.json) | closed | simulation engineer | Reconcile current native reference journey times with SUMO using the same scenario dwells and route. |
| [full-service-validation](../simulation/validation-summary.json) | open | simulation engineer | Run current nominal and degraded full-service cases against the current scenario and simulator; retain failures and exact provenance. |
| [operating-release](../simulation/operations-crosscheck.json) | open | operator | Complete conflict-aware capacity and degraded-operation review and sign the bound operating evidence. |
| [morning-fleet-allocation](../stabling/summary.json) | open | service planner | Reconcile revenue fleet with required morning departures on each line; retain two station berths and same-line overflow storage. |
| continuous-stabling-replay (evidence missing) | open | simulation engineer | Run the selected line-local station/depot candidate across consecutive evenings and synchronised morning starts. |
| [stabling-physical-fit](../stabling/summary.json) | open | track/station designer | Locate usable station and line-local depot tracks, shared charging, isolation, inspection access and protected morning release slots. |
| [solar-storage-endurance](../energy/summary.json) | open | energy designer | Bind declared station/ROW/dedicated PV to site storage and actual charging duty, reconcile conversion losses and prove replenishment across adverse weather; specify residual backup duty explicitly. |
| [depot-placement-and-budget](../depot-scope/summary.json) | open | depot and cost designer | Place the declared PV/storage inventory within the controlled site layout and reconcile itemised installed costs and renewal scope with existing allowances. |

city civil and operating deployment evidence; manufacturing and system certification remain in their own release registers.
