# Baghdad — Urban Rail Network

**Country:** IQ · **Population:** 8,000,000

Auto-planned by [`osr_planner`](../../../design-py/src/osr_planner/) using the linear-logic algorithm on Overpass-verified OpenStreetMap data. Every station sits on an aggregated POI cluster; every line polyline follows the OSM arterial graph (trunk / primary / secondary / tertiary — residential streets excluded, so lines cannot zigzag through a residential grid).

## Network maps

### Suburban / regional map — full network

![Baghdad full rail network including suburban lines](baghdad-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

### Inner-Baghdad map — urban core detail

![Baghdad urban-core detail — central district](baghdad-network-map-detail.png)

*8 km radius around the city centre at a legible street-grid zoom. Shows interchange density, central-business-district stations, and where the radial lines converge on the hub.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`baghdad-corridor.geojson`](baghdad-corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 9 |
| Unique stations | 121 |
| Interchange stations | 31 |
| Multi-line transfer reachability | 89% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | — (set `[stats] coverage` in design.toml) |
| Route length (double track) | 476.6 km |
| Revenue fleet | 90 × 3-car trainsets |
| Spare + cold-reserve | 18 × 3-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 23:30 (≈ 18 h/day) |

## Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| Line 1 | 52.6 km | 27 | 10 | Basmaya ↔ Sab al Bor |
| Line 2 | 70.9 km | 25 | 10 | Mstshfa Tb Alasnan ↔ Tajiyat / Taji New Housing |
| Line 3 | 57.2 km | 24 | 10 | Madinat Al Ward (SW Nahrawan desert) ↔ Abu Ghraib New Developments |
| Line 4 | 35.9 km | 23 | 10 | Mashreq University ↔ Hospital 12 |
| Line 5 | 45.1 km | 21 | 10 | Ibn Al-khateeb Hospital ↔ Al-Taji 2nd Health Center |
| Line 6 | 36.9 km | 21 | 10 | Al Alam ↔ Alzhraa private hospital |
| Line 7 | 43.0 km | 18 | 10 | Al-A'amiriya ↔ Mrkz Shy Albawyh |
| Line 8 | 36.7 km | 18 | 10 | Jam'h Klkamsh Alahlyh ↔ Mstwsf Shy Bwb Alsham |
| Ring Line | 98.4 km | 8 | 10 | Hospital 12 ↔ Madinat Al Ward (SW Nahrawan desert) |
| **Total** | **476.6 km** | **121 unique** | **90** | |

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
- **Network peak throughput (all lines, both directions):** 9 lines × 2 directions × 2,400 = **43,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **432,000 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): *(requires a coverage score)*

## Catchment

- City population: **8,000,000**
- Anchor-weighted coverage: — (set `[stats] coverage` in design.toml)
- Catchment population: *(run the planner with a fresh coverage score)*

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../lib/templates/energy-sites.toml`](../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Standard | 98 | 400 kW | 2500 kWh |
| **Total installed** | **98** | **44,300 kW** | **270,500 kWh** |

Aggregate station-rail charging power: **59,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 320 kWh battery covers running.

## Cost estimate

Rule-of-thumb unit rates (see [`CostAssumptions`](../../../design-py/src/osr_scenario/network_readme.py) to override per-country):

| Component | Unit cost | Quantity | Estimate |
|---|---|---|---|
| Civil track (at-grade, double-track, radials) | $2.0 M/km | 321.5 km (85 % of radial route) | **$643.0 M** |
| Bridges / viaducts on radials (river + highway crossings) | $20.0 M/km | 56.7 km (15 % of radial route) | **$1134.7 M** |
| Ring line (dedicated viaduct, straight across suburbs) | $20.0 M/km | 98.4 km (100 % viaduct) | **$1967.3 M** |
| Solar PV (installed) | $1.00/W | 44,300 kW | **$44.3 M** |
| Battery (power rating, 270,500 kWh ÷ 4 h) | $1.00/W | 67,625 kW | **$67.6 M** |
| Rolling stock (108 trainsets × 3 cars) | $1.0 M/car | 324 cars | **$324.0 M** |
| Stations (civil + fit-out) | $1.0 M/station | 121 stations | **$121.0 M** |
| Depots | $5.0 M/depot | 2 depots | **$10.0 M** |
| **Total capex (planning-grade)** | | | **$4,311.9 M** |

**Exclusions:** signalling / OCC / comms / cybersecurity, land acquisition, contingency reserve (typically 15–25 % of the above), design + engineering fees, financing. The above is a planning-grade bracket for sizing and stakeholder conversations, not a bid-ready estimate.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`baghdad.toml`](baghdad.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`baghdad-network-map.png`](baghdad-network-map.png) | City-wide network map |
| [`baghdad-network-map-detail.png`](baghdad-network-map-detail.png) | Detail-zoom render |
| [`baghdad-corridor.geojson`](baghdad-corridor.geojson) | Line polylines + stations (GeoJSON) |

## Reproducibility

Run `python -m osr_planner --slug <slug> --bbox ... --population ...` to re-plan, then `python -m osr_scenario --design …/design.toml` + `python -m osr_scenario.render_map --design …/design.toml` + `python -m osr_scenario.network_readme --design …/design.toml --scenario …/scenario.toml --out …/README.md --population N` to regenerate this README.
