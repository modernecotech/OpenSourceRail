# Basra — Urban Rail Network

**Country:** IQ · **Population:** 3,955,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Basra rail network on OpenStreetMap](basra-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`basra.corridor.geojson`](basra.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 7 |
| Unique stations | 118 |
| Interchange stations | 18 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 54.2% |
| Route length (double track) | 289.0 km |
| Revenue fleet | 211 × 6-car trainsets |
| Spare + cold-reserve | 25 × 6-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 46.5 km | 20 | 38 | N Outer ↔ SE Mid |
| line-2 | 35.4 km | 17 | 29 | SE Outer ↔ NW Inner |
| line-3 | 30.8 km | 16 | 26 | NE Mid ↔ SW Mid |
| line-4 | 34.4 km | 13 | 28 | E Inner ↔ SW Outer |
| line-5 | 27.7 km | 14 | 24 | S Inner ↔ N Mid |
| line-6 | 33.8 km | 13 | 28 | SW Outer ↔ NE Inner |
| line-7 | 80.4 km | 26 | 63 | NW Mid ↔ NW Mid |
| **Total** | **289.0 km** | **118 unique** | **236** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 6-car, 138 m |
| Max speed | 90 km/h |
| Onboard battery | 720 kWh per trainset |
| Nominal capacity | 900 pax (seated + standing, `metro-6car` per RFC 0008 §1) |

## Ridership capacity

- **Per-train capacity:** 900 passengers (`metro-6car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 900 × 12 = **10,800 pphpd**
- **Network peak throughput (all lines, both directions):** 7 lines × 2 directions × 10,800 = **151,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **1,512,000 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **214,361 – 321,541 trips/day**

## Catchment

- City population: **3,955,000**
- Anchor-weighted coverage: 54.2%
- Catchment population: **≈ 2,143,610** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 18 | 500 kW | 3000 kWh |
| Major | 36 | 400 kW | 2500 kWh |
| Standard | 34 | 300 kW | 2000 kWh |
| Terminal | 11 | 500 kW | 3000 kWh |
| **Total installed** | **100** | **44,100 kW** | **285,000 kWh** |

Aggregate station-rail charging power: **39,000 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 720 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters in rolling stock, open-source CBTC on commodity SBCs (no proprietary signalling vendor), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (250.2 km @ €3.5 M/km) | €876 M |
| Elevated (37.2 km @ €18 M/km) | €669 M |
| Elevated-interchange premium (8 sites @ €20 M) | €160 M |
| **Civil subtotal** | **€1.71 bn** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 19 | €0.4 M | €7.6 M |
| `standard` | 34 | €1.5 M | €51 M |
| `major` | 36 | €3.0 M | €108 M |
| `terminal` | 11 | €2.5 M | €28 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange` | 4 | €4.5 M | €18 M |
| `interchange-elevated` | 14 | €4.5 M | €63 M |
| **Stations subtotal** | | | **€278 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | €25 M | €25 M |
| `layup-minimal` | 11 | €3.0 M | €33 M |
| **Depots subtotal** | | | **€58 M** |

### Rolling stock

Per-trainset BOM at OSR-discipline pricing: **onboard** Na-ion traction battery (~$80/kWh, RFC 0021 §3 — distinct from the trackside stationary battery in the *Systems* section below), tier-2 PMSM motors + SiC inverters (RFC 0022 §10, RFC 0008 §3.2), DIY safety electronics (~$5 680/trainset, RFC 0019), aluminium-extrusion or steel space-frame body. Motors and onboard batteries appear here ONLY — never re-billed elsewhere in the cost stack.

| Item | Count | Unit | Subtotal |
|---|---|---|---|
| `metro-6car` (revenue + spare + cold reserve) | 236 | €4.5 M | €1.06 bn |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Signalling (open-source CBTC on commodity SBCs, RFC 0019) | 289.0 km × €0.4 M/km | €115 M |
| Traction power (**trackside** stationary PV + Na-ion + grid-tie at every station, no OCS, RFC 0002 §6) | 289.0 km × €0.8 M/km | €230 M |
| EPC integration + project management (7%) | on subtotal | €241 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €1.71 bn |
| Stations | €278 M |
| Depots | €58 M |
| Rolling stock | €1.06 bn |
| Signalling + power | €345 M |
| EPC overhead (7%) | €241 M |
| **CAPEX total** | **€3.69 bn** |
| Per-route-km | €13 M / km |
| Per-capita (city pop) | €933 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh basra`.

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €2.21 bn | 4.0% | 25 y, 5 y grace | €163 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €922 M | 8.5% | 25 y, 5 y grace | €97 M / yr |
| Government equity (no debt service) | 15% | €553 M | — | — | — |
| **Total** | **100%** | **€3.69 bn** | | | **€260 M / yr** |

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €42 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €41 M |
| Signalling + comms maintenance | 5 % of signalling CAPEX | €5.7 M |
| Traction energy (994.6 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (1,746 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €10 M |
| **OPEX subtotal** | | **€99 M / yr** |

_Annual fleet utilisation: 211 revenue trainsets × 20.5 h/day × 365 d/yr × 35 km/h commercial × 75% revenue factor = 41.4 M train-km / yr (~196 k km / trainset / yr)._

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
| Annual paid trips | 72.2 M | 144.4 M |
| Farebox revenue | €42 M / yr | €84 M / yr |
| Farebox / OPEX recovery | 42% | 85% |
| Country policy-target recovery (diagnostic) | 45% | 45% |
| Operating shortfall (gov subsidy required) | €57 M / yr | €15 M / yr |
| **Total annual government burden** (debt service + OPEX shortfall) | **€318 M / yr** | **€276 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`basra.toml`](basra.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`basra-network-map.png`](basra-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`basra.corridor.geojson`](basra.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`basra.stations.json`](basra.stations.json) | Machine-readable station list |
| [`basra.design-quality.yaml`](basra.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug basra

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug basra \
    --sidecar .cache/osr-pipeline/rasters/basra.grid.json \
    --out-dir designs/.../Basra

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../basra.toml \
    --out designs/.../README.md
```

`scripts/regenerate-basra.sh` chains steps 3 + drift tests into a single command.
