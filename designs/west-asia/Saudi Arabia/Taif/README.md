# Taif — Urban Rail Network

**Country:** SA · **Population:** 700,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Taif rail network on OpenStreetMap](taif-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`taif.corridor.geojson`](taif.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 42 |
| Interchange stations | 3 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 40.8% |
| Route length (double track) | 73.5 km |
| Revenue fleet | 105 × 3-car trainsets |
| Revenue fleet passenger capacity | 37,800 AW2 pax (50,400 AW3 crush) |
| Spare + cold-reserve | 12 × 3-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 24.4 km | 14 | 39 | SW Outer ↔ N Outer |
| line-2 | 25.1 km | 15 | 40 | SE Outer ↔ NW Outer |
| line-3 | 23.9 km | 13 | 38 | W Mid ↔ NE Outer |
| **Total** | **73.5 km** | **42 unique** | **117** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 3-car, 51 m |
| Max speed | 90 km/h |
| Onboard battery | 360 kWh per trainset |
| Seats | 60 longitudinal seats |
| Nominal capacity (AW2) | 360 pax (seated + standing, `light-metro-3car` per RFC 0008 §1) |
| Crush capacity (AW3) | 480 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 37,800 AW2 pax (50,400 AW3 crush) |
| Total fleet capacity | 42,120 AW2 pax (56,160 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 360 AW2 passengers (`light-metro-3car`)
- **Revenue fleet simultaneous capacity:** 105 × 360 = **37,800 AW2 passengers** (50,400 AW3 crush)
- **Total fleet passenger capacity:** 117 × 360 = **42,120 AW2 passengers** (56,160 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 360 × 20 = **7,200 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 7,200 = **43,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **432,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **345,600 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% active-rider uptake of catchment): ≈ **142,800 – 257,040 paid trips/day** (71,400 – 128,520 daily active riders at 2 trips/rider/day)

## Catchment

- City population: **700,000**
- Anchor-weighted coverage: 40.8%
- Catchment population: **≈ 285,600** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 3 | 500 kW | 3000 kWh |
| Major | 12 | 400 kW | 2500 kWh |
| Standard | 20 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **41** | **19,800 kW** | **134,000 kWh** |

Aggregate station-rail charging power: **23,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 360 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **87.8 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 12.0 kWh/km | 3 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 294 kWh | 24.5 km average line length |
| Onboard battery coverage | 1.2× average line run | 360 kWh usable pack |
| Average 60 s dwell charge | 9.4 kWh/stop | 565 kW average charger across stops |
| Stops to refill one trainset pack | 38 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 99 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 481 MWh/day | 37,094 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 382 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 87.8 MW / 439 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 134 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (71.1 km @ $3.0 M/km) | $213 M |
| Elevated (2.2 km @ $12.0 M/km) | $26 M |
| Elevated-interchange premium (1 sites @ $4.50 M) | $4.5 M |
| **Civil subtotal** | **$244 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 1 | $600 k | $600 k |
| `standard` | 20 | $2.50 M | $50 M |
| `major` | 12 | $4.50 M | $54 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 3 | $12.0 M | $36 M |
| **Stations subtotal** | | | **$168 M** |

### Depots

At-grade portal-frame workshop sheds; pit tracks with stinger + portable wheel lathe (no overhead bridge crane); on-site PV array; Na-ion stationary storage; no traction substation.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `main-heavy` | 1 | $12.0 M | $12 M |
| `layup-minimal` | 5 | $2.0 M | $10 M |
| **Depots subtotal** | | | **$22 M** |

### Rolling stock

Rolling stock is costed at the **delivered production planning unit: $1.4 M per self-contained car**. The raw 3-car light-metro BOM floor remains 592,840 USD direct material plus 35 % assembly allowance = 800,334 USD per consist, but city CAPEX now adds production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. Motors, sensors, train-control computers, onboard batteries, roof PV, and charge hardware appear here ONLY — never re-billed elsewhere in the city cost stack.

| Per-car cost bucket | Basis | Cost |
|---|---|---|
| Direct material BOM floor | Welded frame, panels, glazing, doors, bogies, traction, batteries, HVAC, electronics, interiors | $267 k |
| Production labour + shop overhead | Cut/bend/weld, fit-out, harnessing, paint, factory supervision, utilities, rework reserve | $420 k |
| Fixtures, tooling, QA, certification evidence | Jigs/fixtures, dimensional QA, EN 15085/45545 evidence, supplier audits, homologation dossier amortisation | $310 k |
| Logistics, warranty, spares, commissioning | Freight, duty, insurance, initial spares/tools, manuals/training, site testing, acceptance runs | $403 k |
| **Total per car** | Delivered production planning unit | **$1.4 M** |

| Item | Count | Unit | Subtotal |
|---|---|---|---|
| `light-metro-3car` (revenue + spare + cold reserve) | 117 | $4.20 M | $491 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 351 | $100 k | $35 M |
| High sensitivity check | 351 | $200 k | $70 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 87,800 kW @ $700/kW | $61 M |
| Grid interconnection / PPA tie-in | 87,800 kW @ $100/kW | $8.8 M |
| Annual generation proxy | 87.8 MW × 5.0 peak-sun-h/day × 365 d/yr | 160.2 GWh/yr |
| **Dedicated solar plant subtotal** | | **$70 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 73.5 km × $0.050 M/km | $3.7 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $17 M |
| EPC integration + project management (7%) | on subtotal | $69 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $244 M |
| Stations | $168 M |
| Depots | $22 M |
| Rolling stock | $491 M |
| Railway production plant | $35 M |
| Dedicated solar power plant | $70 M |
| Residual train-control wayside + charging microgrids | $20 M |
| EPC overhead (7%) | $69 M |
| **CAPEX total** | **$1.12 bn** |
| Per-route-km | $15 M / km |
| Per-capita (city pop) | $1,600 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh taif`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–5** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 6** and runs for **35 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–5) | **$34 M / yr** | $48 |
| Steady-state, low-ridership (year 6+) | **$0 k / yr** | $0 |
| Steady-state, high-ridership (year 6+) | **$0 k / yr** | $0 |
| Steady-state, operating-neutral revenue case | **$22 M / yr** | $32 |
| Lifecycle envelope (yr 1–40, low scenario) | **$168 M cumulative** | $240 |
| Lifecycle envelope (yr 1–40, high scenario) | **$168 M cumulative** | $240 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$952 M cumulative** | $1,360 |

_Population basis: 700,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $0 k / yr → $0 k / yr; surplus applied to debt support is $22 M / yr → $22 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $448 M | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $560 M | 2.0% | 40 y, 5 y grace | $22 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 4.5% | 40 y, 5 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $112 M | — | — | — |
| **Total** | **100%** | **$1.12 bn** | | | **$22 M / yr** |

_During the 5-year grace period the public sponsor pays interest only on repayable debt — concessional loan $11 M / yr + fallback bonds $0 k / yr = **$11 M / yr** total. The $448 M grant tranche carries no repayment or coupon. Government equity is drawn across construction ($22 M / yr × 5 yr). Principal repayment begins in year 6 on a 35-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $20 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $8.7 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $183 k |
| Traction energy (175.5 GWh / yr) | 37,094 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 3 cars × 4.0 kWh/car-km; on-site PV 36.1 GWh/yr + dedicated solar plant 87.8 MW / 160.2 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $1.1 M |
| Labour (467 FTE) | driverless roster: OCC/remote 77, station/platform 141, passenger service 42, fleet maintenance 84, infrastructure/energy 87, admin/training 36; no train drivers × country median × 12 × engineer-premium 1.4 | $13 M |
| **OPEX subtotal** | | **$43 M / yr** |

_Annual service work: 37,094 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 14.6 M train-km / yr (43.9 M car-km / yr). On-site PV covers 36.1 GWh/yr and the dedicated solar plant adds 160.2 GWh/yr against 175.5 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$1,700 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $4.53 |
| Day pass (3 trips) | $11.56 (15 % bulk discount) |
| Monthly unlimited pass | $136.00 (~8 % of median monthly income) |
| Annual pass | $1496.00 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = daily active riders at 25-45% of catchment, converted to paid trips at 2 trips/rider/day and capped by practical service capacity (345,600 trips/day). Annual paid trips multiply daily paid trips by 365 service-days at the operating-neutral fare. The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily active riders | 71,400 | 128,520 | 6,909 |
| Daily active riders / catchment | 25% | 45% | 2% |
| Paid trips / active rider | 2 | 2 | 2 |
| Daily paid trips | 142,800 | 257,040 | 13,817 |
| Daily paid trips / city population | 20% | 37% | 2% |
| Annual paid trips | 52.1 M | 93.8 M | 5.0 M |
| Farebox revenue | $236 M / yr | $425 M / yr | $23 M / yr |
| Station shop leases | $5.8 M / yr | $5.8 M / yr | $5.8 M / yr |
| Advertising boards | $14 M / yr | $14 M / yr | $14 M / yr |
| **Total revenue** | **$256 M / yr** | **$445 M / yr** | **$43 M / yr** |
| Revenue / OPEX recovery | 597% | 1038% | 100% |
| Country farebox-only policy target (diagnostic) | 85% | 85% | 85% |
| Gross repayable-debt service + residual OPEX subsidy | $22 M / yr | $22 M / yr | **$22 M / yr** |
| Operating surplus applied to debt support | -$22 M / yr | -$22 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $0 k / yr | $0 k / yr | **$22 M / yr** |
| Operating surplus after OPEX (before debt support) | $213 M / yr | $402 M / yr | $0 / yr |

_Commercial-revenue assumptions: 6,080 m² of station shop/kiosk leases at $90/m²/month and 1,176 advertising boards at $1190/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-active-rider bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`taif.toml`](taif.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`taif-network-map.png`](taif-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`taif.corridor.geojson`](taif.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`taif.stations.json`](taif.stations.json) | Machine-readable station list |
| [`taif.design-quality.yaml`](taif.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug taif

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug taif \
    --sidecar .cache/osr-pipeline/rasters/taif.grid.json \
    --out-dir designs/.../Taif

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../taif.toml \
    --out designs/.../README.md
```

`scripts/regenerate-taif.sh` chains steps 3 + drift tests into a single command.
