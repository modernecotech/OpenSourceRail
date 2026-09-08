# LM3 Manufacturing and Assembly Reference Controls

> Status: **reference defaults — not a production or vehicle release**.

These are affordable pilot-factory defaults for work that should not wait for a
bespoke invention. They make assembly planning, quotations, travelers and first-article
inspection concrete while preserving every supplier, calculation, drawing and approval gate.

## How authority works

Reference defaults for first-article planning only. A released drawing, joint calculation, qualified process specification, supplier instruction, or authorised deviation takes precedence. These values do not release a vehicle, structural joint, glazing system, pressure boundary, HV system, lifting operation, or safety-critical installation.

The word **must** below controls use of this reference package; it does not certify a
component. Where a numerical product value is safety- or supplier-dependent, the default
states the required authority instead of guessing it.

## Common inspection escalation

- First article: 100% of defined characteristics.
- Safety and interfaces: 100% unless an approved control plan says more.
- Routine non-safety: first-off, last-off and 10%, minimum three per batch.
- Failure: on any failure, stop the batch, contain since last accepted check and inspect 100% until the approved control plan restores sampling.

## LM3-MFG-010 — Drawing, Datum And Measurement Control

Applies to: all MAKE parts, all assembly fixtures, all marriage interfaces.

Reference work instructions:

1. Use vehicle coordinates X forward, Y left and Z up; identify the car centre plane, bogie-centre planes and underframe top plane on every assembly drawing.
2. Locate work by a 3-2-1 datum scheme. Do not dimension serial features from one another or use an unverified body panel as a master datum.
3. Treat CAD nominal geometry as basic only where the released drawing provides a geometric tolerance; otherwise the dimension is not released for manufacture.
4. For non-safety brackets and trim only, use a provisional general shop tolerance of ±0.5 mm to 300 mm, ±1.0 mm from 300–1,000 mm and ±2.0 mm above 1,000 mm; hole position ±0.5 mm. A drawing-specific tolerance is mandatory at bogie, coupler, door, glazing, bearing, articulation and crash interfaces.
5. Verify each fixture at installation, after any move or repair, and before each first-article batch against traceable artefacts; record as-found and as-left results.

Inspection: 100% first article and all safety/interface datums; routine non-safety dimensions use first-off, last-off and at least one in ten, with a minimum of three per batch.

Stop and raise an NCR when: missing drawing revision; damaged or out-of-calibration gauge; datum disagreement above released tolerance; unrecorded CAD or NC revision.

Release evidence that supersedes/closes this default: checked detail/assembly drawing, tolerance analysis, inspection plan and calibrated measurement record.

## LM3-MFG-020 — Steel Preparation, Fit-Up And Welding

Applies to: underframe, body frame, bolsters, end rings, roof frame, bogie frame if locally manufactured.

Reference work instructions:

1. Receive material by heat/lot and preserve traceability through cutting and kitting; quarantine unidentified offcuts from structural use.
2. Deburr and remove cutting dross; keep weld lands free of oil, moisture, scale, coating and zinc unless the qualified procedure explicitly permits it.
3. Dry-build in the surveyed fixture, restrain only at released hard points, and record diagonals, twist, bogie centres, coupler centreline and door-portal datums before welding.
4. Use a balanced weld sequence from the centre outward, with inter-pass temperature, consumables, tack removal and distortion correction controlled by the qualified WPS.
5. No flame straightening, weld repair, weld-size substitution or hole enlargement is permitted without an approved repair/deviation instruction.

Inspection: 100% visual inspection and dimensional survey of first article; NDT method, extent and acceptance follow the released weld map and qualified procedure, never this default.

Stop and raise an NCR when: material certificate mismatch; unqualified welder or WPS; fit-up outside drawing tolerance; arc strike or crack; fixture movement.

Release evidence that supersedes/closes this default: released weld map/WPS, welder qualifications, material certificates, NDT plan and signed dimensional report.

## LM3-MFG-030 — Bolted And Captive-Fastener Joints

Applies to: service rails, interior modules, removable panels, roof equipment, structural bolted interfaces.

Reference work instructions:

1. Kit fasteners by joint ID, grade, coating, locking device and lot; do not mix visually similar hardware or substitute stainless/plated pairs without galvanic review.
2. Bring multi-fastener joints to contact by hand, seat in a cross-pattern, then apply the released final torque in at least two stages.
3. Use sockets within the calibrated tool range, record actual tool ID and setting, and apply a visible witness mark after final acceptance.
4. Do not publish or infer numerical torque from nominal diameter. Lubrication, coating, insert strength, prevailing-torque devices and supplier bearing limits control preload.
5. Replace single-use prevailing-torque fasteners and any fastener rejected by the released reuse rule; never re-torque a witness-marked joint unless the procedure requires it.

Inspection: 100% identity and witness-mark check on safety, roof, door, glazing, bogie, coupler, articulation and HV enclosure joints; normal service-rail joints first/last and 10% minimum three.

Stop and raise an NCR when: no numerical torque authority; tool outside calibration; cross-threading or spinning insert; witness mark broken; joint gap after seating.

Release evidence that supersedes/closes this default: joint calculation or supplier instruction, released joint schedule, batch record and signed torque trace.

## LM3-MFG-040 — Adhesive Bonding, Sealing And Glazing

Applies to: panoramic end glass, side glazing, bonded GFRP, roof PV laminates, sealed penetrations.

Reference work instructions:

1. Work in an enclosed clean zone at 18–30 °C, 30–75% RH and at least 3 °C above dew point unless the qualified product procedure is narrower.
2. Record substrate, cleaner, primer, adhesive/sealant and applicator batch/expiry; perform the supplier surface-preparation route and a witnessed adhesion coupon at the start of each shift/material combination.
3. Dry-fit with hard locators before priming. The released drawing must state glass edge clearance, adhesive bite/thickness, spacer hardness, drain path and installation gap.
4. Record start/end application times, environmental readings, bead continuity and clamp/removal time. Supplier open-time and cure limits are mandatory and are not replaced by this default.
5. Protect bond lines from movement, water, dust and coating until released cure; water-test glazing and roof penetrations before interior closure.

Inspection: 100% first article, every safety glazing perimeter and every roof penetration; retain witness coupons by material lot and shift through the defined evidence-retention period.

Stop and raise an NCR when: substrate below dew-point margin; expired or unmatched batch; missed open time; primer contamination; bead discontinuity; glass edge contact.

Release evidence that supersedes/closes this default: supplier-qualified bonding procedure, released glazing/bond drawing, coupon results, environment log and leak-test record.

## LM3-MFG-050 — Gfrp Body, Fascia And Roof Moulded Parts

Applies to: side and roof panels, front fascia pieces, lamp bezels, interior liners, fairings.

Reference work instructions:

1. Survey each mould from tooling datums before first use and after repair; clean, release and inspect it before lay-up.
2. Issue a ply/cut kit and resin/gelcoat batch traveler. Fibre type, orientation, overlap, core, resin ratio, vacuum level and cure cycle come from the qualified laminate schedule.
3. Use moulded or drill-jigged locator features; CNC-trim only from released datums and trial-fit the first part in the master body/fascia frame before drilling production parts.
4. Bond or mould inserts only with positive anti-rotation/pull-out features and witness samples; prevent exposed fibre and seal all trimmed edges and penetrations.
5. The fascia master gauge must simultaneously accept the glass dummy, lamp gauges, washer/sensor keep-outs and removable service panels without forced fit.

Inspection: 100% first article visual, thickness, mass, trim, insert and master-gauge inspection; production sampling follows the qualified control plan, while every safety insert remains individually traceable.

Stop and raise an NCR when: mould datum out; unreleased laminate schedule; cure excursion; dry fibre/void/delamination; insert movement; forced master-gauge fit.

Release evidence that supersedes/closes this default: qualified laminate/process specification, mould acceptance, coupon/mechanical evidence, trim program revision and signed first-article report.

## LM3-MFG-060 — Roof Hvac, Solar And Weatherproofing Assembly

Applies to: HVAC modules, PV rails and laminates, fairings, cable glands, condensate and roof drains.

Reference work instructions:

1. Complete a bench dry-build of rails, HVAC support frame, fairings, glands, drain paths and removable envelopes before the car roof is closed.
2. Lift equipment only from supplier points with a released lift plan; do not use PV rails, fairings or duct flanges as lifting points.
3. Maintain physical segregation between HV/PV, LV/data, condensate and fresh-air paths; route drains continuously downhill and provide cleanable traps only where shown.
4. Install replaceable equipment without permanent adhesive across its removal boundary; preserve roof access, fall-protection and emergency-isolation zones.
5. Perform staged water tests after bare roof sealing, after equipment installation and after fairing closure; electrically test bonding, insulation and PV isolation before energisation.

Inspection: 100% roof fasteners, penetrations, drains, isolation labels and leak-test zones on every car.

Stop and raise an NCR when: standing water; unsealed penetration; blocked removal path; missing lift point; failed bond/insulation test; supplier mass/CG absent.

Release evidence that supersedes/closes this default: released roof arrangement and load calculation, supplier manuals, lift plan, water-test map, electrical test and mass/CG record.

## LM3-MFG-070 — Interior Fit-Out And Service Routing

Applies to: floors, seats, panels, lighting, grab rails, PIS/CCTV, harnesses, hoses.

Reference work instructions:

1. Complete concealed harness, duct, drain and fire-barrier inspection before floors, ceilings or service panels close the zone.
2. Use the common service rail and keyed connectors for non-structural modular fit-out; passenger load-bearing fixtures require a released load path and proof evidence.
3. Route cables and hoses in dedicated trays, protect every edge crossing, support branches close to connectors, and preserve supplier minimum bend radius and service loop.
4. Apply unique labels at both ends and every branch; run continuity/insulation/network checks before energisation and again after panel closure.
5. Dry-fit floors and panels from the centre datum outward, preserve drainage/inspection hatches, eliminate trip lips and sharp edges, then gauge PRM aisle, door circulation and emergency access.

Inspection: 100% concealed-route photo/map, connector identity, safety fixture and accessibility check; cosmetic modules use first/last plus 10% minimum three.

Stop and raise an NCR when: unreleased routing drawing; chafing or unsupported span; mixed HV/LV zone; blocked access panel; failed fire barrier; PRM gauge obstruction.

Release evidence that supersedes/closes this default: released routing and fit-out drawings, fixture load calculation/test, cable test report, fire-material evidence and dimensional gauge record.

## LM3-MFG-080 — Module Marriage, Lifting And Recovery Interfaces

Applies to: body-to-bogie marriage, battery/HVAC modules, train ends, articulation, jacking and rerailing points.

Reference work instructions:

1. Weigh each accepted module and record centre of gravity before planning the lift; compare cumulative body mass and reactions with the controlled mass ledger.
2. Use only marked, rated and proof-accepted lifting/jacking points with positive cribbing and a released synchronous lift plan; establish an exclusion zone and appoint one lift controller.
3. Mobile lifting columns are the factory default for carbody/bogie marriage. Portable screw or scissor jacks are a recovery option only when the selected units, foundations/packing, side-load restraint and vehicle jacking pads are specifically engineered and proof tested.
4. Raise in defined increments while monitoring level and pad load; stop on unequal load, unexpected deformation, loss of communication or support movement.
5. After marriage, record ride heights, axle loads, clearances, hoses/cables, retention devices and fastener witness marks before static energisation.

Inspection: 100% lift-point identity, equipment certificates, pre-use check, lift log and post-marriage geometry for every vehicle movement.

Stop and raise an NCR when: unknown mass/CG; expired lifting certificate; unverified ground or cribbing; side-loaded jack; pad load imbalance; person beneath unsupported vehicle.

Release evidence that supersedes/closes this default: checked lift/recovery plan, equipment schedule/certificates, jacking-pad calculation and proof test, lift log and post-marriage survey.

## LM3-MFG-090 — Finish, Corrosion Protection And Livery

Applies to: steel structure, GFRP exterior, livery film, roof radiative coating trial.

Reference work instructions:

1. Inspect and record hidden steel preparation and base corrosion system before panels, floors or equipment conceal it.
2. Use pre-coloured GFRP and replaceable rail-rated livery film on approved smooth zones to reduce spray finishing; seal cut edges and keep film clear of joints, vents, drains, labels, sensors and inspection areas.
3. Apply film to a clean dry surface within the film supplier temperature window, use knifeless tape at visible boundaries and record batch, installer and adhesion trial.
4. Calcium-carbonate nanoparticle roof coating remains a controlled trial over the mandatory fire/UV/weathering-compatible base system; it must not cover PV, bonded joints, walkways, vents, drains or earth bonds.
5. Compare trial and control coupons for adhesion, fire/smoke, UV/weathering, cleanability, solar reflectance and thermal benefit before fleet use.

Inspection: 100% hidden base protection, prohibited zones and first livery/roof trial; routine film appearance and edge adhesion by first/last plus 10% minimum three zones.

Stop and raise an NCR when: unprotected steel; surface contamination; film over inspection/safety feature; roof coating without compatible base; failed coupon or peel edge.

Release evidence that supersedes/closes this default: released finish-zone map, coating/film supplier system, environmental log, coupon qualification and signed appearance/corrosion inspection.

## LM3-MFG-100 — Ncr, Rework And Configuration Handback

Applies to: all parts, all suppliers, all build cells, all test stages.

Reference work instructions:

1. Tag and segregate nonconforming material or digitally inhibit its next operation; never erase the original result or repair before disposition.
2. Disposition is use-as-is, rework to the original requirement, repair to an approved instruction, return/scrap, or design change. Only the named design authority may approve use-as-is, repair or design change.
3. Repeat all inspections invalidated by rework and extend the check to adjacent features that could have been affected.
4. Before cell handback, reconcile installed serial/lot numbers, software/configuration IDs, concessions, open work, tool records and measured mass with the as-built record.
5. A red-line is temporary build evidence, not a revised design; incorporate accepted changes into controlled source and reissue before repetition.

Inspection: 100% NCR and concession traceability; quality independently verifies closure and configuration reconciliation before the next release gate.

Stop and raise an NCR when: unidentified part; unapproved repair; repeat defect trend; missing retest; as-built/configuration mismatch; open safety NCR.

Release evidence that supersedes/closes this default: approved NCR disposition, repair instruction, repeat-inspection evidence, updated design revision and signed configuration handback.
