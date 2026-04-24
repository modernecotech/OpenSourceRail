# As-Samawah — Urban Rail Network

**Country:** IQ · **Population:** 220,000

Auto-planned by [`osr_planner`](../../../design-py/src/osr_planner/) using the linear-logic algorithm on Overpass-verified OpenStreetMap data. Every station sits on an aggregated POI cluster; every line polyline follows the OSM arterial graph (trunk / primary / secondary / tertiary — residential streets excluded, so lines cannot zigzag through a residential grid).

## Network map

![As-Samawah rail network auto-planned by osr_planner](../../../docs/screenshots/samawah-network-map.png)

*Detail-zoom render: [`samawah-network-map-detail.png`](../../../docs/screenshots/samawah-network-map-detail.png). Corridor GeoJSON for GIS / alignment tooling: [`samawah-corridor.geojson`](../../../docs/screenshots/samawah-corridor.geojson).*

## At a glance

| Metric | Value |
|---|---|
| Lines | 4 |
| Unique stations | 29 |
| Interchange stations | 5 |
| Multi-line transfer reachability | 100% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | — (set `[stats] coverage` in design.toml) |
| Route length (double track) | 45.1 km |
| Revenue fleet | 16 × 3-car trainsets |
| Spare + cold-reserve | 8 × 3-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 23:30 (≈ 18 h/day) |

## Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| Line 1 | 12.1 km | 11 | 4 | Al M'aly Khlf Alskh ↔ Jam'h Sawh |
| Line 2 | 10.8 km | 11 | 4 | Mjm' Albrkh Alskny ↔ Abwjwylanh |
| Line 3 | 13.5 km | 11 | 5 | Dwr Alskk ↔ Aljrbw'yh Alstalaf |
| Line 4 |  8.7 km | 8 | 3 | Rail Station 1 ↔ Klyh Tb Alasnan Jam'h Almthna |
| **Total** | **45.1 km** | **29 unique** | **16** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 3-car, 68 m |
| Max speed | 80 km/h |
| Onboard battery | 320 kWh per trainset |
| Nominal capacity | 200 pax (seated + standing) |

## Ridership capacity

- **Per-train capacity:** 200 passengers
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 200 × 12 = **2,400 pphpd**
- **Network peak throughput (all lines, both directions):** 4 lines × 2 directions × 2,400 = **19,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **192,000 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): *(requires a coverage score)*

## Catchment

- City population: **220,000**
- Anchor-weighted coverage: — (set `[stats] coverage` in design.toml)
- Catchment population: *(run the planner with a fresh coverage score)*

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../lib/templates/energy-sites.toml`](../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Standard | 16 | 500 kW | 3000 kWh |
| **Total installed** | **16** | **7,700 kW** | **46,500 kWh** |

Aggregate station-rail charging power: **12,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 320 kWh battery covers running.

## Cost estimate

Rule-of-thumb unit rates (see [`CostAssumptions`](../../../design-py/src/osr_scenario/network_readme.py) to override per-country):

| Component | Unit cost | Quantity | Estimate |
|---|---|---|---|
| Civil track (double-track) | $2.0 M/km | 45.1 km | **$90.2 M** |
| Solar PV (installed) | $1.00/W | 7,700 kW | **$7.7 M** |
| Battery (power rating, 46,500 kWh ÷ 4 h) | $1.00/W | 11,625 kW | **$11.6 M** |
| Rolling stock (24 trainsets × 3 cars) | $1.0 M/car | 72 cars | **$72.0 M** |
| Stations (civil + fit-out) | $1.0 M/station | 29 stations | **$29.0 M** |
| Depots | $5.0 M/depot | 2 depots | **$10.0 M** |
| **Total capex (planning-grade)** | | | **$220.5 M** |

**Exclusions:** signalling / OCC / comms / cybersecurity, land acquisition, contingency reserve (typically 15–25 % of the above), design + engineering fees, financing. The above is a planning-grade bracket for sizing and stakeholder conversations, not a bid-ready estimate.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`samawah.toml`](samawah.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`samawah-network-map.png`](../../../docs/screenshots/samawah-network-map.png) | City-wide network map |
| [`samawah-network-map-detail.png`](../../../docs/screenshots/samawah-network-map-detail.png) | Detail-zoom render |
| [`samawah-corridor.geojson`](../../../docs/screenshots/samawah-corridor.geojson) | Line polylines + stations (GeoJSON) |

## Reproducibility

Run `python -m osr_planner --slug <slug> --bbox ... --population ...` to re-plan, then `python -m osr_scenario --design …/design.toml` + `python -m osr_scenario.render_map --design …/design.toml` + `python -m osr_scenario.network_readme --design …/design.toml --scenario …/scenario.toml --out …/README.md --population N` to regenerate this README.
