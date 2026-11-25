# Engineering decisions and evidence

The Airport example exposes a contradiction that affects every track metre, train diagram and supply site. Five mapped passenger-area centroids are at least 15.09 km apart in stop order. The six-stop, 12 km schematic remains available for reproducing earlier estimates. Use the corrected horizontal study for new enquiries. It follows retained road mapping and explicitly marked connecting sections. Um Al Tubol has an assumed operating chainage pending site selection. Iraq’s National Investment Commission gives the Airport line length and named areas in its investment announcement. The published route table gives neither a surveyed centreline nor observed hourly boardings. [Original investment announcement](https://investpromo.gov.iq/wp-content/uploads/2024/02/baghdad-metro-EN.pdf)

## Delivery plan

Run each calculation on the same physical revision. An evidence update can change an evaluation without changing its geometry. The release decision has two separate deliverables: a reproducible digital reference and a controlled first article. Assign design changes in the order below and repeat stages that consume their changed outputs.

| Task and owner | Inputs and work | Completion test and next evidence |
| --- | --- | --- |
| A01 • Integration | Register the route, demand, vehicle, power, civil and procurement inputs used in the decision. Record units, source, estimation basis, affected downstream work and validation route. | Reject a mismatched alignment, formation or price scope. Show measured, supplied, calculated and assumed inputs separately. Replace assumptions when the same candidate receives reviewed evidence. |
| A02 • GIS | Trace ordered centroid and road geometry. Mark connectors, missing stop sites and unresolved grade. Accept a source-identified replacement centreline. | Prove the length inequality on the original stop order. Recompute chainages on changed geometry. Obtain surveyed levels, curves, crossings, utilities, access and land before approving a corridor. |
| A03 • Service | Apply wait, in-vehicle time, access and transfers to the hourly origin–destination input. Preserve a fixed-demand control. | Compare 15, 20 and 30 minutes. Conserve riders, hold the station order fixed, and demonstrate candidate-bound count ingestion. Calibrate the responses using local observed counts and travel times. |
| A04 • Vehicle and operations | Use train mass, grade, actuation delay, adverse adhesion and available brake modules. Calculate attainable stops, residual independent force, heat and signalling distance. | Challenge the high load with a failed module. Obtain instrumented brake and wheel-slide duty, overlap and recovery evidence before accepting separation. |
| A05 • Vehicle and interfaces | Trace stock and installed allowances to assembly/BOM, centres and axle reactions. Screen end-of-life energy, loaded door widths and suspension travel. | Conserve weight and moment in each mass case. Record drawing conflicts and weigh the fitted article. Check actual spring, battery and door envelopes under governing loads. |
| A06 • Electrical and service | Use the revised chainages, the same OD matrices, assisted dwell, train mass and auxiliaries. Re-site both electrical architectures. Test a normal day, hot day, site outage, path outage and combined outage. | Report completed trips, attainable voltage, numerical residual, branch and source currents on the same service. Obtain scoped equipment ratings, return-circuit and protective isolation evidence for both. |
| A07 • Civil and erection | Move unequal central/high axle loads across the same girder and check the same footing. Price stock, haul, lifting, piers and bearings. Separate partial end bays. | Identify designs worth quoting at the actual lift radius. Record outstanding checks for prestress development, shear, fatigue, lifting stages, ground and bearings. |
| A08 • Production and procurement | Take actual family counts and operating fleet to the workshop. Trace stock to routing, fixtures, resources, inspection, rework and delivery schedules. | Re-run ordinary production and disruptions against the same order. Obtain matching subcontractor offers, measured cycles and first-article inspections. |
| A09 • Economics | Reconcile replacement civil quantities to displaced cost lots. Price the ordinary service and operations at the achieved fleet, energy and demand. Track missing offers and construction risks. | Show attributable estimates, price date and scope, without booking the same purchase twice. Keep unpriced exposure visible in capital and 30-year cash. Calibrate risks before assigning confidence levels. |
| A10 • Independent review and publication | Present the upstream constraint, model result, failed limit, commercial scope and next action for each decision. Rebuild and check the published handoff. | A reader can reproduce results, identify the physical and evaluation revisions, see failed options and find the specific return needed before fabrication or operation. |

Cost sensitivity is conditional on the chosen quantities and rates. The UK Infrastructure and Projects Authority describes separating base costs, uncertainty and risk. The US Federal Transit Administration checks scope, quantities, market conditions and schedule together. Both inform the estimate method here. [IPA cost guidance](https://www.gov.uk/government/publications/cost-estimating-guidance/cost-estimating-guidance) · [FTA cost estimation](https://www.transit.dot.gov/regulations-and-guidance/cost-estimation-fta-funded-transit-projects)

## Use the audit

For a costed desktop comparison, use the [GIS simulation](GIS-SIMULATION.md). Public elevation, soil texture and historical water layers feed its rail profile, support quantities, train and power replay, and purchaser cash model.

Run `./osr design railway audit` from the repository root. Use `--json` for stage identities, source references, assumption values, case results and unresolved evidence. Use `--help` for alternate inputs. The offline [decision results](AUDIT-RESULTS.md) show the default comparison. Each reference describes its own study scope. The production release remains held for physical and procurement evidence.

## Compare a fitted train on the same railway

The original Airport study allocates 700 places and a 65 kWh service battery to a six-car train. The battery falls short of its emergency energy duty at the assumed end of life. The [replacement battery input](battery-trial.json) sizes a 100 kWh trial and identifies its mass, mounting position and installed price. The [interior input](saloon-trial.json) allocates the usable floor to seats, wheelchair places, standing, doors and circulation. Both are planning inputs. A workshop can replace them with its own dimensions and documented equipment return. [Assumptions and mounting datums](vehicle-audit-guide.md)

Run the two inputs together to compare their operating, civil and purchasing consequences. From the repository root:

```sh
study=cities/Baghdad/engineering/simulation
./osr design railway audit --saloon-layout "$study/saloon-trial.json" \
  --battery-alternative "$study/battery-trial.json" --json > build/fitted-airport.json
./osr design railway audit --saloon-layout "$study/saloon-trial.json" \
  --battery-alternative "$study/battery-trial.json" --layout paired6 --packet build/fitted-enquiry.zip
```

Start with `service_offers` for trips completed and `decision.candidates` for failed and outstanding duties. The normal service boards up to the floor-plan capacity. The civil comparison also carries the high crowd load and adverse longitudinal distribution. The packet includes dimensioned floor allocations in DXF, their fleet quantities and the separately priced installed battery. The fleet price removes the original pack allowance once. Seat support, accessibility, suspension, braking and peak battery power still need tests on the fitted article.

| Fitted six-car trial | Result | Consequence for the enquiry |
| --- | --- | --- |
| Normal passenger layout | 20 fixed seats, two wheelchair places and four standing places per car. The train offers 156 places. | Price the fitted floor plan and return the installed furniture mass. |
| Loaded train mass | 158.136 t in the central 156-person case and 246.336 t with the 700-person adverse crowd and high equipment allowances. | Use the heavier axle distribution for the civil screen even when the ordinary service carries fewer people. |
| Emergency energy | The 100 kWh trial supplies 64 kWh after the usable-energy and ageing allowances. A further assumed 20% hot-weather loss leaves 51.2 kWh against 50.4 kWh required. | Obtain the hot discharge curve and brake-excitation duty. A further 0.8 kWh loss consumes the remaining energy margin. |
| Loss of one driven axle | Both layouts finish 72 of 72 trips in the fitted 30-minute replay. The required force reserve is deficient for 6,424 seconds of accumulated train duty on each layout. | Obtain the allowable degraded service and measured wheel-force data before selecting the drive. |

Add `--fault-controller-sensitivity` to the JSON command to repeat the axle fault with the reserve enforced by the controller. The fitted trial still completes 72 trips per layout and records 898 seconds per layout when the original traction request exceeds the controller limit. The trial does not establish an approved degraded timetable.

## Return prices against a revised design

Download the [six-site paired enquiry](audited-enquiry.zip) or the [30-site radial enquiry](audited-enquiry-radial30.zip) and open its README. Both use the same alignment, train, passenger offer, degraded duties and cash periods. Each has its own circuit, quantities and issue receipt. The radial enquiry includes the lost service under path isolation. Each package includes the alignment in GeoJSON, train and station loads, feeder duties, girder takeoff, workshop routing basis, quantities, cash periods and blank return files. The manifest binds the files to one physical candidate and evaluation. To verify a download, run `python3 -m cities.Baghdad.engineering.simulation.audit_packet path/to/enquiry.zip` in the checked-out edition. For a custom enquiry, record the issue ID printed by the original export in the buyer's register. Pass that value with `--issue-id` when verifying the returned file. The local SHA-256 check detects changed contents. Issuer identity and approval of the underlying drawings require separate evidence. The earlier [12 km drawing issue](../prototype/airport-enquiries.zip) is retained for prototype detail. Check each drawing against the revised interfaces before quoting it.

To reproduce the radial issue locally, run `./osr design railway audit --layout radial30 --packet build/radial30.zip`. Use the same command with revised service or survey inputs to issue a different scope. Supplier and equipment returns belong in the buyer-side JSON review. A failed operating case can be priced for comparison and remains visibly held in its packet.

Export the full comparison using `./osr design railway audit --json`. Each procurement lot in `production.<layout>.pricings` has a scope ID, physical unit, current quantity, currency and operating year. Send the same scope to each interested supplier and retain their own quotation documents and ERPNext Supplier Quotation references. To replay buyer-reviewed returns, pass `--offers buyer-offers.json --json`. The input uses schema `baghdad-airport-buyer-offers/1`. Each entry in `layouts` (e.g. `paired6`) has an `offers` list and an `awards` list. Each offer supplies its ID, supplier, scope ID, buyer review reference, document SHA-256, complete lot price in 2026 USD and optional claimed domestic value. Each award identifies the scope, offer ID and buyer award reference. The ledger keeps competing offers and their price differences. Only the explicitly chosen return enters the recalculated cash flow. A buyer or supplier declaration of local value still needs evidence of origin. [Worked buyer inputs and regression cases](test_audit_offers.py) · [Purchasing and factory guide](audit-production-guide.md)


## Test an engineering or owner assumption

For a stopping-distance sensitivity, use `./osr design railway audit --available-stop-m 350 --overlap-m 30`. This leaves 320 m from the front of the train for braking. The report compares it with the distance under delayed application, high mass and degraded braking. Substitute the surveyed approach limit and its required overlap when available.

For owner risk, use `--risk-return owner-risk.json --json`. The buyer file uses schema `baghdad-airport-owner-risk/1` and a `layouts` object keyed by `paired6` or `radial30`. Its dated lines identify the engineering scope, exclusions and how much of an exposure the historical contingency already covers. The ordinary ledger and the risk-adjusted cash are both available for review. [Return fields and worked cases](test_audit_production.py)
