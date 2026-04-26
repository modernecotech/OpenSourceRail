# Kampala — Urban Rail Network

**Country:** UG · **Population:** 1,875,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Kampala rail network on OpenStreetMap](kampala-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`kampala.corridor.geojson`](kampala.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 4 |
| Unique stations | 98 |
| Interchange stations | 12 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 24.0% |
| Route length (double track) | 201.1 km |
| Revenue fleet | 144 × 4-car trainsets |
| Spare + cold-reserve | 16 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 39.8 km | 22 | 32 | W Outer ↔ E Outer |
| line-2 | 36.9 km | 21 | 30 | S Outer ↔ N Outer |
| line-3 | 34.6 km | 20 | 28 | S Outer ↔ N Outer |
| line-4 | 89.9 km | 36 | 70 | NW Outer ↔ NW Outer |
| **Total** | **201.1 km** | **98 unique** | **160** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 4-car, 90 m |
| Max speed | 90 km/h |
| Onboard battery | 460 kWh per trainset |
| Nominal capacity | 540 pax (seated + standing, `metro-4car` per RFC 0008 §1) |

## Ridership capacity

- **Per-train capacity:** 540 passengers (`metro-4car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 540 × 12 = **6,480 pphpd**
- **Network peak throughput (all lines, both directions):** 4 lines × 2 directions × 6,480 = **51,840 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **518,400 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **45,000 – 67,500 trips/day**

## Catchment

- City population: **1,875,000**
- Anchor-weighted coverage: 24.0%
- Catchment population: **≈ 450,000** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 12 | 500 kW | 3000 kWh |
| Major | 35 | 400 kW | 2500 kWh |
| Standard | 46 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **99** | **41,300 kW** | **270,500 kWh** |

Aggregate station-rail charging power: **29,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 460 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters in rolling stock, open-source CBTC on commodity SBCs (no proprietary signalling vendor), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (192.0 km @ €3.5 M/km) | €672 M |
| Elevated (8.2 km @ €18 M/km) | €148 M |
| Elevated-interchange premium (7 sites @ €20 M) | €140 M |
| **Civil subtotal** | **€960 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `standard` | 46 | €1.5 M | €69 M |
| `major` | 35 | €3.0 M | €105 M |
| `terminal` | 5 | €2.5 M | €12 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 12 | €4.5 M | €54 M |
| **Stations subtotal** | | | **€244 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 5 | €3.0 M | €15 M |
| **Depots subtotal** | | | **€40 M** |

### Rolling stock

Per-trainset BOM at OSR-discipline pricing: **onboard** Na-ion traction battery (~$80/kWh, RFC 0021 §3 — distinct from the trackside stationary battery in the *Systems* section below), tier-2 PMSM motors + SiC inverters (RFC 0022 §10, RFC 0008 §3.2), DIY safety electronics (~$5 680/trainset, RFC 0019), aluminium-extrusion or steel space-frame body. Motors and onboard batteries appear here ONLY — never re-billed elsewhere in the cost stack.

| Item | Count | Unit | Subtotal |
|---|---|---|---|
| `metro-4car` (revenue + spare + cold reserve) | 160 | €3.0 M | €480 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Signalling (open-source CBTC on commodity SBCs, RFC 0019) | 201.1 km × €0.4 M/km | €80 M |
| Traction power (**trackside** stationary PV + Na-ion + grid-tie at every station, no OCS, RFC 0002 §6) | 201.1 km × €0.8 M/km | €160 M |
| EPC integration + project management (7%) | on subtotal | €137 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €960 M |
| Stations | €244 M |
| Depots | €40 M |
| Rolling stock | €480 M |
| Signalling + power | €240 M |
| EPC overhead (7%) | €137 M |
| **CAPEX total** | **€2.10 bn** |
| Per-route-km | €10 M / km |
| Per-capita (city pop) | €1,121 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh kampala`.

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €1.26 bn | 3.8% | 30 y, 7 y grace | €83 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €525 M | 14.0% | 30 y, 7 y grace | €77 M / yr |
| Government equity (no debt service) | 15% | €315 M | — | — | — |
| **Total** | **100%** | **€2.10 bn** | | | **€161 M / yr** |

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €19 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €25 M |
| Signalling + comms maintenance | 5 % of signalling CAPEX | €4.0 M |
| Traction energy (452.5 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (1,219 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €2.7 M |
| **OPEX subtotal** | | **€51 M / yr** |

_Annual fleet utilisation: 144 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 28.3 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$145 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Target affordability: monthly unlimited pass at 5 % of median income → single-trip price set by the 30:1 pass / trip ratio used by every operator in the affordability literature (STIB, Delhi Metro, Cairo Metro).

| Product | Price target |
|---|---|
| Single-trip fare | €0.22 (~$0.24 USD) |
| Day pass (3 trips) | €0.57 (15 % bulk discount) |
| Monthly unlimited pass | €6.67 (~5 % of median monthly income) |
| Annual pass | €73.37 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 34.2 M | 68.4 M |
| Farebox revenue | €7.6 M / yr | €15 M / yr |
| Farebox / OPEX recovery | 15% | 30% |
| Country policy-target recovery (diagnostic) | 40% | 40% |
| Operating shortfall (gov subsidy required) | €43 M / yr | €36 M / yr |
| **Total annual government burden** (debt service + OPEX shortfall) | **€204 M / yr** | **€196 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`kampala.toml`](kampala.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`kampala-network-map.png`](kampala-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`kampala.corridor.geojson`](kampala.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`kampala.stations.json`](kampala.stations.json) | Machine-readable station list |
| [`kampala.design-quality.yaml`](kampala.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug kampala

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug kampala \
    --sidecar .cache/osr-pipeline/rasters/kampala.grid.json \
    --out-dir designs/.../Kampala

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../kampala.toml \
    --out designs/.../README.md
```

`scripts/regenerate-kampala.sh` chains steps 3 + drift tests into a single command.
