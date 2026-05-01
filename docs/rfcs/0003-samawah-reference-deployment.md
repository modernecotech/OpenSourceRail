# RFC 0003 — Samawah Urban Rail: Reference Deployment

**Status:** Draft
**Date:** 2026-04-20
**Depends on:** [docs/ARCHITECTURE.md](../ARCHITECTURE.md), [RFC 0001](0001-track-state-consensus.md), [RFC 0002](0002-energy-sizing.md)

## 1. Summary

This RFC proposes a concrete reference deployment for OpenSourceRail: a **four-line urban rail network** serving **Samawah (As-Samawah), capital of Al-Muthanna Governorate, Iraq**. Every station coordinate corresponds to a **real OpenStreetMap anchor** within Samawah's built-up urban fabric — Overpass-verified on 2026-04-24. Every inter-station polyline is **routed along actual streets** (shortest-path on the OSM road graph, weighted to favour arterials over residential) rather than straight-line "as the crow flies". The four lines are:

- **Line 1 "Nahrain" — N–S spine** (~15 km routed, 8 stations). Connects **Al-Muthanna University** (northern interchange with L4) through the **hospital cluster**, the **city centre** (triple interchange with L2/L3), and southern residential neighbourhoods to the **main depot at Al-Maali** (southern terminus).
- **Line 2 "Sharqiyyeh" — E–W crosstown** (~10 km routed, 6 stations). Western residential (Al-Naft) through **Samawah Central** (interchange with L1/L3) to eastern residential (Al-Bustan Sharqi).
- **Line 3 "Mahatta" — SE branch** (~12 km routed, 5 stations). From **Samawah Central** (interchange with L1/L2) through SE residential to the **Samawah Railway Station** on the Baghdad–Basra mainline.
- **Line 4 "Shamal" — Northern cross** (~5.5 km routed, 5 stations). From **Um al-Asafir** (NE terminus) through **Al-Muthanna University** (interchange with L1), **Al-Sukuk**, **Jarbuwiya**, to **Abu Jwailana** (NW terminus). Added in the 2026-04-24 revision after a coverage audit flagged 40+ neighbourhoods >1 km from any station in the original 3-line layout, most of them clustered in the northern Jarbuwiya + Um al-Asafir districts.

Total network: **~29 km of double-track light metro, 21 unique stations, 23-trainset fleet**. Two interchange hubs: Samawah Central (L1/L2/L3) and Al-Muthanna University (L1/L4).

The previous draft of this RFC proposed a 2-line design (14 km radial + 16 km ring, 30 km total). That geometry placed Al-Muthanna University ~8 km south-east of its real location, placed "Samawah Railway Station" in the north-west when the real station is south-east, and routed the Halqa ring through palm groves + agricultural land that wasn't built-up. That design was retired in favour of the OSM-grounded network below.

This is the reference case for `osr-sim`, the anchor for conversations with potential pilot stakeholders, and the concrete instantiation against which subsequent subsystem designs are measured. It is a planning-grade concept design, not a surveyed alignment — it exists to make the architecture *real* rather than to commit any specific routing.

## 2. Why Samawah

| Factor | Samawah | What it means for OSR |
|---|---|---|
| Population | ~373,770 (As-Samawah Subdistrict, 2024 Iraq census; canonical figure in [`lib/city-batches/world-sample.toml`](../../lib/city-batches/world-sample.toml)) | Right-sized for light metro — too small for a major vendor to bother with, ideal for an open-source first deployment |
| Existing rail | Station on Baghdad–Basra mainline + **rail yard with 300–800 stored wagons + adjacent rolling-stock workshop** (see §2.1) | Rail culture, intercity interchange, **and a brownfield-recovery anchor that turns this from a reference scenario into a deployable pilot** |
| Climate | Hot desert; ~6+ peak sun hours annual mean | PV yield ~20% above the RFC 0002 reference (5 PSH) — catenary-free + solar is conservative, not ambitious |
| Grid reliability | Limited; frequent outages | Storage autonomy has real operational value, not just a planning formality |
| Existing electrification | None on Iraqi mainlines | No legacy catenary, no vendor-locked OCS — greenfield on D7 |
| Development context | Al-Muthanna is among Iraq's lower-income governorates | Capital sensitivity is high; the ~66% capex reduction in RFC 0002 is decisive, not marginal |
| Institutional anchors | Al-Muthanna University (engineering faculty), new German Hospital, government buildings | Each anchor is a major daily demand generator; the radial alignment serves all of them on one line |
| Workforce | Engineering graduates from Al-Muthanna University | Potential domestic design/build partnership — the core promise of OSR is "workers who design and build the systems in the country" |

The combination is close to optimal: genuine need, favorable physics, no legacy to migrate, and domestic technical capacity to engage. If OSR cannot make sense here, it likely cannot make sense anywhere.

### 2.1 Physical-asset anchor — Samawah is brownfield, not greenfield

Satellite imagery review (2026-04-26) of the rail yards immediately
adjacent to **Samawah Train Station (محطة قطار السماوة)** identifies
two stockpiles of dormant rolling stock:

- **Northern yard** (along Samawah Train Station): ~4–6 parallel
  sidings packed end-to-end. **Estimated ~120–300 wagons.**
- **Southern yard** (diagonal NE–SW sidings): ~5–8 parallel sidings
  with similar density, plus a large workshop / shed building at the
  southern end. **Estimated ~150–480 wagons.**
- **Total estimate: ~300–800 wagons.** Predominantly standard 4-axle
  freight stock (covered wagons, hoppers, flatbeds) — passenger
  coaches a small fraction.

The southern yard's workshop building was the target of a 2011
Iranian Waxon Park rehabilitation deal (per *Iraqi Business News*
historical reporting). Outcome of that deal is unclear and is part of
the [RFC 0027](0027-brownfield-pilot-asset-recovery.md) Phase 1
assessment.

National context (Iraqi Republic Railways / IRR / السكك الحديد
العراقية):

- **National fleet:** 10,326 freight wagons, 255 passenger coaches
- **Gauge:** 1 435 mm standard nationwide → fully compatible with
  [RFC 0009](0009-track-design-standard.md)
- **Couplers:** SA-3 (Soviet automatic) + screw/buffer combo →
  **incompatible** with the Scharfenberg Type 10 spec'd by RFC 0008
  §3.1, but the recovered drawgear is resaleable to legacy operators
  (RFC 0027 §5.3)

**What this means for the Samawah pilot:** the pilot is no longer a
hypothetical greenfield deployment. It is the systematic conversion
of an existing rail-yard + workshop complex into the first OSR
production site, anchored on:

1. **A dormant fleet with recoverable wheelsets, axleboxes, brake
   gear, and structural steel** worth $8–15 M in component value
   against $1–3 M in recovery operations cost (per RFC 0027 §3).
2. **An existing workshop building with foundations, pit tracks, and
   crane gantries** that would otherwise require €5–8 M to build
   greenfield (RFC 0014).
3. **An active rail corridor** through the city, available as the
   intercity interchange at the Samawah Railway Station terminal
   (Line 3 SE branch in §3.3 above).
4. **Standard gauge** matching OSR spec — no gauge conversion
   required.
5. **A national rail authority (IRR) under reconstruction pressure**
   — the political context favours engagement.

**Conversion strategy** is in
[RFC 0027 — Brownfield Pilot: Existing-Asset Recovery & Workshop
Integration](0027-brownfield-pilot-asset-recovery.md), which carries
the per-phase doctrine, recovery yield estimates, workshop conversion
matrix, and risk register. RFC 0027 is intended to apply to every
brownfield deployment, not just Samawah; the candidate-city list is
in §9 there.

**Status of the brownfield assessment** at time of writing:
- ☐ Phase 1 site visit + fleet census — **not yet started; gating item**
- ☐ Workshop tooling audit — pending Phase 1
- ☐ NDT campaign on a sample wheelset population — pending Phase 1
- ☐ MoU draft with IRR / Iraqi Ministry of Transport — pending
  diplomatic / technical-community introduction

The single highest-value next step on the OSR programme is **getting
a real Phase 1 census on the ground**. Without it, the Samawah
deployment costs in §1 of [RFC 0021](0021-battery-traction.md) and
the depot CAPEX in [RFC 0014](0014-depot-design-standard.md) are
greenfield estimates; with it, the per-consist mechanical CAPEX
drops by **~$30–60 k** and the depot CAPEX drops by **a factor of 5–10**
per RFC 0027.

## 3. Geography and Indicative Alignment

Samawah sits on the Euphrates in southern Iraq. The city stretches roughly east–west along the river with residential suburbs fanning north and south. The mainline railway enters from the northwest, the city centre sits on the river bend, and the major newer developments (hospital, university campus, expanding residential districts) are south and east of the historic core.

![Samawah network — 4 lines road-snapped on OpenStreetMap](../../designs/west-asia/Iraq/Samawah/samawah-network-map.png)

*Four lines road-snapped on OSM tiles: blue = L1 Nahrain, orange =
L2 Sharqiyyeh, green = L3 Mahatta, magenta = L4 Shamal. Station
markers coloured by archetype (red terminal, purple depot-terminal,
blue major, orange interchange, white standard). Every polyline is
shortest-path on the road graph, weighted to favour arterials.
Regenerate with `./scripts/regenerate-samawah.sh`; see
[§3.6 Realism notes](#36-realism-notes) for what surveying would
still change.*

> **Important caveat.** The alignment below is indicative. Precise routing, station siting, and ROW acquisition are out of scope for this RFC — those depend on surveying, stakeholder consultation, and local planning processes that only Samawah's own planners and Al-Muthanna Governorate can lead. What this RFC provides is a *credible skeleton* that demonstrates how an OpenSourceRail network would be organized for a city of Samawah's size and form.

### 3.1 Line 1 — Nahrain (N–S spine)

Eight stations, ~11 km total. North-to-south sequence along the dense urban core, elevated through the city centre + hospital interchange, at-grade elsewhere:

| # | Station | Lat / Lon | Purpose | OSM reference |
|---|---|---|---|---|
| 1 | Al-Muthanna University | 31.3386, 45.2884 | N terminus; university campus | `amenity=university جامعة المثنى` |
| 2 | Jamia Al-Muthanna | 31.3374, 45.2870 | Residential south of campus | `place=neighbourhood جامعة المثنى` |
| 3 | Al-Qashla | 31.3196, 45.2916 | Dense urban cluster NE of centre | `place=neighbourhood القشلة` |
| 4 | Samawah Teaching Hospital | 31.3213, 45.2734 | Major regional hospital | `amenity=hospital مستشفى السماوة التعليمي` |
| 5 | Samawah Central | 31.3079, 45.2827 | Triple interchange (L1/L2/L3) | `place=city السماوة` |
| 6 | Al-Hakam | 31.2973, 45.2757 | Southern residential | `place=neighbourhood حي الحكم` |
| 7 | Hayy 270 Dar | 31.2969, 45.2646 | Residential cluster | `place=neighbourhood حي 270 دار` |
| 8 | Al-Maali | 31.2785, 45.2794 | S terminus; main depot | `place=neighbourhood الشراكية` |

Expected daily ridership at build-up: **35,000 – 48,000 passenger-trips** (highest — serves university + hospital + city centre).

### 3.2 Line 2 — Sharqiyyeh (E–W crosstown)

Six stations, ~7 km total. Western residential through the city centre to eastern residential:

| # | Station | Lat / Lon | Purpose | OSM reference |
|---|---|---|---|---|
| 1 | Al-Naft | 31.3123, 45.2485 | W terminus; housing complex | `place=neighbourhood حي النفط` |
| 2 | Al-Mualimin | 31.3152, 45.2740 | Central-west residential | `place=neighbourhood حي المعلمين` |
| 3 | Samawah Central | 31.3079, 45.2827 | Interchange with L1, L3 | shared with L1 |
| 4 | Al-Sharqi | 31.3105, 45.2888 | Dense east residential | `place=neighbourhood حي الشرقي` |
| 5 | Al-Sharqi East | 31.3135, 45.2901 | Residential cluster | `place=neighbourhood حي الشرقي عكد الداحرة` |
| 6 | Al-Bustan Sharqi | 31.3167, 45.3118 | E terminus; secondary layup | `place=neighbourhood البساتين الشرقية` |

Expected daily ridership at build-up: **18,000 – 25,000 passenger-trips**.

### 3.3 Line 3 — Mahatta (SE branch to railway station)

Five stations, ~5 km total. Short branch from the city centre to the intercity railway station:

| # | Station | Lat / Lon | Purpose | OSM reference |
|---|---|---|---|---|
| 1 | Samawah Central | 31.3079, 45.2827 | Interchange with L1, L2 | shared |
| 2 | Al-Hidriya | 31.3050, 45.2796 | Residential south of centre | `place=neighbourhood الحيدريه` |
| 3 | Al-Nahda | 31.2978, 45.2897 | Dense SE residential | `place=neighbourhood حي النهضة` |
| 4 | Al-Qasim | 31.2869, 45.2826 | Southern residential | `place=neighbourhood حي القاسم` |
| 5 | Samawah Railway Station | 31.2746, 45.3032 | SE terminus; Baghdad–Basra intercity interchange | `railway=station محطة قطار السماوة` |

Expected daily ridership at build-up: **12,000 – 18,000 passenger-trips** (modest, gated by intercity service frequency).

### 3.4 Line 4 — Shamal (Northern cross)

Five stations, ~5.5 km total. Added in the 2026-04-24 revision after a
coverage audit showed 40+ neighbourhoods sitting >1 km from the
nearest 3-line station, with the largest cluster in the northern
suburbs. Line 4 interchanges with Line 1 at the Al-Muthanna
University station:

| # | Station | Lat / Lon | Purpose | OSM reference |
|---|---|---|---|---|
| 1 | Um al-Asafir | 31.3442, 45.2981 | NE terminus; northern residential | `place=neighbourhood ام العصافير (حي الرسالة)` |
| 2 | Al-Muthanna University | 31.3386, 45.2884 | Interchange with L1 | shared with L1 |
| 3 | Al-Sukuk | 31.3384, 45.2763 | Residential mid-arc | `place=neighbourhood السكك` |
| 4 | Jarbuwiya | 31.3393, 45.2640 | Dense NW residential cluster | `place=neighbourhood الجربوعية الاولى` |
| 5 | Abu Jwailana | 31.3395, 45.2426 | NW terminus; western-edge residential | `place=neighbourhood ابوجويلانة` |

Expected daily ridership at build-up: **10,000 – 15,000 passenger-trips** (newest line; development-driven growth on the 20-year horizon).

### 3.5 System totals

| Metric | Value |
|---|---|
| Route-km (double track) | ~55 km |
| Stations (unique) | 33 |
| Lines | 3 (auto-planned by `osr-design`) |
| Multi-line interchanges | central interchange complex + radial-junction interchanges — every radial converges on the elevated-junction at city centre per the via-centre routing rule for ≤ 3-line networks |
| Fleet (revenue) | 49 × 3-car trainsets |
| Fleet (spare + cold-reserve) | 6 × 3-car trainsets |
| Average inter-station spacing | ~1.2 km (per [`SpacingConfig`](../../crates/osr-routing/src/station.rs) — 1.2 km inner, 2 km transitional, 4 km outer; matches the operator brief of "1.2 km inner / 2–5 km outer") |
| Demand surface | Anchor (POI) + WorldPop residential population blend per [`build_demand_surface`](../../design-py/src/osr_geo/rasterize.py) — lines reach population centres without mapped POIs |
| Service hours | 05:30 – 23:30, 18 hours |

> The table above is **derived from** [`design.toml`](../../designs/west-asia/Iraq/Samawah/design.toml);
> regenerate with `python -m osr_scenario.stats --format markdown`.
> A drift test (`design-py/tests/test_rfc_drift.py`) fails CI if this
> table ever contradicts the design file. The full regeneration
> pipeline is one command:
>
> ```bash
> ./scripts/regenerate-samawah.sh
> ```
>
> which emits the sim scenario (`designs/west-asia/Iraq/Samawah/samawah.toml`), the network
> map PNGs (`docs/screenshots/samawah-network-map*.png`), runs the
> drift + round-trip tests, and prints the summary stats above.
| Target daily ridership (steady-state) | 65 000 – 90 000 passenger-trips |

### 3.6 Realism notes

Honest assessment of the revised (2026-04-24) 4-line design
against real Samawah OSM data:

**What's real.** Every station coordinate in
[`designs/west-asia/Iraq/Samawah/design.toml`](../../designs/west-asia/Iraq/Samawah/design.toml)
corresponds to a named OSM feature verified by Overpass query:
either a specific `place=neighbourhood` node, an `amenity` node
(university / hospital), or a `railway=station` node. The 220 000
population, the bounding box, the Euphrates position, and the
Baghdad–Basra mainline crossing at the south-east are all OSM-
consistent. The triple-interchange at Samawah Central is at the
verified `place=city` node.

**What's *not* real yet.** Things a surveyor would still catch:

- **Inter-station polylines follow the cheapest-road shortest path**
  through the OSM network (arterials weighted 0.6–0.8, residentials
  1.8). That's planning-grade, not engineering-grade — curve radii,
  grades, and the ROW width needed for double track aren't checked.
  A real alignment survey will adjust station coordinates by tens
  of metres to snap to stakeable centrelines + may replace some
  segments with elevated viaduct where the road is too narrow.
- **Coverage audit flags 40+ neighbourhoods >1 km from any station**
  after Line 4 was added to pick up the northern Jarbuwiya cluster.
  The remaining outliers are mostly fringe residential (distant
  Jarbuwiya branches, Al-Ma'ali south of the rail, agricultural
  villages beyond the urban edge). Extending the network further
  is deferred to a future RFC if those areas develop.
- **Line 1's Al-Qashla → Hospital segment** swings west-then-south
  to reach the hospital cluster — a one-detour on an otherwise
  N–S spine. Kept for the hospital demand anchor; planners may
  prefer skipping.
- **Al-Bustan Sharqi** (Line 2 east terminus) sits at the outer
  edge of built-up area. Secondary layup siting here works but
  detailed land acquisition is pending.
- **29 km / 220 k population across 4 lines** is at the upper end
  of the light-metro ratio. Comparable cities: Amiens (135 k →
  11 km), Tours (140 k → 15 km), Orléans (115 k → 30 km across
  2 lines). Samawah's 29 km is a full 5-phase build-out target
  (Phase A delivers Line 1 north first).

**How to take this to the next fidelity level:**

1. Re-run the `design-py` routing + rendering pipeline with a
   one-command refresh:

   ```bash
   ./scripts/regenerate-samawah.sh
   ```

   which fetches Samawah OSM (cached), routes every line on the
   road graph, emits `corridor.geojson` + `designs/west-asia/Iraq/Samawah/samawah.toml`
   + the map PNGs, and runs the scenario + RFC drift tests.
2. Feed the stationed alignment + `corridor.geojson` into
   [`osr-alignment-export`](../../crates/osr-alignment/src/main.rs)
   to produce LandXML + railML for import into Bentley OpenRail
   or Civil 3D.
3. Cross-reference against Iraqi Ministry of Transport + Al-
   Muthanna Governorate road + cadastre datasets.
4. Review with Al-Muthanna University transportation faculty
   and the Governorate planning office.

## 4. Service Plan

### 4.1 Headways

| Period | Line 1 Nahrain | Line 2 Sharqiyyeh | Line 3 Mahatta |
|---|---|---|---|
| AM peak (07:00–09:30) | 5 min | 6 min | 7 min |
| Midday (09:30–16:00) | 8 min | 10 min | 12 min |
| PM peak (16:00–19:00) | 5 min | 6 min | 7 min |
| Evening (19:00–22:00) | 10 min | 12 min | 12 min |
| Late evening (22:00–23:30) | 15 min | 15 min | 15 min |

Line 1 is the busiest service (university + hospitals + centre + southern residential — all major demand anchors). Line 2 provides east-west connectivity crossing L1 at Samawah Central. Line 3 is a short branch whose headway is aligned with the (roughly twice-daily) Baghdad–Basra mainline intercity arrivals so that a rail-station transfer always has a connecting metro service within 5 minutes of the peak timetable.

### 4.2 Anchor-driven demand

Unusually for light metro, ridership here is *dominated* by a few large institutional anchors rather than by distributed demand. This has design consequences:

- **University:** sharp peaks 07:30 and 15:00 during term; low on Fridays and summer. Platform capacity at Al-Muthanna University must handle 2,000+ pax in 20 minutes.
- **Hospitals (two):** steady demand through the day, with a visiting-hours peak in mid-afternoon. 24-hour operation would be justifiable for hospital access; this RFC stops at 23:30 but flags the question.
- **Railway station:** bunched demand aligned with the (roughly twice-daily) intercity arrivals. Line 1 timetable should align a service with each mainline arrival/departure.
- **Souq and Centre:** evenings and weekends, counter-cyclical to the university peak — this is helpful for fleet utilization.

### 4.3 Rolling stock

Reference platform per [ARCHITECTURE §4 D5](../ARCHITECTURE.md):
- 3-car, ~57 m consist with low-floor centre door zones (light metro class)
- Na-ion onboard battery, 360 kWh/trainset (120 kWh/car), sized for one route-length with station opportunity charging
- Open SiC traction inverter, Rust control firmware
- TSN Ethernet trainbus
- HVAC sized for 50 °C ambient, which is load-bearing in Samawah summers (see §5.4)

## 5. Energy: Samawah-specific Numbers

Applying [RFC 0002](0002-energy-sizing.md) to this network, with Samawah-specific adjustments for climate and duty cycle.

### 5.1 Demand

| Component | kWh/day |
|---|---|
| Line 1 line-haul (4 kWh/car-km × 3 cars × traffic) | ≈ 40,000 |
| Line 2 line-haul | ≈ 22,000 |
| HVAC uplift for extreme heat (+25% over RFC 0002 baseline in peak summer) | ≈ 15,000 |
| Stations, depot aux, signals, info systems | ≈ 22,000 |
| Charging losses | ≈ 10,000 |
| **Total (peak summer)** | **≈ 110,000 kWh/day = 110 MWh/day** |
| Total (shoulder season average) | ≈ 85 MWh/day |

Slightly higher than the RFC 0002 reference because Samawah summers are more HVAC-intensive, and we've scaled up to 30 km of route.

### 5.2 PV generation

Samawah's 6 PSH annual mean (with summer peaks above 8 PSH) is higher than the generic reference.

| Surface | Area | Notes |
|---|---|---|
| Station canopies (20 × 2,000 m²) | 40,000 m² | Dual-use shade — valuable in Samawah heat |
| Depot roof (East Depot) + Northwest layup | 16,000 m² | |
| ROW vertical bifacial along 30 km × 2 sides × 4 m effective | 240,000 m² projected, ~120,000 m² of panel | Vertical orientation also reduces dust accumulation vs. horizontal |
| ROW ballast-shoulder panels | 120,000 m² | Tilted; subject to dust soiling management |
| **Total panel area** | **~300,000 m²** | |

At 220 W/m² × 0.75 packing × 0.78 PR (lower PR than RFC 0002 due to high module temperatures — heat derates silicon):
- Nameplate AC: **~38 MW**
- Annual generation at 6 PSH: **~83 GWh/yr = 228 MWh/day average**
- Comfortable 2× headroom over peak-summer demand; clean surplus most of the year

The headroom deliberately buys two things specific to Samawah:
1. **Dust-storm resilience.** Peak soiling events in Muthanna can cut yield 40–60% for several days. The surplus lets us absorb this without grid dependence.
2. **Grid export opportunity.** Iraq's grid is energy-constrained; feed-in under a state-utility PPA could be a material revenue line, not an afterthought.

### 5.3 Storage

Given grid unreliability, Samawah's storage sizing should be more generous than the RFC 0002 baseline. Target: **3-day autonomy** (vs. 2-day generic).

- Trackside: 20 stations × 2.5 MWh = 50 MWh
- Main depot: 40 MWh
- Secondary layup: 5 MWh
- **Total trackside storage: 95 MWh Na-ion**

Onboard: 14 revenue trainsets × 360 kWh = 5.0 MWh rolling stock battery,
with two spare consists adding another 0.7 MWh if fully provisioned.

### 5.4 Thermal considerations

Samawah summers routinely exceed 45 °C; record highs approach 55 °C. This has three design consequences:

1. **HVAC energy dominates.** Per-car traction + HVAC at 50 °C ambient can reach 6 kWh/car-km. The 4 kWh/car-km reference figure is already rolled up with an average HVAC; the RFC's +25% summer uplift reflects realistic worst-case.
2. **Battery conditioning.** Both sodium-ion and LFP prefer operation below 45 °C. Trackside battery enclosures need insulation + passive ventilation minimum; active cooling for high-C discharge periods is justified for the main depot only. Onboard packs sit under the floor with thermally managed enclosures; Na-ion's wider safe-operation temperature window is particularly useful here.
3. **PV temperature derating.** Panels in Samawah can reach 70+ °C module temp on a summer afternoon. Bifacial + vertical mounting runs cooler than horizontal ballasted arrays and is preferred on the ROW for this reason as much as the area one.

### 5.5 Capex summary (Samawah-specific)

Applying RFC 0002's cost basis, scaled to 30 km and adjusted:

| Item | Cost (USD) |
|---|---|
| 38 MW PV (blended across surfaces) @ $700/kW | $26.6 M |
| 95 MWh trackside Na-ion storage @ $200/kWh installed | $19.0 M |
| Charging infrastructure | $3.0 M |
| Onboard batteries, 16 trainsets × 360 kWh @ $150/kWh | $0.9 M |
| Grid tie + BOP + site works | $5.0 M |
| Engineering, commissioning, contingency (20% — slightly higher for novel deployment) | $11.1 M |
| **Energy subsystem total** | **≈ $66 M** |

For comparison, a conventional 25 kV AC catenary + 4 traction substations for a 30 km system in this market would run **≈ $180 M**. The OSR energy approach is **~37% of the catenary cost.**

## 6. Mapping to OpenSourceRail Architecture

This is where the reference deployment connects back to the domain designs:

### D1. Operations & Dispatch
- One Operations Control Centre at East Depot, with a backup dispatch workstation at Samawah Central.
- Dispatcher interface: web-based; full observability via the OpenTelemetry + Prometheus stack; no proprietary HMI.
- Integration with intercity rail: the OCC subscribes to the Iraqi Republic Railways (IRR) timetable via GTFS-RT (or bilateral feed if GTFS isn't available) so that Line 1 services align with mainline arrivals.

### D2. Train Control
- **Two consensus regions:** Line 1 (12 W-Nodes, one per station plus depot) and Line 2 (10 W-Nodes).
- Region boundaries at Eastern Bridge and Al-Muthanna University — the Line 1/Line 2 interchanges — handled by the handoff protocol in RFC 0001 §7.4.
- Interlockings at the three turnback sidings (Line 1 termini and mid-line) plus the depot throats.
- No track circuits: position is sensor-fused per [RFC 0001](0001-track-state-consensus.md) §5.1, with beacon-fix sites at every switch and every platform.

### D3. Communications
- Public 5G SA for primary train↔wayside link — Zain Iraq, Asiacell, or Korek presence in Samawah; one or more operators will likely carry the project with a network-slicing arrangement.
- LoRa mesh gateways at every W-Node site as the safety-telemetry fallback, giving citywide coverage independent of carrier uptime.
- TSN Ethernet backbone along the ROW (single fiber pair in a ruggedized conduit, ring topology per line).

### D4. Passenger Services
- **Account-based fare** per [ARCHITECTURE §4 D4](../ARCHITECTURE.md):
    - Iraqi mobile money rails (zainCash, AsiaHawala) as primary.
    - QR tickets via a local web-app (no native app required — important for feature-phone access).
    - Optional reloadable NFC card for those who prefer it, but not the default channel.
- Trilingual passenger info (Arabic, Kurdish, English) on displays and announcements; Arabic is primary for Samawah but the project infrastructure should generalize.
- Station screens: SBC + standard displays per the D4 design, with prayer-time integration for culturally appropriate PA silence windows.

### D5. Rolling Stock
- 14 + 2 spare 3-car consists, 48 cars total.
- Reference T-ECU hardware across all non-traction-power functions.
- Onboard battery at 360 kWh/trainset, Na-ion.
- HVAC designed for 50 °C ambient, verified in summer commissioning.

### D6. Infrastructure
- Switch machines: 8 on Line 1, 6 on Line 2, plus depot and yard throat switches.
- Level crossings: ~12 on Line 1 at-grade sections, ~8 on Line 2 — all instrumented into the consensus log the same way stations are.
- Track geometry CBM: every revenue service train carries the sensor package from D6.

### D7. Energy
- See §5. Samawah is an archetypal D7 deployment: sunny, grid-constrained, catenary-free.

### D8. Depot & Maintenance
- **East Depot:** main facility, 20 stalls, full CBM and workshop, 12 MWp PV + 40 MWh Na-ion microgrid. Training wing for operator personnel — part of the workforce domestication mission.
- **Northwest Junction layup:** 4 stalls, PV canopy, 5 MWh buffer, basic inspection only.

## 7. What This Means for `osr-sim`

Samawah is the **primary reference scenario** for `osr-sim`. Simulator development priorities:

1. **Topology import.** Represent Line 1 (12 stations + turnbacks), Line 2 (10 stations + layup), the two interchanges. Track geometry at RFC-0001 granularity (sections with offsets).
2. **Demand model.** Origin–destination matrix calibrated to the four anchor-types (station, centre, hospital, university) with time-of-day curves matching §4.2. Friday schedules as a first-class variant.
3. **Climate model.** A simple Samawah annual climate series (PSH, ambient temperature) drives both PV yield and HVAC load; this lets the simulator run an annual operations + energy profile, not just a single day.
4. **Fleet simulation.** 14 revenue trainsets plus spares with the battery model, running timetable-driven services, with opportunity charging at station stops per RFC 0002.
5. **Dust event injection.** Step-function drops in PV yield lasting 1–5 days are a modeled stress, used to validate storage sizing.
6. **Fault injection.** W-Node crashes, radio outages, grid outages. Tests that service degrades gracefully.

The existence of a concrete reference case is important for discipline: every feature added to `osr-sim` should demonstrably improve fidelity of the Samawah simulation, not just be abstractly useful.

## 8. Stakeholders and Partnerships

This is early and speculative, but the architecture only makes sense if it's eventually deployable. Plausible stakeholders to engage, ordered by likely path-opening value:

1. **Al-Muthanna University, College of Engineering** — natural partner for design-phase engineering work, student internships, and a credible domestic technical voice.
2. **Al-Muthanna Governorate** — transit planning authority and likely project sponsor.
3. **Iraqi Republic Railways (IRR)** — operator of the existing mainline; intercity interchange is via them.
4. **Iraqi Ministry of Transport** — for regulatory approval of novel signaling architecture.
5. **GIZ / German development cooperation** — given the new German Hospital anchor, there may be a natural coordination path with German-Iraqi development relations.
6. **Multilateral development banks** (World Bank, IsDB, AIIB) — likely financing routes for a novel urban-rail pilot.
7. **Domestic EPC and electronics industry** — the path to workforce domestication runs through companies that would actually fabricate PCBs, build switchgear, and integrate stations.

No engagement is being proposed here. This list exists so that when code is running and the simulator is working, there is a clear trajectory toward a conversation, not a blank map.

## 9. Open Questions

1. **Urban planning compatibility.** The indicative alignment in §3 must be compared against Samawah's urban plan before it can be taken seriously as a routing proposal. This is a desk exercise that a motivated student at Al-Muthanna University could do productively.
2. **Ridership reality check.** The 65,000–90,000 daily pax figure is a projection by analogy to mid-sized light-metro systems globally. A proper local demand study would refine it by a factor of perhaps 2×. The energy and fleet sizing have enough margin to absorb this, but station capacities and interchange geometry do not.
3. **Intercity interchange design.** How exactly does a passenger move between an intercity IRR train and the Line 1 metro at Samawah Railway Station? Platform-level integration is best; shared fare media is ideal but depends on IRR's modernization timeline.
4. **Bridge over the Euphrates.** Line 1 crosses the river between Samawah Central and Eastern Bridge stations. Existing road bridges may carry the alignment piggyback, or a dedicated rail bridge may be needed. Major capex item; outside this RFC.
5. **Construction phasing.** Full network in one go is unlikely. Plausible phasing: (Phase A) Line 1 western section, station → centre → Eastern Bridge; (Phase B) Line 1 eastern section, Eastern Bridge → University; (Phase C) Line 2 ring. Each phase must be operationally meaningful on its own.
6. **Land acquisition.** ROW is the single biggest planning-phase risk and is entirely local-authority territory; OSR technology cannot help here, only not make it worse (the catenary-free design needs no overhead easements, which is a small help).
7. **Women-only car policy.** Common in the region; implementable as a carriage-designation display change, but the social design of the service should be discussed with local stakeholders rather than assumed.
8. **Prayer-time service patterns.** Friday midday service should be adjusted for mosque access; Ramadan schedules differ from the standard day. These are timetable questions, not infrastructure.

## 10. Next Steps

With this RFC in place:

1. **Stand up `osr-sim`** with the Line 1 topology as the first scenario. A working annual simulation of the Samawah network is the single most effective artifact this project can produce for advocacy and engineering discipline.
2. **Run the energy numbers in simulation**, not just on a spreadsheet. §5 is a starting point; the sim will refine it and expose error margins.
3. **Draft RFC 0004 — Regulatory and Certification Path for Novel Signaling in Iraq**, since the SMRaft-based train control in RFC 0001 will face its first real regulatory conversation here.
4. **Publish an accessible summary** (Arabic + English) aimed at a non-technical audience at Al-Muthanna University and in governorate outreach, so that the project is visible to potential domestic contributors from the beginning rather than being announced after the fact.

---

*This RFC treats Samawah as a design target, not a prediction. Whether OpenSourceRail actually deploys here depends on decisions made by the people and institutions of Samawah and Iraq. What we commit to is: the reference design will be kept honest, the simulator will match the real geography, and the work will be done in public so that local engineers can contribute from day one.*
