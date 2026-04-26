# Samawah — Urban Rail Network

**Country:** IQ · **Population:** 373,770

Auto-planned by [`osr_planner`](../../../design-py/src/osr_planner/) using the linear-logic algorithm on Overpass-verified OpenStreetMap data. Every station sits on an aggregated POI cluster; every line polyline follows the OSM arterial graph (trunk / primary / secondary / tertiary — residential streets excluded, so lines cannot zigzag through a residential grid).

## Network maps

### Suburban / regional map — full network

![Samawah full rail network including suburban lines](city-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

### Inner-Samawah map — urban core detail

![Samawah urban-core detail — central district](city-network-map-detail.png)

*8 km radius around the city centre at a legible street-grid zoom. Shows interchange density, central-business-district stations, and where the radial lines converge on the hub.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`city-corridor.geojson`](city-corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 40 |
| Interchange stations | 0 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | — (set `[stats] coverage` in design.toml) |
| Route length (double track) | 40.2 km |
| Revenue fleet | 38 × 3-car trainsets |
| Spare + cold-reserve | 6 × 3-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 23:30 (≈ 18 h/day) |

## Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 11.5 km | 14 | 13 | ال مطشر ↔ مستشفى الالماني |
| line-2 | 11.3 km | 12 | 13 | مستوصف صحي حي العسكري ↔ جامعة الامام جعفر الصادق فرع المثنى |
| line-3 | 17.5 km | 14 | 18 | سيطرة ↔ مدرسة الوهج الابتدائية المختلطة  |
| **Total** | **40.2 km** | **40 unique** | **38** | |

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
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 2,400 = **14,400 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **144,000 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): *(requires a coverage score)*

## Catchment

- City population: **373,770**
- Anchor-weighted coverage: — (set `[stats] coverage` in design.toml)
- Catchment population: *(run the planner with a fresh coverage score)*

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../lib/templates/energy-sites.toml`](../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| **Total installed** | **0** | **0 kW** | **0 kWh** |

Aggregate station-rail charging power: **13,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 320 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters in rolling stock, open-source CBTC on commodity SBCs (no proprietary signalling vendor), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (39.9 km @ €3.5 M/km) | €140 M |
| Elevated (0.3 km @ €18 M/km) | €4.6 M |
| **Civil subtotal** | **€144 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 1 | €0.4 M | €0.4 M |
| `standard` | 19 | €1.5 M | €28 M |
| `major` | 14 | €3.0 M | €42 M |
| `terminal` | 5 | €2.5 M | €12 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| **Stations subtotal** | | | **€86 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 5 | €3.0 M | €15 M |
| **Depots subtotal** | | | **€40 M** |

### Rolling stock

Per-trainset BOM at OSR-discipline pricing: commodity Na-ion cells (~$80/kWh, RFC 0021), tier-2 PMSM motors + SiC inverters (RFC 0022 §10, RFC 0008 §3.2), DIY safety electronics (~$5 680/trainset, RFC 0019), aluminium-extrusion or steel space-frame body.

| Item | Count | Unit | Subtotal |
|---|---|---|---|
| `light-metro-3car` (revenue + spare + cold reserve) | 44 | €2.0 M | €88 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Signalling (open-source CBTC on commodity SBCs, RFC 0019) | 40.2 km × €0.4 M/km | €16 M |
| Traction power (distributed PV + Na-ion, no OCS, RFC 0002) | 40.2 km × €0.8 M/km | €32 M |
| EPC integration + project management (7%) | on subtotal | €28 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €144 M |
| Stations | €86 M |
| Depots | €40 M |
| Rolling stock | €88 M |
| Signalling + power | €48 M |
| EPC overhead (7%) | €28 M |
| **CAPEX total** | **€435 M** |
| Per-route-km | €11 M / km |
| Per-capita (city pop) | €1,165 / person |

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`samawah.toml`](samawah.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`city-network-map.png`](city-network-map.png) | City-wide network map |
| [`city-network-map-detail.png`](city-network-map-detail.png) | Detail-zoom render |
| [`city-corridor.geojson`](city-corridor.geojson) | Line polylines + stations (GeoJSON) |

## Reproducibility

Run `python -m osr_planner --slug <slug> --bbox ... --population ...` to re-plan, then `python -m osr_scenario --design …/design.toml` + `python -m osr_scenario.render_map --design …/design.toml` + `python -m osr_scenario.network_readme --design …/design.toml --scenario …/scenario.toml --out …/README.md --population N` to regenerate this README.
