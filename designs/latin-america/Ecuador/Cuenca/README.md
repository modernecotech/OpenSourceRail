# Cuenca — Urban Rail Network

**Country:** EC · **Population:** 817,100

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Cuenca rail network on OpenStreetMap](cuenca-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`cuenca.corridor.geojson`](cuenca.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 48 |
| Interchange stations | 5 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 57.4% |
| Route length (double track) | 78.5 km |
| Revenue fleet | 68 × 3-car trainsets |
| Spare + cold-reserve | 9 × 3-car trainsets |
| Peak headway | 5 min |
| Service hours | 05:30 – 02:00 (≈ 20 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 26.5 km | 17 | 26 | E Mid ↔ W Outer |
| line-2 | 27.1 km | 16 | 26 | W Outer ↔ E Outer |
| line-3 | 24.9 km | 15 | 25 | NE Outer ↔ SW Mid |
| **Total** | **78.5 km** | **48 unique** | **77** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 3-car, 68 m |
| Max speed | 80 km/h |
| Onboard battery | 320 kWh per trainset |
| Nominal capacity | 360 pax (seated + standing, `light-metro-3car` per RFC 0008 §1) |

## Ridership capacity

- **Per-train capacity:** 360 passengers (`light-metro-3car`)
- **Peak frequency:** 12 trains/hour/direction (5-min headway)
- **Peak capacity per line per direction:** 360 × 12 = **4,320 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 4,320 = **25,920 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **259,200 passenger-trips/day**
- **Practical daily ridership estimate** (10–15 % of catchment): ≈ **46,901 – 70,352 trips/day**

## Catchment

- City population: **817,100**
- Anchor-weighted coverage: 57.4%
- Catchment population: **≈ 469,015** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 5 | 500 kW | 3000 kWh |
| Major | 22 | 400 kW | 2500 kWh |
| Standard | 13 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **46** | **22,700 kW** | **151,000 kWh** |

Aggregate station-rail charging power: **19,500 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 320 kWh battery covers running.

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters in rolling stock, open-source CBTC on commodity SBCs (no proprietary signalling vendor), no overhead catenary, and self-EPC overhead. Conventional metro budgets land 2–3× higher because of the line items OSR has architected away. `country-costs.toml` applies the per-country labour/material multiplier downstream.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (72.1 km @ €3.5 M/km) | €252 M |
| Elevated (4.9 km @ €18 M/km) | €87 M |
| Elevated-interchange premium (3 sites @ €20 M) | €60 M |
| **Civil subtotal** | **€400 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~11 t / 13-bay canopy delivered on two lorries, 3–5 day erection). Precast L-unit platform edge. Vertical circulation per archetype.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 2 | €0.4 M | €0.8 M |
| `standard` | 13 | €1.5 M | €20 M |
| `major` | 22 | €3.0 M | €66 M |
| `terminal` | 5 | €2.5 M | €12 M |
| `depot-terminal` | 1 | €3.0 M | €3.0 M |
| `interchange` | 3 | €4.5 M | €14 M |
| `interchange-elevated` | 2 | €4.5 M | €9.0 M |
| **Stations subtotal** | | | **€124 M** |

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
| `light-metro-3car` (revenue + spare + cold reserve) | 77 | €2.0 M | €154 M |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Signalling (open-source CBTC on commodity SBCs, RFC 0019) | 78.5 km × €0.4 M/km | €31 M |
| Traction power (**trackside** stationary PV + Na-ion + grid-tie at every station, no OCS, RFC 0002 §6) | 78.5 km × €0.8 M/km | €62 M |
| EPC integration + project management (7%) | on subtotal | €57 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | €400 M |
| Stations | €124 M |
| Depots | €40 M |
| Rolling stock | €154 M |
| Signalling + power | €92 M |
| EPC overhead (7%) | €57 M |
| **CAPEX total** | **€867 M** |
| Per-route-km | €11 M / km |
| Per-capita (city pop) | €1,061 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh cuenca`.

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Multilateral concessional loan (IBRD / AfDB / ADB class) | 60% | €520 M | 4.5% | 25 y, 5 y grace | €40 M / yr |
| Sovereign bonds (10-y benchmark + project) | 25% | €217 M | 9.5% | 25 y, 5 y grace | €25 M / yr |
| Government equity (no debt service) | 15% | €130 M | — | — | — |
| **Total** | **100%** | **€867 M** | | | **€65 M / yr** |

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | €6.2 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | €11 M |
| Signalling + comms maintenance | 5 % of signalling CAPEX | €1.5 M |
| Traction energy (137.4 GWh / yr) | trackside PV + Na-ion (RFC 0002) — **self-generated, €0 / yr** | €0 k |
| Labour (483 FTE) | ~6 FTE/route-km + 12 admin core × country median × 12 × engineer-premium 1.4 | €3.1 M |
| **OPEX subtotal** | | **€22 M / yr** |

_Annual fleet utilisation: 68 revenue trainsets × 20.5 h/day × 365 d/yr × 30 km/h commercial × 75% revenue factor = 11.4 M train-km / yr (~168 k km / trainset / yr)._

### Ticket pricing anchored to median income

Country median monthly income: **$410 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). Target affordability: monthly unlimited pass at 5 % of median income → single-trip price set by the 30:1 pass / trip ratio used by every operator in the affordability literature (STIB, Delhi Metro, Cairo Metro).

| Product | Price target |
|---|---|
| Single-trip fare | €0.63 (~$0.68 USD) |
| Day pass (3 trips) | €1.60 (15 % bulk discount) |
| Monthly unlimited pass | €18.86 (~5 % of median monthly income) |
| Annual pass | €207.46 (10 × monthly = ~1 free month) |

### Farebox & operating subsidy

Practical-ridership bracket = 5–10 % of urban population × 365 service-days. At the affordability-anchored fare:

| | Low scenario | High scenario |
|---|---|---|
| Annual paid trips | 14.9 M | 29.8 M |
| Farebox revenue | €9.4 M / yr | €19 M / yr |
| Farebox / OPEX recovery | 43% | 85% |
| Country policy-target recovery (diagnostic) | 55% | 55% |
| Operating shortfall (gov subsidy required) | €13 M / yr | €3.3 M / yr |
| **Total annual government burden** (debt service + OPEX shortfall) | **€77 M / yr** | **€68 M / yr** |

**Caveats:** The funding-stack 60/25/15 split, the 5 % income-share affordability target, and the 5–10 % daily-pax bracket are project-level defaults. Real deployments will negotiate the share with the financing institutions and will tune fares iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`cuenca.toml`](cuenca.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`cuenca-network-map.png`](cuenca-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`cuenca.corridor.geojson`](cuenca.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`cuenca.stations.json`](cuenca.stations.json) | Machine-readable station list |
| [`cuenca.design-quality.yaml`](cuenca.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug cuenca

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug cuenca \
    --sidecar .cache/osr-pipeline/rasters/cuenca.grid.json \
    --out-dir designs/.../Cuenca

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../cuenca.toml \
    --out designs/.../README.md
```

`scripts/regenerate-cuenca.sh` chains steps 3 + drift tests into a single command.
