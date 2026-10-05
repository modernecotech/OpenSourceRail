# Baghdad access, demand and paid journeys

**Status: survey handoff; no calibrated demand forecast or revenue uplift.**

Native population pixels → verified station entrances/walking times → jobs/destinations and surveyed OD journeys → route choice → section/time train loads → unique paid journeys → collected fare receipts.

The [retained access report](../access/README.md) counts radial unions in 2020 pixels. Rivers, motorways, walls, crossing availability and station vertical access need an entrance-based walking network. The retained OSM export contains selected arterial geometry and building/water polygons; it is not a complete pedestrian graph or entrance survey. Do not route through private premises, infer a crossing from coincident lines or count a 2 km feeder catchment as convenient walking coverage. Jobs, entrances and OD observations remain missing.

The current financial paid-trip assumption remains capacity-led. Shorter lines and different catchments do not automatically preserve or increase patronage. `baghdad_demand_bridge.py --od <survey.json>` validates explicit line paths against declared transfers and reports unique paid journeys, train boardings, line boardings and fare receipts separately. An integrated fare charges each journey once; only an explicitly declared boarding tariff charges its legs. The source and survey date are required. Aggregated annual line boardings are not peak section loads, unique people or a validated route-choice forecast.

Before adopting receipts, independently qualify the OD evidence and sampling/expansion weights, income/concession response, entrances and accessible walking paths, waiting/transfer time, route choice, peak section capacity, fare caps and collection losses. Re-size service/fleet/energy/OPEX together and regenerate the financial ledger. No survey, jobs, path, peak load or additional income is fabricated to close the gap.

[Source-bound handoff and accounting](summary.json).
