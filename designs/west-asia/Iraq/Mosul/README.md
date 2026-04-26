# Mosul — Urban Rail Network

**Country:** IQ · **Population:** 1,940,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Mosul rail network on OpenStreetMap](mosul-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`mosul.corridor.geojson`](mosul.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 5 |
| Unique stations | 60 |
| Interchange stations | 4 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 38.2% |
| Route length (double track) | 144.6 km |
| Revenue fleet | 108 × 4-car trainsets |
| Spare + cold-reserve | 14 × 4-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 29.0 km | 14 | 25 | SW Mid ↔ E Outer |
| line-2 | 31.5 km | 12 | 26 | SE Outer ↔ NW Outer |
| line-3 | 32.3 km | 11 | 27 | NW Outer ↔ E Mid |
| line-4 | 27.6 km | 12 | 24 | N Mid ↔ S Outer |
| line-5 | 24.2 km | 11 | 20 | NE Outer ↔ W Mid |
| **Total** | **144.6 km** | **60 unique** | **122** | |

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
- **Network peak throughput (all lines, both directions):** 5 lines × 2 directions × 6,480 = **64,800 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **648,000 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **74,108 – 111,162 trips/day**

## Catchment

- City population: **1,940,000**
- Anchor-weighted coverage: 38.2%
- Catchment population: **≈ 741,080** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 4 | 500 kW | 3000 kWh |
| Major | 18 | 400 kW | 2500 kWh |
| Standard | 24 | 300 kW | 2000 kWh |
| Terminal | 9 | 500 kW | 3000 kWh |
| **Total installed** | **56** | **25,900 kW** | **172,000 kWh** |

Aggregate station-rail charging power: **21,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 460 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters in rolling stock, open-source CBTC on commodity SBCs (no proprietary signalling vendor), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (117.3 km @ €3.5 M/km) | €411 M |
| Elevated (26.5 km @ €18 M/km) | €477 M |
| Elevated-interchange premium (5 sites @ €20 M) | €100 M |
| **Civil subtotal** | **€988 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 4 | €0.4 M | €1.6 M |
| `standard` | 24 | €1.5 M | €36 M |
| `major` | 18 | €3.0 M | €54 M |
| `terminal` | 9 | €2.5 M | €22 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange-elevated` | 4 | €4.5 M | €18 M |
| **Stations subtotal** | | | **€135 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 9 | €3.0 M | €27 M |
| **Depots subtotal** | | | **€52 M** |

### Rolling stock

Per-trainset BOM at OSR-discipline pricing: **onboard** Na-ion traction battery (~$80/kWh, RFC 0021 §3 — distinct from the trackside stationary battery in the *Systems* section below), tier-2 PMSM motors + SiC inverters (RFC 0022 §10, RFC 0008 §3.2), DIY safety electronics (~$5 680/trainset, RFC 0019), aluminium-extrusion or steel space-frame body. Motors and onboard batteries appear here ONLY — never re-billed elsewhere in the cost stack.

| Item | Count | Unit | Subtotal |
|---|---|---|---|
| `metro-4car` (revenue + spare + cold reserve) | 122 | €3.0 M | €366 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Signalling (open-source CBTC on commodity SBCs, RFC 0019) | 144.6 km × €0.4 M/km | €58 M |
| Traction power (**trackside** stationary PV + Na-ion + grid-tie at every station, no OCS, RFC 0002 §6) | 144.6 km × €0.8 M/km | €115 M |
| EPC integration + project management (7%) | on subtotal | €120 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €988 M |
| Stations | €135 M |
| Depots | €52 M |
| Rolling stock | €366 M |
| Signalling + power | €173 M |
| EPC overhead (7%) | €120 M |
| **CAPEX total** | **€1.83 bn** |
| Per-route-km | €13 M / km |
| Per-capita (city pop) | €945 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh mosul`.

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €1.10 bn | 4.0% | 25 y, 5 y grace | €81 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €458 M | 8.5% | 25 y, 5 y grace | €48 M / yr |
| Government equity (no debt service) | 15% | €275 M | — | — | — |
| **Total** | **100%** | **€1.83 bn** | | | **€129 M / yr** |

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €15 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €23 M |
| Signalling + comms maintenance | 5 % of signalling CAPEX | €2.9 M |
| Traction energy (339.4 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (880 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €5.2 M |
| **OPEX subtotal** | | **€46 M / yr** |

_Annual fleet utilisation: 108 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 21.2 M train-km / yr (~196 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$380 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Target affordability: monthly unlimited pass at 5 % of median income → single-trip price set by the 30:1 pass / trip ratio used by every operator in the affordability literature (STIB, Delhi Metro, Cairo Metro).

| Product | Price target |
|---|---|
| Single-trip fare | €0.58 (~$0.63 USD) |
| Day pass (3 trips) | €1.49 (15 % bulk discount) |
| Monthly unlimited pass | €17.48 (~5 % of median monthly income) |
| Annual pass | €192.28 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 35.4 M | 70.8 M |
| Farebox revenue | €21 M / yr | €41 M / yr |
| Farebox / OPEX recovery | 45% | 89% |
| Country policy-target recovery (diagnostic) | 45% | 45% |
| Operating shortfall (gov subsidy required) | €26 M / yr | €4.9 M / yr |
| **Total annual government burden** (debt service + OPEX shortfall) | **€155 M / yr** | **€134 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`mosul.toml`](mosul.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`mosul-network-map.png`](mosul-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`mosul.corridor.geojson`](mosul.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`mosul.stations.json`](mosul.stations.json) | Machine-readable station list |
| [`mosul.design-quality.yaml`](mosul.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug mosul

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug mosul \
    --sidecar .cache/osr-pipeline/rasters/mosul.grid.json \
    --out-dir designs/.../Mosul

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../mosul.toml \
    --out designs/.../README.md
```

`scripts/regenerate-mosul.sh` chains steps 3 + drift tests into a single command.
