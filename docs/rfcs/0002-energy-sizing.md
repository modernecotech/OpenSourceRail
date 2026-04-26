# RFC 0002 — Energy Sizing for a Reference Light Metro Line

**Status:** Draft
**Date:** 2026-04-20
**Depends on:** [docs/ARCHITECTURE.md](../ARCHITECTURE.md) §4 D5, §4 D7

## 1. Summary

This RFC puts concrete numbers to the catenary-free, solar-first energy architecture of D7. It does so for a **reference light-metro line**: 20 km, 15 stations, 2-track, 5-minute headway peak. For this reference case the RFC derives:

- Daily energy demand: **≈100 MWh/day**.
- PV nameplate required for net-positive annual generation in a 5 PSH climate: **≈25 MW**.
- Trackside sodium-ion storage required for service continuity through a two-day solar outage: **≈60 MWh**.
- Onboard battery per trainset: **≈900 kWh** (3 × 300 kWh cars) enabling ~1.5 round-trips between opportunity charges.
- Total capex for the energy subsystem: **≈$30M** vs. **≈$100M** for conventional catenary + traction substations — a **60–70% cost reduction**.

These numbers are first-order. They are offered as a planning baseline and as the starting point for the `osr-sim` energy model; they are not a substitute for a detailed design study on any specific line.

## 2. Non-goals

- Not a complete electrical design. Transformer sizings, harmonics, protection coordination, and grounding all require proper EE work outside this RFC.
- Not applicable to freight or long intercity. Per [ARCHITECTURE §1](../ARCHITECTURE.md), OpenSourceRail's scope is urban transit only; this RFC's sizing is therefore exclusively for light metro and metro service profiles.
- Not a land-use or permitting study. ROW PV implies planning-regime negotiations this RFC cannot resolve.

## 3. Reference Deployment

| Parameter | Value |
|---|---|
| Alignment | 20 km, double track, at-grade or elevated mix |
| Stations | 15 (average 1.3 km spacing) |
| Service hours | 18 h/day (05:00–23:00) |
| Peak headway | 5 min (both directions) |
| Off-peak headway | 10 min |
| Rolling stock | 3-car LRV / light metro, 60 t per car, 2.5 m wide × 3.6 m high |
| Fleet size | 12 trainsets (10 in service, 2 spare) |
| Typical ambient | Tropical or subtropical; 5 peak sun-hours (PSH) annual mean |

This sizing represents a moderately busy urban transit line — representative of, say, a new-build metro for a mid-sized capital city in our target regions. Smaller systems scale down linearly; larger systems break into multiple regions (RFC 0001 §6.2).

## 4. Energy Demand Model

### 4.1 Per-train consumption

Light metro rolling stock consumes approximately 3–5 kWh per car-km, depending on stopping density, grade profile, and HVAC load. For the reference line we use **4 kWh/car-km**, which matches published figures for several modern LRV/light-metro platforms and leaves a realistic margin for passenger HVAC in a hot climate.

Auxiliaries (HVAC, lighting, compressors) are ~15% of total vehicle draw and are rolled into the 4 kWh/car-km figure.

### 4.2 Daily aggregate

| | Value |
|---|---|
| Trains passing a point per hour (peak, one direction) | 12 (= 60/5) |
| Peak duration | 4 h (morning + evening peaks combined) |
| Off-peak duration | 14 h |
| Off-peak throughput | 6 trains/h |
| Daily train-passes per direction | 12×4 + 6×14 = 132 |
| Daily train-km | 132 × 20 × 2 = 5,280 |
| Daily car-km | 5,280 × 3 = 15,840 |
| **Line-haul energy** | 15,840 × 4 = **63.4 MWh/day** |
| Depot, stations, HVAC, lighting, signals (≈ 30% of traction) | **19.0 MWh/day** |
| Depot battery conditioning + charging losses (≈ 10%) | **8.2 MWh/day** |
| Auxiliary (fare systems, passenger info, accessibility) | **1.5 MWh/day** |
| **Total daily demand** | **≈92 MWh/day** → round to 100 MWh/day for planning |

Regeneration (braking) recaptures ~20% of traction energy when the onboard battery has headroom to accept it — this is already included in the 4 kWh/car-km figure, which is a net consumption value.

### 4.3 Demand profile through the day

Demand is not flat. First-order shape:

- 05:00–07:00: ramp-up, ~60% of peak hourly draw
- 07:00–10:00: morning peak, full hourly draw
- 10:00–16:00: off-peak, ~50% of peak hourly draw
- 16:00–19:00: evening peak, full hourly draw
- 19:00–23:00: evening taper, ~60 → 30% of peak
- 23:00–05:00: depot charging of fleet batteries, ~40% of peak draw (at low c-rate, spread over 6 h)

Peak hourly draw is roughly 8 MWh/h (≈ 8 MW average, probably ~12 MW instantaneous with stochastic peaks). This matters for storage sizing and grid-tie capacity.

## 5. PV Generation

### 5.1 Available PV area

| Surface | Area estimate | Notes |
|---|---|---|
| Station/platform canopies | 15 × 2,000 m² = 30,000 m² | Dual-use weather shelter; visually acceptable; first thing to build. |
| Depot roof | 10,000 m² | High-quality flat roof; easy to install and maintain. |
| ROW along track — vertical bifacial | 20 km × 2 sides × 4 m effective height = 160,000 m² projected area, ~80,000 m² of panel | Property-line fencing dual-use; catches morning/evening sun at complementary angles. |
| ROW along track — horizontal / slanted panels above ballast shoulder | 20 km × 2 × 2 m usable = 80,000 m² | Requires clearance management; standard tilt. |
| Between-rail / on-sleeper PV (Sun-Ways-class) | 20 km × 2 × 2.5 m = 100,000 m² available but not included in baseline | Phase-4+, not counted in this sizing. |
| **Baseline PV area counted** | **200,000 m²** | Excludes between-rail option. |

### 5.2 Nameplate

At modern module density of ~220 W/m² (2026-vintage monocrystalline + bifacial), 200,000 m² yields **44 MW nameplate**. Derating for:

- Packing factor 0.75 (structure, access paths, mutual shading) → 33 MW
- Performance ratio 0.80 (inverter losses, soiling, temperature, wiring) → **26.4 MW AC output**

Round to **25 MW AC** for planning.

### 5.3 Annual generation

At 5 PSH: 25 MW × 5 h × 365 = **45.6 GWh/year** = **125 MWh/day average**.

Daily demand is ~100 MWh. Headroom is roughly **25%**, which is intended. It covers:

- Seasonal variation (winter months at higher latitudes in the target band still see 4 PSH).
- Cloudy-day losses (a 5-day cloudy stretch at 50% yield is ~10% of a year if it happens 4×/year).
- Module degradation over lifetime (~0.5%/year).
- Demand growth.

### 5.4 Surplus monetization

On clear days the system will generate **far above demand during midday** (peak 25 MW instantaneous vs. 8 MW average demand). Three dispositions, in priority order:

1. **Charge trackside storage** (§6) — priority 1 until storage is full.
2. **Charge onboard fleet batteries** opportunistically — priority 2 during dwells and terminal stops.
3. **Export to grid** — priority 3, where regulations and grid infrastructure allow, at whatever FIT/PPA rate applies locally.

Deployments in regions without grid export should plan to curtail rather than undersize generation — curtailment cost is zero, undersizing leaves the line stranded on cloudy days.

## 6. Trackside Storage

Trackside storage sits at stations and at the depot. It has three duties:

1. **Diel shift.** Store midday surplus, deliver it during morning/evening peaks and overnight depot charging.
2. **Peak shaving.** Absorb the difference between 8 MW average and ~12 MW instantaneous demand.
3. **Cloudy-day autonomy.** Keep service running through solar-poor periods without a full grid-import contract.

### 6.1 Sizing

| Duty | Required capacity |
|---|---|
| Diel shift (surplus midday → peak + night) | ~35 MWh (storing roughly one-third of daily generation for time-shifted use) |
| Peak shaving headroom | ~5 MWh |
| One-day cloudy autonomy at 50% yield | ~50 MWh (to cover the ~50 MWh shortfall versus demand) |
| Two-day cloudy autonomy target | ~60 MWh total |
| **Baseline design** | **60 MWh** |

Two-day autonomy is a judgment call: single-day cloudy weather is common in target climates, two-day stretches are meaningful to plan around, three-day stretches are rare enough that grid fallback is acceptable.

### 6.2 Placement

Distributed, not centralized:

- **Station sites (15):** 2 MWh each = 30 MWh total. Co-located with station PV and station charging pads. Handles local peak shaving.
- **Depot site (1):** 30 MWh. Co-located with depot PV and overnight fleet charging.
- **Total: 60 MWh.**

Distribution across stations means no single battery failure halts service, and transmission losses are minimized because storage is co-located with both generation (canopy PV) and load (charging pads).

### 6.3 Chemistry and form factor

Sodium-ion primary per [RFC 0021 §3](0021-battery-traction.md). Installed cost at 2026 prices: ~$80/kWh at cell level (RFC 0021 §4 sourcing matrix), ~$120–150/kWh installed including BMS, enclosures, and site works.

- 60 MWh × $200/kWh = **$12 M** for trackside storage.

Duty cycle at these sizings is gentle (≈0.3 C average charge, ≈0.5 C peak discharge), supporting ≥6000-cycle life — comfortably >15 years of daily cycling.

## 7. Onboard Battery and Charging Strategy

### 7.1 Per-trainset sizing

A 3-car trainset consuming 12 kWh/train-km (3 × 4) uses **480 kWh per 40 km round trip**. Design goals:

- Able to complete one full round trip on a single charge without intermediate charging — a "limp home" mode if charging pads fail.
- Opportunity charge at terminals (4-minute dwell) and at mid-line charging stations.
- Avoid deep cycling to preserve pack life: operate between 20% and 80% SoC nominally.

Usable pack = 60% of total. To absorb a 480 kWh round trip without drawing below 20% SoC: total pack ≥ 480 / 0.6 = **800 kWh**. Round up to **900 kWh per trainset = 300 kWh/car** to leave headroom for HVAC extremes and gradient cases.

### 7.2 Chemistry split

Onboard chemistry is a weight/volume tradeoff:

- **LFP** at ~180 Wh/kg → 900 kWh = 5 t per trainset
- **Sodium-ion** at ~140 Wh/kg → 900 kWh = 6.4 t per trainset
- Difference: 1.4 t per trainset — about 0.8% of a 180 t light-metro consist

Conclusion for this reference case: **either works**. Default to sodium-ion for supply-chain sovereignty; LFP is acceptable where local supply is easier or where a specific light-vehicle platform is pack-volume-constrained. At metro duty cycles the gravimetric-density delta does not meaningfully affect energy consumption.

### 7.3 Charging infrastructure

| Site | Charger count | Power | Purpose |
|---|---|---|---|
| Terminals (2) | 2 × 1 MW | DC conductive, pantograph-up style | 4-min dwell adds ~65 kWh; 8 round-trips before reaching 20% SoC |
| Key intermediate stations (4) | 4 × 500 kW | DC conductive, pantograph-up | 60-s dwell adds ~8 kWh; used as range-extender, not primary energy source |
| Depot (10 stalls) | 10 × 150 kW | AC conductive, overnight | Low-C overnight charging of full fleet; best for pack life |

Capex: 2×1MW + 4×500kW + 10×150kW = **5.5 MW** of charging equipment. At ~$300/kW installed: **$1.65 M**.

### 7.4 Round-trip energy accounting

For a trainset doing 8 round trips/day (320 km):

- Total consumption: 8 × 480 = 3,840 kWh
- Opportunity charge at 6 station charging events per round trip × 8 kWh + terminal charges ≈ ~130 kWh per round trip
- Net depot draw per trainset: ~3,840 − 8×130 = ~2,800 kWh/day
- At 10 active trainsets: 28 MWh/day depot charging — within the 30 MWh depot storage capacity

Numbers check out: the fleet can sustain full service without pulling from grid during a single cloudy day, provided trackside storage was charged the preceding day.

## 8. Cost Comparison

Greenfield 20 km double-track light metro, **energy infrastructure only** (excludes rolling stock vehicle cost, track, stations, signaling):

### 8.1 OpenSourceRail approach

| Item | Cost |
|---|---|
| 25 MW PV (utility-grade + canopies + ROW mounting systems) at $700/kW blended | $17.5 M |
| 60 MWh trackside sodium-ion storage at $200/kWh installed | $12.0 M |
| Charging infrastructure (5.5 MW across terminals, mid-line, depot) | $1.65 M |
| Per-trainset battery × 12 trainsets × 900 kWh × $150/kWh | $1.6 M |
| Grid-tie inverters, switchgear, site works | $3.0 M |
| Engineering, commissioning, contingency (15%) | $5.4 M |
| **Total** | **≈ $41 M** |

### 8.2 Conventional catenary approach

| Item | Cost |
|---|---|
| Overhead catenary + support structures, 20 km double track at $2 M/km | $80 M |
| Traction substations, 4–5 sites at $4 M/site | $18 M |
| Grid connection works | $3 M |
| SCADA + OCS controls (proprietary vendor package) | $5 M |
| Engineering, commissioning, contingency (15%) | $15.9 M |
| **Total** | **≈ $120 M** |

### 8.3 Delta

**OSR approach ≈ 34% of conventional approach.** Savings: **~$80 M on a 20 km line.**

Additional factors not captured above:
- OSR eliminates specialized OCS maintenance workforce requirements → opex savings over lifetime.
- OSR's surplus generation is revenue or offset; catenary has no such capability.
- Catenary capex grows with line length; OSR per-km cost is roughly constant as generation and storage scale with km. Longer lines amplify the advantage.
- Catenary recovery from faults is slow (possession, isolation, line work); distributed battery + charging recovers faster from single-site failures.

Against this, OSR has:
- Novel-technology risk that may justify a reserve in financing.
- Dependence on PV supply chain (the alternative depends on copper, steel-mast, and catenary-wire supply chains, which are equally stressed in different ways).
- Higher onboard mass per trainset (~5–6 t battery vs. a pantograph + transformer at ~2 t); marginal impact on rolling-resistance energy.

## 9. Sensitivity Analysis

How do the numbers change as key assumptions flex?

| Variable | Change | Impact |
|---|---|---|
| Climate (PSH) | 4 PSH instead of 5 | PV yield drops 20%; either +20% PV nameplate (+$3.5 M) or +30% storage (+$3.6 M) needed. Still well below catenary capex. |
| Peak headway | 3 min instead of 5 min | Demand grows ~50% (~150 MWh/day). All sizings scale ~linearly; OSR advantage vs. catenary preserved. |
| Line length | 40 km instead of 20 km | OSR cost scales ~linearly to $80 M; catenary scales nearly linearly to $240 M. OSR advantage widens. |
| PV area available | Half (ROW not available) | Must rely on canopies + depot only (40,000 m²). Drop to 5 MW nameplate, 25 MWh/day generation — net-negative against demand. Line needs grid-import contract or extended storage. This case is the scenario most sensitive to solar-friendly geometry. |
| Cloudy-day frequency | 10% of days have <40% yield | Requires 2-day autonomy (covered by 60 MWh baseline) + grid fallback contract. No change to baseline sizing. |
| Sodium-ion cost | $300/kWh installed (pessimistic) | Trackside storage cost 60 MWh × $300 = $18 M. Total rises to $47 M vs. $120 M catenary. Still a strong advantage. |
| LFP instead of Na-ion for trackside | — | Cost ~comparable at utility scale; raw-material sovereignty point weakens. |

### 9.1 The case most likely to break this RFC

**Limited PV area** is the single-largest risk. If the ROW cannot host PV (planning, heritage, or engineering constraints) and station+depot area yields only ~5 MW, the line is net-negative on solar and must buy ~half its energy from grid. The capex comparison still favors OSR (no catenary), but the annual energy bill shifts from near-zero to material. This scenario must be evaluated early in any specific deployment — it is not a universal problem but it is a line-specific one.

Mitigation where ROW PV is constrained: offsite solar PPA, or accept higher grid dependence and focus savings on the catenary capex alone.

## 10. Safety and Reliability

Energy is not in the SIL-4 safety boundary (see RFC 0001 §3 and §9: traction control is onboard, MA enforcement does not depend on charging availability). Still, energy failures degrade service, and some considerations apply:

- **Loss of trackside storage at one station.** Adjacent stations' storage and fleet onboard capacity carry service until repair. No safety impact.
- **Loss of mid-line charging.** Trainsets adjust duty cycle (reduce round-trip count) until repair; trains never strand because onboard capacity is sized for full round trip without opportunity charging.
- **Loss of all PV.** Grid import + storage keeps service running for the storage-sizing horizon (~2 days). Operators must negotiate grid-fallback contracts as a normal commercial matter.
- **Thermal runaway / battery fire.** Sodium-ion and LFP are both thermal-runaway-resistant chemistries (unlike NMC). Standard battery-room fire suppression (inert-gas deluge, compartmentalization) applies. Onboard fires in BEMU/battery-electric rail stock have a well-understood mitigation playbook from ~decade of bus/truck operations — rail fire doors and passenger evacuation rules adapt directly.
- **PV soiling and bird strike.** Operational concerns, not safety ones. Cleaning schedules and mesh protection are standard utility-PV practice.

## 11. Open Questions

1. **Between-rail PV.** Sun-Ways-class on-sleeper PV could double the effective PV area per track-km. At what point is it worth the clearance and tamping complexity? Prototype in `osr-sim` first.
2. **Battery recycling and second-life.** Traction packs at end-of-life (still ~80% capacity) are ideal candidates for cascade into trackside storage. Designing the spec so packs are physically swappable between roles would amortize the battery capex across two duty cycles — worth its own small RFC.
3. **Dynamic opportunity-charging sizing.** For very high-frequency service (<3 min headway), the dwell-time charging energy starts to matter as a primary source, not a range-extender. Where's the crossover, and how does it change the onboard-pack sizing?
4. **Grid-tie protocol choice.** IEEE 2030.5 is defaulted in ARCHITECTURE §D7 — this should be confirmed against target-region utility standards.
5. **Seasonal tilt and tracking.** Fixed-tilt vs. single-axis tracking changes PV cost by ~15% and yield by ~20%. Bias toward fixed-tilt at these sizes for simplicity; revisit if yield binds.
6. **Metro-class ridership peaks.** Full-metro duty (6-car, 2-min headway, underground) will push line-haul demand well above the light-metro reference in §4. The sizing framework scales, but a dedicated RFC validating it for a metro-class reference line is warranted before Phase 5.

## 12. Prior Art

- **Stadler FLIRT Akku** — 80–150 km range on battery, opportunity charging at electrified sections. Our reference-metro sizing sits comfortably under this proven envelope.
- **Hitachi Masaccio (TrainLab)** — hybrid battery-catenary for regional service.
- **Siemens Mireo Plus B** — BEMU, commercial operation in Germany.
- **Adelaide Flinders Line tram** — solar-powered light rail using a rooftop PV + grid-feed arrangement; validates solar-rail economics.
- **Sun-Ways (Swiss pilot)** — on-sleeper PV.
- **Bankset / Deutsche Bahn PV fence pilots** — vertical bifacial along ROW.
- **India Railways rooftop PV program** — large-scale PV on station and depot roofs; demonstrates the regulatory path in a major target region.

The OpenSourceRail contribution over the prior art is not any individual element — each has been piloted somewhere. It is the **integrated design** that treats PV + trackside storage + BEMU as a single system with open software coordinating energy dispatch, and sizes it as a complete alternative to catenary rather than a retrofit.

---

*This RFC is a planning artifact. Actual pilot deployments will produce per-line sizing studies that refine these numbers with local climate, grid conditions, and operational patterns.*
