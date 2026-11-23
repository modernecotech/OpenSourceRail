# Baghdad Airport vehicle and local factory enquiries

Price one representative equipped car, one separately orderable equipped powered bogie and the repeat order of six six-car sets. The 36-car opening uses three diagrammed sets and three spares. Six-stop, 12 km Airport service and protected conductor rail define the duty. The v0.8 enquiry schedules use the existing Airport first-article geometry and planning quantities. The buyer should issue these schedules with the source drawings and agree the delivery location, programme, witness arrangements and bid deadline for each competition. Fabrication and passenger-service releases remain on hold. [Airport prototype and downloadable drawings](../README.md)

| Enquiry | Common buyer quantity | Comparable price treatment |
|---|---:|---|
| `pilot-car` | 1 equipped 17 m car with two bogies | $1.696m–$3.392m planning range. Show the charge for first-of-kind engineering, the credit for any separately supplied bogie and the credit if the car is accepted into the series. |
| `pilot-bogie` | 1 equipped powered bogie with two driven axle positions | $0.318m–$0.742m planning range. Show the standalone delivered price and the credit for incorporation in the pilot car or series. |
| `fleet` | 6 complete six-car sets | $50.88m planning allowance. Return price for all 36 cars and separately identify the net balance after confirmed pilot reuse. Supply, integration and supplier factory tests form part of the complete fleet return. |
| `tooling` | 1 opening programme with vehicle lines itemised | $44.80m planning allowance for shared opening tooling and recovery scope. Identify the vehicle share and dependencies. A scoped vehicle-tooling subtotal needs reconciliation before it can replace the complete allowance. |
| `depot-control` | 1 depot and 1 control centre in the parent lot | $75.00m combined parent allowance. Price the workshop and stabling share and identify support interfaces with the control centre. |
| `test-vehicle` | 1 independent physical test programme | Nested inside `integrated-test`. Show witnesses, setup, measurement, reporting and retest separately from supplier factory acceptance. |
| Routine support and major renewal | 6 sets, with explicit annual service and event years | Cross-reference `opex-other`, `opex-payroll` and `renewal-fleet-major-renewal`. The planning renewal is $38.16m in operating year 25. Return the actual triggers, prices and asset population. |

Planning amounts are constant 2026 USD. Quote owner-controlled tests, fixed tools, workshop assets, consumables, repair contracts and recurrent training as identifiable lines. Allocate each line once to its owning contract and show inclusions and credits. Keep on-vehicle rescue interfaces inside the rolling-stock offer and price fixed recovery equipment, wayside recovery and operator drills against their applicable owners. A supplier alternative carries its own drawings, interface and mass changes, verification plan, commercial return and evaluation identity. [Buyer estimate and overlap rules](../PROCUREMENT-PLAN.md) · [Canonical estimate edition and lot definitions](../sourcing-estimate.json)

Review the [installed-car general arrangement](INSTALLED-GA.md) for positioned and open fitout, door and bogie datums, and quantitative design allocations.

## Source and issue register

| Record | Current identity |
|---|---|
| Airport physical candidate | `b38d4bd348cc57d8f3fab9696df06e5b35ba51380670aa8e566b7f89d9c5da01` |
| Airport opening evaluation | `6a0580105823dbd30dadde4e44f7d9032aee7a4b210e229950d17673a7231e87` |
| Frame revision | `5904e648c5de9b4b6ad5cf4c0c5ebfa93d5a35c2c746b3c12ae52eed49c929ae` |
| Mechanical article evaluation | `4ab9d5d23b03233335034bc983ea82fef736053fa2cdd681cf447548897bd351` |
| Packet evaluation | `f1f0ca81dc1ee27c63cea9a404a62117a5b4799c5126938e000bdfbf74116772` |
| Buyer estimate edition | `83de4f2c3023521a1b9a9b02c436b10ffa9c24a67763d700da624e53036ad095` |
| Separate citywide selection | `d514564801b2df2cd8b2a06e59619b5aff6e0ec425256117120047a937c9aeaf` |

Extract the [source packet](../airport-prototype.zip) and verify filenames and SHA-256 values against `manifest.json`. Send `opening.json`, `service.json`, `mechanical.json`, `car-and-bogies.ifc`, `revised-cuts.csv`, `opening-bom.csv`, `portal-detail.svg`, `powered-bogie-sheet.svg`, `door-leaf-travel.obj`, `fitout-interfaces.json` and the relevant return forms with the vehicle enquiry. Include `draft-work-orders.json` for factory review. This workshop draft binds the opening in `source_bindings.opening` and has its own evaluation ID. Record the issued files and hashes on the RFQ. The citywide selection has its own fleet and service quantities. [Citywide service decision](../../../CITYWIDE-SERVICE.md)

## Complete the return

1. Copy the [vehicle schedule](vehicle-quote.csv) and [factory schedule](factory-quote.csv). Keep the enquiry IDs and buyer quantities. Complete the supplier columns or mark the specific field open, excluded or included in a named line. Where a planning quantity remains open, state the counted or bounded quantity and unit. Supply subordinate schedules if one row contains multiple part numbers or years. [Factory routing and handover](factory-routing.md)
2. Attach the signed quotation with supplier and manufacturing sites, contact, quote reference and revision, issue and expiry dates, RFQ round, candidate/frame/edition IDs and bid scope. Give currency and price base, tax and duties, Incoterm and named place, payment milestones, escalation, lead-time trigger, first delivery and dated series deliveries, warranty and response times. Break out the unit rate, extension, non-recurring engineering/tooling, freight, installation, labour, spares, tests and commissioning. State all deviations, splits by maker and country of origin, and any restrictions on repair, data and tooling ownership.
3. For every technical row, return revision-controlled drawing/part IDs, material, supplier quantities and dimensions with units, proposed production limits, mass by assembly with fluid condition and measurement basis, and the evidence reference and status. Give provenance and uncertainty or range for a declared mass. Retain blanks or open status where data are pending. Use the archived `returns/fitout.csv` for detailed fits and measured margins and `returns/weights.json` for grouped train mass and axle evidence. The 5.273 t/car stock figure includes bare frames and liners. The 201.55 t loaded train is a planning sensitivity. [Fitout instructions](../fitout-guide.md) · [Weighing instructions](../weight-guide.md)
4. For routine upkeep and renewable items give the applicable asset population, interval or trigger, shop task, labour and materials, consumables and recommended spares, downtime, lead times and warranty coverage. Give the annual price and event year, amount and quantity for each renewal. Supply explicit declarations for zero additional scope; unresolved prices and intervals stay open. Compare parent lots only after the scope and pilot credits reconcile. [Commercial return and annual cash](../commercial-guide.md)
5. Buyer records one controlled RFQ round per lot, keeps supplier returns confidential and checks comparability, expiry, delivery programme and credit coverage. Technical review records separately the drawing compliance, tests still due and proposed exceptions. Preserve signed originals, issuer/date, serial and attachment hashes. The award, approved build release, acceptance and operating authority have separate records. [ERPNext buyer procedure](../PROCUREMENT-PLAN.md) · [Witnessed commissioning](../../commissioning/COMMISSIONING.md)
