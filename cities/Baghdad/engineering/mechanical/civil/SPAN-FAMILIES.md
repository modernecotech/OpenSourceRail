# Compare straight viaduct spans and supports

Compare the issued 10 m box with independently sized U-girders and a two-piece box under the same route, load and erection conditions. The earlier comparison kept one box and cage throughout. Its approximate $118m direct saving and $7,975 per 20 m placement headroom belong to the 148 km first programme. [Earlier common-section sensitivity](SPAN-COMPARISON.md)

This screen uses 12 km of continuous double track, one straight run, 24 axles and 198.64 t at normal study crowd load. The shared running-line trial has 4.50 m track centres. Station islands require a different arrangement. End bents count once per continuous line. A partial end bay is budgeted as a whole placement. Its closure length and excess ordered length are reported separately and the closure design and price remain open.

### Which design to quote

26 trials were investigated at 200 kPa. 0 require a foundation outside the modeled family. 26 have a priced civil subtotal, 9 pass the stated checks, and 9 satisfy both conditions. No common site rating was entered at 12 m. Each contractor offer is checked against its stated working load. Each price case identifies the lowest estimated 30-year present value among trials that pass and carry a price. Confirm supplier scope, the load chart and independent design review before procurement.

| Rate case | Lowest 30-year cost among screened options | Installed $m/km | 30-year PV $m/km | Haul and erection rates |
|---|---|---:|---:|---|
| low | 20m U 1.55m / shared | 5.95 | 6.07 | 12 m planning rate |
| base | 20m U 1.55m / shared | 8.97 | 9.35 | 12 m planning rate |
| high | 20m U 1.55m / shared | 15.63 | 16.86 | 12 m planning rate |

### Shallow foundation case

The following base-rate comparison assumes 200 kPa. Each single-track U has 3.60 m of nominal clear channel. Each standard depth and its 200 mm deeper counterpart were evaluated. The table gives the candidate with the lowest priced 30-year present value among the two depths passing the listed stress and handling screens, separately for each pier arrangement. Where neither depth passes, the table gives priority to a modeled foundation, then fewer failed checks and the lower projected cost if tied. The JSON retains every depth and every failure. The two-piece option is a new post-tensioned box with a match-cast joint and a temporary tower at midspan.

| Span and family | Depth m | Pier | Footing width m | Supports | Lift unit t | Strand count | Hook demand / matched price band t at 12 m | Installed $m/km | 30-year PV $m/km | Extra $/placement to match 10 m¹ | Screen |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 10 m issued-box | 1.40 | separate | 3.75 | 2,402 | 34.2 | 12 | 42.0 / 60 | 9.93 | 10.69 | +0 | trial screens pass |
| 10 m issued-box | 1.40 | shared | 5.25 | 1,201 | 34.2 | 12 | 42.0 / 60 | 9.81 | 10.57 | +566 | trial screens pass |
| 10 m U | 1.15 | separate | 3.75 | 2,402 | 30.3 | 16 | 37.7 / 60 | 10.64 | 11.40 | -3,543 | trial screens pass |
| 10 m U | 1.15 | shared | 5.25 | 1,201 | 30.3 | 16 | 37.7 / 60 | 10.52 | 11.28 | -2,982 | trial screens pass |
| 15 m U | 1.32 | separate | 4.00 | 1,602 | 50.5 | 28 | 59.9 / 60 | 9.13 | 9.64 | +5,944 | trial screens pass |
| 15 m U | 1.32 | shared | 5.75 | 801 | 50.5 | 28 | 59.9 / 60 | 9.11 | 9.62 | +6,134 | trial screens pass |
| 20 m U | 1.55 | separate | 4.25 | 1,202 | 77.7 | 38 | 89.9 / 110 | 9.06 | 9.44 | +8,645 | trial screens pass |
| 20 m U | 1.55 | shared | 6.00 | 601 | 77.7 | 38 | 89.9 / 110 | 8.97 | 9.35 | +9,578 | trial screens pass |
| 25 m U | 1.82 | separate | 4.75 | 962 | 112.7 | 48 | 128.4 / 180 | 9.45 | 9.75 | +6,012 | footings touch or overlap |
| 25 m U | 1.82 | shared | 6.75 | 481 | 112.7 | 48 | 128.4 / 180 | 9.47 | 9.77 | +5,714 | trial screens pass |
| 30 m U | 1.92 | separate | 5.00 | 802 | 149.6 | 68 | 169.0 / 180 | 8.93 | 9.19 | +14,885 | lifting tension, footings touch or overlap |
| 30 m U | 1.92 | shared | 7.50 | 401 | 149.6 | 68 | 169.0 / 180 | 9.11 | 9.36 | +12,319 | lifting tension |
| 20 m joined-box | 1.55 | separate | 4.25 | 1,202 | 41.7 | 28 | 50.3 / 60 | 10.87 | 11.43 | -4,729 | transfer tension |
| 20 m joined-box | 1.55 | shared | 6.00 | 601 | 41.7 | 28 | 50.3 / 60 | 10.78 | 11.33 | -4,260 | transfer tension |

¹ Positive headroom is the additional installed dollars this alternative can absorb per actual lifting placement before matching the independent 10 m box at the same length and rates. A negative number means it is already dearer. Complete installed prices remain open.

A partial figure includes only priced work. The JSON lists every included amount and the outstanding scope in `partial_cost_cases`. When the crane has no price, the material, casting, forms and modeled support costs remain visible. They do not enter the quotation ranking on their own.

### What changes the order

These three design sensitivities show how soil and price uncertainty affect the installed subtotal. An asterisk marks a footing trial where the independent pads touch or overlap. The preceding table gives each design's failed checks.

| Quotation case | Low / base / high installed $m/km | 150 / 200 / 250 kPa installed $m/km at base rates |
|---|---:|---:|
| 10m issued-box 1.40m / separate | 6.51 / 9.93 / 17.54 | 10.22 / 9.93 / 9.81 |
| 20m U 1.55m / shared | 5.95 / 8.97 / 15.63 | 9.47 / 8.97 / 8.90 |
| 25m U 1.82m / shared | 6.31 / 9.47 / 16.39 | 10.03 / 9.47 / 9.29 |

The U is wide enough for a preliminary body-clearance trial. Its floor, web thickness, depth, gross area, centroid and inertia vary by span. Each U span has a full-pretension trial and a 200 mm deeper staged version. The latter takes roughly 30% of the final strands for handling, with 0.08L pickup inset, then adds profiled post-tensioning after landing. Extra ducts, anchors and stressing are priced. Stock stress is checked at pickup, midspan and on landing with the initial strands. Duct drape, end anchorage and losses need a supplier design. Prestress uses the issued strand's initial force and 30% loss, with zero bottom tension at peak positive service moment as a design target. The 10 m reference retains 12 strands. Hogging during the lift and full-transfer fibre stresses are separate screens. The deflection result bounds gross-section gravity curvature. Creep, cracking, camber, prestress transfer length, fatigue, local wheel load distribution and shear/torsion capacity require detailed design. The reported torque acts at the support pair. Open-section warping and lateral stability need shell analysis and a lifting trial. Check computed movement against rail, collector and boarding tolerances. This train uses a protected conductor and steel wheels.

Enter a positive site bearing pressure using `--soil-kpa`. The 150, 200 and 250 kPa comparisons remain visible. Two adjacent beam ends load an interior bent. The shallow trial evaluates square widths of 2.5–25 m in 0.25 m increments until vertical bearing and no-uplift trials pass for longitudinal braking and either one or both loaded tracks. Each cap extends at least 250 mm beyond the outer bearing pad. The common pier has a wider and deeper cap. Its one-sided train loads can govern the footing. Wind, seismic, piles, settlement, utilities, drainage, clearances and cap reinforcement need site-specific offers. Both foundations at the ends are conservatively priced as interior sizes.

The 60 t figure originated as a provisional lifting assumption with no verified crane chart. [Original pilot lifting inputs](https://github.com/modernecotech/OpenSourceRail/blob/5ffe46dceb9e23db594fbe033c472fd847772969/engineering/pilot_civil/policy.json#L103-L110)

Each piece takes one haul and one lift. Hook demand includes assumed 4 t rigging and a 1.10 handling multiplier. The 60, 110 and 180 t bands estimate costs at 12 m radius. A heavier lift requires a new price. Set `--lift-radius-m` to the surveyed radius and `--crane-limit-t` to the available working load at that radius. Changing radius changes the chart requirement and rate coverage. The suspended mass and rigging still determine hook demand. Verify the radius, rigging, ground bearing and lift method at the site. The segmented option pays for match casting, tensioning and tower cycles. Check the joint at full tendon force with the tower still engaged, then with the tower removed. A failed supported-joint stress check requires a redesigned tendon or a controlled, analysed unloading sequence. Lifting an unstressed half requires its own reinforcing and local pick design. The yard trial holds eight moulds, with 24 h and 48 h release cycles. Obtain occupation and capacity returns alongside the traffic closure bids.

The 1.5 MPa release tension and 18 MPa release compression checks are provisional material targets. The three shallow soil pressures are hypotheses. Obtain release-strength data, surveyed soil and authority criteria before structural selection. Prices use the repository's Iraqi cement, sand, gravel, reinforcing steel and currency inputs. Low/base/high are estimate cases covering ordinary civil scope, casting, haul, bearings, equipment, erection, disruption and support works. The other-elevated allowance is common per route-km. Trial moulds, strand rates, traffic bookings, maintenance and crane-class uplifts are estimating assumptions. The 30-year present value includes annual inspections and one bearing replacement at year 20 discounted at 4% real. Check contractor inclusion credits, abnormal haul limits, pile/special works, traffic staging, time-dependent PT maintenance and disruption before accepting a total. A low installed subtotal alone cannot select a design.

Delhi Metro explicitly allows precast small U girders up to 30 m and describes two-crane erection and traffic constraints. Obtain local truck paths, lifting charts, designs and quotations for the same operating conditions. [Delhi Metro civil construction specifications, section 10.1.1](https://backend.delhimetrorail.com/documents/8790/OUTLINE_CONSTRUCTION_SPECIFICATIONS_for_Civil_Works_Revision-R4_June_2025.pdf)

Run the same comparison for another route length, soil pressure, train or material from the repository root. The input hashes, study assumptions, envelopes, footprints, work quantities and low/base/high cost breakdowns are included in JSON.

```sh
python3 -m cities.Baghdad.engineering.mechanical.civil.family_comparison --check
python3 -m cities.Baghdad.engineering.mechanical.civil.family_comparison --route-km 18 --soil-kpa 150 --crane-limit-t 60
python3 -m cities.Baghdad.engineering.mechanical.civil.family_comparison --lift-radius-m 18 --crane-limit-t 95.5
python3 -m cities.Baghdad.engineering.mechanical.civil.family_comparison --route-km 148.2 --soil-kpa 150 --json > build/span-families.json
```

To enter a contractor return, copy the exact `physical_id` and `placements` from the relevant trial's JSON. This example uses the deeper 20 m U on a shared pier. The haul and erection rates are delivered USD per placement, exclusive of traffic closure. The working load must cover modeled hook demand at the quoted radius.

```json
{
  "supplier": "Example contractor",
  "offer_id": "example-A",
  "physical_id": "6c9560ea68ef50fed774f256a8d7d373cad9a7e2fd590eb086e553dc802ff076",
  "placements": 1200,
  "lift_radius_m": 18,
  "working_load_t": 95.5,
  "haul_usd_per_placement": 1200,
  "erection_usd_per_placement": 3500,
  "placements_per_shift": 4
}
```

Run the matching scope with `--lift-radius-m 18 --erection-offer offer.json`. Repeat `--erection-offer` for other bidders. Matched returns replace the planning haul and erection rates. For each rate case the model compares those offers including traffic closures at their respective production rates. Materials, the price per closure and other civil work retain their estimating basis. Each return has a digest and match status in JSON.

Evaluation `8034e0f4e19877c032d247258f827b2bcc2aa8132e0e52049540c48192c22400`. All cases remain open for independent engineering review.
