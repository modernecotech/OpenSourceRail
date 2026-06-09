# Comilla — Urban Rail Network

**Country:** BD · **Population:** 600,000

Auto-planned by the OpenSourceRail design pipeline: [`osr_geo`](../../../../design-py/src/osr_geo/) rasterises Overpass-verified OpenStreetMap features (arterial road graph, buildings, water, protected land, demand-anchor POIs) onto a 20 m cost / demand / buildability grid; [`osr-design`](../../../../crates/osr-design/) (rust) runs a demand-rewarded Dijkstra on that grid to synthesise corridors, places stations against the demand surface, and classifies every segment (at-grade / elevated / bridge — no tunnels per [RFC 0011](../../../../docs/rfcs/0011-civil-infrastructure-design-standard.md)). Population, country, and bbox are read from the canonical city catalog at [`lib/city-batches/world-sample.toml`](../../../../lib/city-batches/world-sample.toml).

## Network map

![Comilla rail network on OpenStreetMap](comilla-network-map.png)

*Every line visible end-to-end — radials out to the city edge, forced-coverage suburbs, and the ring line if present. Auto-fit zoom based on the network's actual bounding box.*

Corridor polylines + stations as GeoJSON for GIS / alignment tooling: [`comilla.corridor.geojson`](comilla.corridor.geojson).

## At a glance

| Metric | Value |
|---|---|
| Lines | 3 |
| Unique stations | 38 |
| Interchange stations | 2 |
| Multi-line transfer reachability | 0% (line-pairs sharing ≥ 1 station) |
| Anchor-weighted coverage | 40.9% |
| Route length (double track) | 65.7 km |
| Revenue fleet | 95 × 3-car trainsets |
| Revenue fleet passenger capacity | 34,200 AW2 pax (45,600 AW3 crush) |
| Spare + cold-reserve | 11 × 3-car trainsets |
| Peak headway | 3 min |
| Service hours | 05:30 – 02:00 (20.5 h/day) |

## Lines

*Termini are tagged by compass quadrant + radial band (Inner < 0.33 R, Mid 0.33–0.67 R, Outer > 0.67 R, where R is the network's outermost station-to-centre distance).*

| Line | Length | Stations | Trainsets | Termini |
|---|---|---|---|---|
| line-1 | 26.5 km | 15 | 42 | SE Outer ↔ W Outer |
| line-2 | 18.7 km | 12 | 30 | SE Mid ↔ NW Mid |
| line-3 | 20.5 km | 11 | 34 | SW Mid ↔ E Outer |
| **Total** | **65.7 km** | **38 unique** | **106** | |

## Rolling stock

| Property | Value |
|---|---|
| Consist | 3-car, 51 m |
| Max speed | 90 km/h |
| Onboard battery | 360 kWh per trainset |
| Seats | 60 longitudinal seats |
| Nominal capacity (AW2) | 360 pax (seated + standing, `light-metro-3car` per RFC 0008 §1) |
| Crush capacity (AW3) | 480 pax, short-duration structural/egress reference |
| Revenue fleet capacity | 34,200 AW2 pax (45,600 AW3 crush) |
| Total fleet capacity | 38,160 AW2 pax (50,880 AW3 crush, incl. spare + reserve) |

## Ridership capacity

- **Per-train planning capacity:** 360 AW2 passengers (`light-metro-3car`)
- **Revenue fleet simultaneous capacity:** 95 × 360 = **34,200 AW2 passengers** (45,600 AW3 crush)
- **Total fleet passenger capacity:** 106 × 360 = **38,160 AW2 passengers** (50,880 AW3 crush, incl. spare + reserve)
- **Peak frequency:** 20 trains/hour/direction (3-min headway)
- **Peak capacity per line per direction:** 360 × 20 = **7,200 pphpd**
- **Network peak throughput (all lines, both directions):** 3 lines × 2 directions × 7,200 = **43,200 passengers/hour**
- **Daily theoretical capacity (peak × 10):** ≈ **432,000 passenger-trips/day**
- **Practical daily service capacity** (80% load factor): ≈ **345,600 passenger-trips/day**
- **Planning daily ridership scenario** (25-45% active-rider uptake of catchment): ≈ **122,698 – 220,858 paid trips/day** (61,349 – 110,429 daily active riders at 2 trips/rider/day)

## Catchment

- City population: **600,000**
- Anchor-weighted coverage: 40.9%
- Catchment population: **≈ 245,399** (within ~800 m walk of a station)

## Energy infrastructure (solar + battery)

On-site trackside + depot PV and battery storage. Per-tier sizing (from [`../../../../lib/templates/energy-sites.toml`](../../../../lib/templates/energy-sites.toml)):

| Tier | Sites | PV each | Battery each |
|---|---|---|---|
| Depot-Main | 1 | 5000 kW | 40000 kWh |
| Interchange | 2 | 500 kW | 3000 kWh |
| Major | 12 | 400 kW | 2500 kWh |
| Standard | 17 | 300 kW | 2000 kWh |
| Terminal | 5 | 500 kW | 3000 kWh |
| **Total installed** | **37** | **18,400 kW** | **125,000 kWh** |

Aggregate station-rail charging power: **21,750 kW**. Trains opportunity-charge during station dwell per RFC 0002; onboard 360 kWh battery covers running.

Dedicated utility-scale solar plant / contracted offsite PPA asset: **77.7 MW** sized to cover the generated timetable traction-energy gap after station/depot PV, including a 115% planning coverage margin. This is carried as infrastructure CAPEX below.

### Energy Feasibility Check

| Check | Value | Interpretation |
|---|---:|---|
| Trainset line-haul intensity | 12.0 kWh/km | 3 cars × 4.0 kWh/car-km planning basis |
| Average one-way line energy | 263 kWh | 21.9 km average line length |
| Onboard battery coverage | 1.4× average line run | 360 kWh usable pack |
| Average 60 s dwell charge | 9.5 kWh/stop | 572 kW average charger across stops |
| Stops to refill one trainset pack | 38 stops | Opportunity charging supplements, not replaces, onboard reserve |
| PV daily yield proxy | 92 MWh/day | 5.0 peak-sun-hour planning proxy before local derates |
| Scheduled traction demand | 430 MWh/day | 33,170 scheduled train-km/day × 108% depot/deadhead factor |
| On-site PV shortfall before solar plant | 338 MWh/day | Gap used to size the dedicated plant / offsite solar PPA asset |
| Dedicated solar plant | 77.7 MW / 389 MWh/day | Utility PV + interconnection with 115% planning coverage margin |
| Residual grid/PPA top-up need | 0 MWh/day | Backup import after on-site PV plus the dedicated solar plant |
| Station/depot stationary storage | 125 MWh | Distributed Na-ion buffer for charging peaks and grid outages |

## CAPEX (planning grade)

All figures come from the `[costs]` block in `design.toml` — emitted by the `osr-design` Rust planner per RFC 0011 §9. The procurement basis is **USD direct-supplier planning pricing**; `*_eur` fields remain in `design.toml` only as compatibility mirrors at 0.92 USD→EUR. **OSR-discipline unit costs**: prefab portal-frame canopies (no bespoke architectural cladding), at-grade depots without overhead bridge cranes, **delivered rolling stock at about $1.4 M per self-contained car** (raw marketplace BOM retained only as an audit floor), commodity Na-ion cells + tier-2 PMSM motors + DIY SiC inverters, **onboard-first train control with only residual wayside** (no trackside fibre backbone, no proprietary CBTC vendor stack, no trackside computer interlockings — the function moves into the trainset, already counted in rolling-stock CAPEX), no overhead catenary, a dedicated solar plant when the generated timetable exceeds station/depot PV, and self-EPC overhead. The rolling-stock line now includes production labour, shop overhead, fixtures/tool amortisation, rail QA and homologation evidence, freight, duty, warranty, initial spares, training, commissioning, and acceptance testing. A separate lean railway production-plant setup line adds $100 k per vehicle/car module, with $200 k retained as the high sensitivity check. `country-costs.toml` applies the per-country labour/material multiplier downstream where a local tender view is needed.

### Civil works

| Bucket | Value |
|---|---|
| At-grade (61.8 km @ $3.0 M/km) | $186 M |
| Elevated (2.8 km @ $12.0 M/km) | $34 M |
| Elevated-interchange premium (2 sites @ $4.50 M) | $9.0 M |
| **Civil subtotal** | **$228 M** |

### Stations

Prefab portal-frame canopy + factory-bonded PV sandwich panel (RFC 0010 §3, ~9 t / 11-bay light-metro canopy delivered on two lorries, 3–5 day erection). Ground-level platform slab with controlled pedestrian approaches; the rail datum drops through the station bay for level boarding. Overbridges, lifts, and stairs are only for elevated/stacked interchanges or site-specific road barriers.

| Archetype | Count | Unit | Subtotal |
|---|---|---|---|
| `halt` | 1 | $600 k | $600 k |
| `standard` | 17 | $2.50 M | $42 M |
| `major` | 12 | $4.50 M | $54 M |
| `terminal` | 5 | $4.50 M | $22 M |
| `depot-terminal` | 1 | $5.0 M | $5.0 M |
| `interchange-elevated` | 2 | $12.0 M | $24 M |
| **Stations subtotal** | | | **$149 M** |

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
| `light-metro-3car` (revenue + spare + cold reserve) | 106 | $4.20 M | $445 M |

### Railway production plant

Each city carries a lean local railway production-plant setup allowance for tooling, basic fixtures, plant services, and commissioning bay setup. It is costed per vehicle/car module, not per trainset, and stays separate from the delivered rolling-stock procurement line.

| Item | Count | Unit | Subtotal |
|---|---:|---:|---:|
| Vehicle/car modules supported by city fleet | 318 | $100 k | $32 M |
| High sensitivity check | 318 | $200 k | $64 M |

### Dedicated solar power plant

Station/depot PV is counted in the charging microgrid and depot asset lines. When the generated timetable still has a traction-energy shortfall, the README adds a separate utility-scale solar plant or contracted offsite PPA asset sized from that gap.

| Item | Basis | Value |
|---|---|---:|
| Utility-scale PV field | 77,714 kW @ $700/kW | $54 M |
| Grid interconnection / PPA tie-in | 77,714 kW @ $100/kW | $7.8 M |
| Annual generation proxy | 77.7 MW × 5.0 peak-sun-h/day × 365 d/yr | 141.8 GWh/yr |
| **Dedicated solar plant subtotal** | | **$62 M** |

### Systems

| Item | Basis | Subtotal |
|---|---|---|
| Residual signalling / train-control wayside (onboard ATP/ATO + T-OBS carries the function; W-Nodes, balises, LoRa gateways, OCC interfaces remain) | 65.7 km × $0.050 M/km | $3.2 M |
| Station/depot charging microgrids (conductive charger, switchgear, inverter interface, local PV/battery tie-in; no continuous wayside supply) | per-stop allowance by station archetype | $15 M |
| EPC integration + project management (7%) | on subtotal | $63 M |

### Total

| Bucket | Value |
|---|---|
| Civil works | $228 M |
| Stations | $149 M |
| Depots | $22 M |
| Rolling stock | $445 M |
| Railway production plant | $32 M |
| Dedicated solar power plant | $62 M |
| Residual train-control wayside + charging microgrids | $18 M |
| EPC overhead (7%) | $63 M |
| **CAPEX total** | **$1.02 bn** |
| Per-route-km | $16 M / km |
| Per-capita (city pop) | $1,698 / person |

## Funding & affordability

Planning-grade financing model anchored to country financial parameters from [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml). Pure function of the [costs] block above + the country code — regenerate by re-running `scripts/regenerate-city.sh comilla`.

### Government commitment summary (budgetable)

Bottom line for next year's budget submission. Construction phase runs **years 1–7** (public equity drawdown + interest-only grace on repayable debt; grant disbursements are non-repayable); steady-state operation begins **year 8** and runs for **33 years** until the loans amortise.

| Phase | Annual gov / municipal commitment | Per resident / yr |
|---|---|---|
| Construction (years 1–7) | **$25 M / yr** | $41 |
| Steady-state, low-ridership (year 8+) | **$24 M / yr** | $40 |
| Steady-state, high-ridership (year 8+) | **$5.2 M / yr** | $9 |
| Steady-state, operating-neutral revenue case | **$21 M / yr** | $35 |
| Lifecycle envelope (yr 1–40, low scenario) | **$960 M cumulative** | $1,601 |
| Lifecycle envelope (yr 1–40, high scenario) | **$346 M cumulative** | $576 |
| Lifecycle envelope (yr 1–40, operating-neutral after opening) | **$874 M cumulative** | $1,457 |

_Population basis: 600,000 (catchment per `lib/city-batches/world-sample.toml`). After year 40, debt service drops to zero; steady-state commitments below are net of any operating surplus applied to repayable-debt support. The operating-neutral case already covers steady-state OPEX from fares, station shops, and advertising. Low/high residual OPEX shortfall before debt is $2.6 M / yr → $0 k / yr; surplus applied to debt support is $0 k / yr → $16 M / yr._

### CAPEX funding stack

| Tranche | Share | Principal | Rate | Tenor | Annual debt service (post-grace) |
|---|---|---|---|---|---|
| Climate / development grant (non-repayable) | 40% | $408 M | — | — | — |
| Green concessional loan (World Bank / AfDB / ADB / GCF class) | 50% | $510 M | 2.0% | 40 y, 7 y grace | $21 M / yr |
| Sovereign / project bonds (fallback only) | 0% | $0 k | 8.5% | 40 y, 7 y grace | $0 k / yr |
| Government equity (no debt service) | 10% | $102 M | — | — | — |
| **Total** | **100%** | **$1.02 bn** | | | **$21 M / yr** |

_During the 7-year grace period the public sponsor pays interest only on repayable debt — concessional loan $10 M / yr + fallback bonds $0 k / yr = **$10 M / yr** total. The $408 M grant tranche carries no repayment or coupon. Government equity is drawn across construction ($15 M / yr × 7 yr). Principal repayment begins in year 8 on a 33-year amortisation schedule._

### Annual OPEX (steady state)

| Component | Basis | Annual cost |
|---|---|---|
| Rolling-stock maintenance | 4 % of rolling-stock CAPEX | $18 M |
| Civil + station + depot maintenance | 2 % of fixed-asset CAPEX | $8.0 M |
| Residual train-control wayside maintenance | 5 % of residual signalling CAPEX | $162 k |
| Traction energy (156.9 GWh / yr) | 33,170 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor; 3 cars × 4.0 kWh/car-km; on-site PV 33.6 GWh/yr + dedicated solar plant 77.7 MW / 141.8 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr @ $0.10/kWh; solar plant O&M 1.5%/yr | $933 k |
| Labour (428 FTE) | driverless roster: OCC/remote 69, station/platform 127, passenger service 39, fleet maintenance 76, infrastructure/energy 81, admin/training 36; no train drivers × country median × 12 × engineer-premium 1.4 | $1.4 M |
| **OPEX subtotal** | | **$28 M / yr** |

_Annual service work: 33,170 scheduled train-km/day × 365 d/yr × 108% depot/deadhead factor = 13.1 M train-km / yr (39.2 M car-km / yr). On-site PV covers 33.6 GWh/yr and the dedicated solar plant adds 141.8 GWh/yr against 156.9 GWh/yr traction demand before residual grid/PPA top-up (0.0 GWh/yr). Driverless labour follows RFC 0015: train drivers are not counted, but OCC remote-assist, platform presence, passenger service, and fleet/energy maintenance scale with the larger service._

### Ticket pricing anchored to median income

Country median monthly income: **$195 USD** (per [`lib/templates/country-finance.toml`](../../../../lib/templates/country-finance.toml)). The revenue-forward case sets the monthly unlimited pass at **8 % of median monthly income** and pairs it with higher service uptake, more frequent trains, station retail, and advertising. Single-trip fare is set so that 30 single trips equal one monthly pass — a frequent commuter averaging ~50 trips / month still receives an effective ~40 % bulk discount.

| Product | Price target |
|---|---|
| Operating-neutral single-trip fare (8 % pass) | $0.52 |
| Day pass (3 trips) | $1.33 (15 % bulk discount) |
| Monthly unlimited pass | $15.60 (~8 % of median monthly income) |
| Annual pass | $171.60 (11 × monthly = ~1 free month) |

### Revenue & operating neutrality

Planning ridership bracket = daily active riders at 25-45% of catchment, converted to paid trips at 2 trips/rider/day and capped by practical service capacity (345,600 trips/day). Annual paid trips multiply daily paid trips by 365 service-days at the operating-neutral fare. The operating-neutral column solves annual paid trips so **farebox + station-shop leases + advertising = steady-state OPEX**. Gross post-grace repayable-debt service remains visible in the CAPEX funding stack, while any operating surplus is netted from the budgetable government support line.

| | Low scenario | High scenario | Operating-neutral target |
|---|---|---|---|
| Daily active riders | 61,349 | 110,429 | 68,235 |
| Daily active riders / catchment | 25% | 45% | 28% |
| Paid trips / active rider | 2 | 2 | 2 |
| Daily paid trips | 122,698 | 220,858 | 136,469 |
| Daily paid trips / city population | 20% | 37% | 23% |
| Annual paid trips | 44.8 M | 80.6 M | 49.8 M |
| Farebox revenue | $23 M / yr | $42 M / yr | $26 M / yr |
| Station shop leases | $903 k / yr | $903 k / yr | $903 k / yr |
| Advertising boards | $1.5 M / yr | $1.5 M / yr | $1.5 M / yr |
| **Total revenue** | **$26 M / yr** | **$44 M / yr** | **$28 M / yr** |
| Revenue / OPEX recovery | 91% | 157% | 100% |
| Country farebox-only policy target (diagnostic) | 50% | 50% | 50% |
| Gross repayable-debt service + residual OPEX subsidy | $24 M / yr | $21 M / yr | **$21 M / yr** |
| Operating surplus applied to debt support | $0 k / yr | -$16 M / yr | **$0 k / yr** |
| **Net gov repayable-debt support + residual OPEX subsidy** | $24 M / yr | $5.2 M / yr | **$21 M / yr** |
| Operating surplus after OPEX (before debt support) | $0 k / yr | $16 M / yr | $0 / yr |

_Commercial-revenue assumptions: 5,480 m² of station shop/kiosk leases at $16/m²/month and 1,064 advertising boards at $136/board/month, with occupancy derates applied._

**Caveats:** The grant-first funding stack, the 8 % operating-neutral fare target, the 25-45% daily-active-rider bracket, and the station-commercial assumptions are project-level defaults. Real deployments will negotiate the capital split with financing institutions and tune fares, retail mix, advertising inventory, and service frequency iteratively from boarding data. Treat the numbers above as a first-iteration sanity check, not as a bid-ready financial close.

## Files

| File | Role |
|---|---|
| [`design.toml`](design.toml) | Authoritative design |
| [`comilla.toml`](comilla.toml) | Expanded simulation scenario (input to `osr-sim`) |
| [`comilla-network-map.png`](comilla-network-map.png) | Auto-fit network map (rendered by `osr_scenario.render_map`) |
| [`comilla.corridor.geojson`](comilla.corridor.geojson) | Line polylines + stations (GeoJSON) |
| [`comilla.stations.json`](comilla.stations.json) | Machine-readable station list |
| [`comilla.design-quality.yaml`](comilla.design-quality.yaml) | Coverage / anchor-hit / civil-mix metrics + auto-gate result |

## Reproducibility

```bash
# 1. raster bundle from OpenStreetMap (cached by query hash)
python -m osr_geo.cli --slug comilla

# 2. design.toml + corridor.geojson + design-quality.yaml
#    (population + country pulled from lib/city-batches/world-sample.toml)
cargo run --release --bin osr-design -- --slug comilla \
    --sidecar .cache/osr-pipeline/rasters/comilla.grid.json \
    --out-dir designs/.../Comilla

# 3. scenario.toml + map PNGs + this README
python -m osr_scenario --design designs/.../design.toml
python -m osr_scenario.render_map --design designs/.../design.toml
python -m osr_scenario.network_readme \
    --design designs/.../design.toml \
    --scenario designs/.../comilla.toml \
    --out designs/.../README.md
```

`scripts/regenerate-comilla.sh` chains steps 3 + drift tests into a single command.
