# Baghdad: zero-tunnel, viaduct-first, catenary-free design rebaseline

**Proposed design decision for the release after v0.7.0 — 17 November 2026.** This is a cost-and-feasibility screening specification, **not** a revised published v0.7.0 cost, a supplier quote, a fabrication release or permission to operate. Retain the immutable [v0.7.0 Baghdad estimate](https://github.com/modernecotech/OpenSourceRail/blob/v0.7.0/cities/Baghdad/COST-AND-DELIVERY.md) as the comparison case.

## 1. Non-negotiable project purpose

Deliver a safe, accessible and affordable driverless urban railway that Iraq can design, build, maintain, repair and improve. Make the civil structure simple to produce locally; simplify installation and disruption; keep open specifications and local ownership of design information. Rank options by **installed cost, whole-life cost, reliable passenger capacity, construction time, local value added and maintainability**. Do not allow one subsystem's apparent saving to increase the total railway cost.

The **new Baghdad candidate has zero tunnels and zero underground passenger stations**. Cross streets, railways, waterways and utility corridors on grade-separated viaducts; keep depots and non-conflicting support facilities at ground level. For mainline service, the preferred cost comparison is **100% elevated revenue guideway**. Test an above-ground mixed elevated/at-grade option only where it has independent right of way, no public road level crossings and an explicit safety, access and disruption case. Grade and curvature must come from an actual mapped alignment; a tunnel-free policy does not prove every original route can be retained unchanged.

**No continuous overhead catenary is the preferred architecture**, but it is a **whole-life-cost preference, not a physical prohibition**. Keep the overhead-powered v0.7.0 system as an equal-service benchmark until batteries, power distribution and charging are properly priced. Do not assert that deleting an overhead line deletes the cost of supplying electrical energy.

## 2. Preserve wheel-supported trains; reopen the energy supply decision

For the Baghdad 700-place, six-car service, compare these alternatives at the **same route, grades, passenger load, 150 s headway, peak dwell, climate and fault-reserve**:

| Candidate | How it moves | Continuous overhead wire? | Design caveat |
|---|---|---|---|
| A — battery-electric with station/depot charging | Powered steel-wheel bogies, onboard storage, automatic protected station connectors | No | MW charging pulses; hot-weather battery mass, cooling, degradation and replacement |
| B — protected continuous conductor rail | Powered bogies and guarded wayside power rail on segregated elevated guideway | No | Still a continuous electrical railway; emergency evacuation, contact protection and maintenance require specific engineering |
| C — battery plus limited protected wayside supply | Powered bogies and storage, with short energized segments or high-power stations | No | Size of storage, energized length, power peaks and isolation are separate design variables |
| D — continuous 1.5 kV overhead | The released powered-bogie comparator | Yes | Masts, collection, access, maintenance and visual/clearance cost; may nevertheless be cheaper over 30 years at very high frequency |

Mechanical spring arrestor/relaunch, passive-only station launch and ferrite/maglev remain **research alternatives**, not the default network architecture. In the existing [equal-service evaluation](../../docs/design-engine/v07-architecture-decision/README.md), station-only propulsion cannot complete sustained uphill cases. Independent service and emergency braking remain mandatory regardless of regenerative braking or storage.

Practical catenary-free commercial examples exist, but are not directly scalable without calculation. [Alstom SRS for tramway](https://www.alstom.com/sites/alstom.com/files/2021/09/17/Alstom_Product_Sheet_SRS_for_Tramway_NS_EN.pdf) lists **1.2 MW charging for 20 seconds** (6.7 kWh at its terminals, before losses), and [CAF Freedrive](https://www.cafmobility.com/en/solutions/trains/tram-light-rail/) offers overhead-free energy-storage trams. Neither proves a 700-place Baghdad metro can be recharged within its selected dwell. [Network Rail's traction strategy](https://www.networkrail.co.uk/wp-content/uploads/2020/09/Traction-Decarbonisation-Network-Strategy-Interim-Programme-Business-Case.pdf) found full electrification can win on whole-life cost as service becomes frequent, in a different rail operating context. Test, do not assume, whether that applies to Baghdad.

## 3. First arithmetic rebaseline: remove all tunnels

Use the current [Baghdad v0.7.0 ledger](COST-AND-DELIVERY.md) unchanged as the reference: 148.2 km/$8,340.593m capital and 605.652 km/$32,557.218m (the large network includes the small). Published rates are tunnel $70m/route-km, elevated $9m/route-km and at grade $4m/route-km. The original direct-to-installed multiplier is **1.326**: 8% design + 2.5% test on preceding direct costs, followed by 20% project allowance.

| Civil-only change, **same remaining scope and prices** | 148.2 km (US$bn) | 605.652 km (US$bn) |
|---|---:|---:|
| Published v0.7.0, mixed tunnel/elevated/at-grade | 8.341 | 32.557 |
| **No tunnels:** replace 8 km / 30 km of tunnels with elevated track; retain other at-grade mileage | **7.694** | **30.131** |
| **All viaduct:** additionally raise 35.2 km / 170.652 km of at-grade revenue guideway | **7.927** | **31.262** |

For the first programme, tunnel replacement saves (70 − 9) × 8 × 1.326 = **$647.088m** installed. Raising the remaining 35.2 km costs (9 − 4) × 35.2 × 1.326 = **$233.376m** installed. Net all-viaduct saving is **$413.712m**, **not** $647m. For the larger concept, the respective numbers are **$2,426.580m** saving and **$1,131.423m** additional, net saving **$1,295.157m**. These are arithmetic substitutions only: route length, bridge crossings, station type, foundations, property, pier clearance and elevated access can change; **do not publish them as validated budgets**.

### Guideway value engineering, not just replacing tunnel kilometres

The 30 km reference uses 10 m spans with 6,000 independent beam placements and 6,002 support positions for double track. Applied mechanically to 148.2 km that implies about **29,640 beam placements** and independently supported positions of similar order. Test a **common pier and crosshead for two parallel beams** and repeatable **20–30 m spans** where street geometry, mass and crane access allow, retaining shorter modules for constrained sites. Compare installed concrete/steel, foundation count, factory capacity, transport, lifting equipment, lane closure time and repair access. A longer beam is not automatically cheaper; a 10 m span count is not automatically efficient.

## 4. Battery and no-overhead power reality check

Baghdad's current planning model uses **20 kWh per six-car train-km**, ~**201.7 t** crowd mass, **700 places**, **150-second peak interval**, **35-second dwell**, and **64 stations across seven lines**. Its notional mean interstation distance is 148.2 ÷ (64 − 7) ≈ **2.60 km**; real spacing will vary.

* A train consumes **~52 kWh** over 2.6 km under the current whole-service energy assumption. To replenish all of this within 35 s at **90% charge-chain efficiency** needs **~5.94 MW per train** at the charger. This is an indicative upper-activity case, not a charging-system design. Charging at termini, additional coasting and a larger onboard energy reserve can reduce per-stop peak, while making another charging duty more demanding.
* A 201.7 t train at 20 m/s has **~11.2 kWh** of kinetic energy. Climbing 1% for 2.6 km requires **~14.3 kWh of potential energy** before rolling or air resistance. Thus a passive train launched to 72 km/h **cannot** reach the next station on that grade. The previous station-only launch is not a credible universal network baseline.
* Reaching 20 m/s from rest in 200 m takes **~1.0 m/s²** average acceleration and roughly **4 MW mechanical power near the end**, excluding grades and losses; a short station motor is therefore not automatically cheap or gentle.
* First-programme annual traction/auxiliary demand in the current model is **~1,049 GWh**, averaging **~160 MW over 18 operating hours/day**. Roof and station solar can help auxiliaries and station buffers but cannot be presented as the sole supply for this intensive metro without an independently checked generation and storage model.

The existing overhead/feeders/grid scope includes **$1.2m per track-km plus $8m per substation**. In the first programme this is **$355.680m route equipment + $240.000m for 30 sites**; for the metropolitan concept **$1,453.565m route equipment + $800m for 100 sites**. **Neither amount is an automatic saving**. Chargers still need grid connections, feeders, site civil works, buffering, power electronics and controls. The line-equipment amount is an absolute **upper-bound accounting envelope** for equipment potentially omitted, not a verified avoidable OLE quote; it contains some common electrical functions.

An honest no-catenary cost becomes:

> Tunnel-free viaduct capital − **verified avoidable** overhead-specific scope + station/depot chargers + retained/changed grid and substations + onboard batteries/converters/collectors + cooling and fire protection + charge-buffer storage + added fleet/maintenance capacity + design, testing and contingency.

The **30-year comparison** must also price battery and buffer replacement, charge losses, charger downtime, grid-demand charges and temperature-driven degradation, against overhead or conductor-rail inspection and renewal. Do **not** preserve the old $5/train-km operating rate across unlike propulsion options by assumption. Express local share as evidenced Iraqi invoices and labour hours, not counts of locally labelled parts.

## 5. Finite execution plan

1. **Lock the brief.** Publish the no-tunnel/no-underground-stations rule and the no-overhead preference in one machine-readable Baghdad scenario. Keep v0.7.0 immutable; record the next revision as a new candidate with a new version and ID.
2. **Remap seven lines above ground.** Mark every Tigris crossing, road/rail overpass, clearance, steep grade, available right of way, pier footprint and accessible entrance. Do not claim the RFI's 148.2 km is the new buildable length until the above-ground route is measured.
3. **Civil quantity generator.** Build repeatable 10/20/25/30 m span and paired-track pier alternatives; output pier/foundation count, tonnage, lifting class, factory shifts, disruption days and priced guideway/station rates. Feed the same quantities to BIM, bill of materials, delivery and cost.
4. **Equal-service energy model.** For each route segment and direction, run empty/normal/crowd mass, peak heat, 0–2% representative grades plus real-site grades, degraded braking and 150 s headways. Report speed curve, kWh per interstation, peak charging MW, battery energy/power and reserve, traction/supply ratings and substation simultaneous load.
5. **Quote A/B/C/D power alternatives.** Obtain equipment supply plus installation, depot infrastructure, safety isolations, 30-year renewals, charging/battery thermal limits and maintenance costs. Store quoted unit rates and provenance in one machine-readable cost ledger; retain unknowns as unknowns.
6. **Select architecture once.** Calculate matched per-route-km installed cost, whole-life present cost, cost per delivered passenger-km under an explicit demand forecast, uptime, battery life, construction disruption, and Iraqi value added. Choose the least expensive feasible whole system subject to hard safety/accessibility gates, while publishing why any catenary exception is justified.
7. **Release an RFQ-ready demonstration design.** Propose 1.5–2 km of viaduct, one 700-place train representative car/drive module, one station charge or conductor segment, protected braking, rescue walkway and test procedure. A viable digital quote/production pack does not require mm-level final detailing of every part, but it must fix interfaces, operating loads, quantities, material grades, supplier responsibilities and unresolved holds.

**Stop rule:** do not create more city catalogues, redundant bespoke cost engines, rendered copies or new architecture variants until the four costed traction cases and the two civil alternatives can be compared from one measured input set. Tests should check numerical identity, units, no-tunnel constraints, energy balance, cost scope double-counting and persistence across Workbench edits. Reuse the existing calculation engine rather than cloning it for Baghdad.

## Communication and public-facing changes once the alternative is chosen

Lead the README and Baghdad proposal with **“tunnel-free, predominantly prefabricated elevated urban railway; overhead-free preferred subject to whole-life proof”**, giving the selected system and its status in plain language. Put v0.6 passive launch and v0.7.0 overhead examples in an explicitly labelled research/history section. Show one public cost per **named and dated** candidate, with understandable currency and assumptions; avoid presenting a draft comparison figure as the final procurement budget.

