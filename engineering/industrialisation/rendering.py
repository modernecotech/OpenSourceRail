"""Publication rendering isolated from the industrialisation calculations."""


def readme(vendors, supplier_lines):
    return f'''# Coordinated industrialisation programme

**Status: proposed programme; products, rights, commercial terms and physical acceptance remain open.** Vehicle platform, bogie localisation and the viaduct system share one configuration and evidence chain. HÜBNER and CRRC are proposed discussion partners; no exact product or manufacturing-transfer agreement is selected. [Controlled programme](../../design/industrialisation/programme.json).

## Vehicle configuration and civil demand

[Vehicle-to-civil trace](vehicle-civil-load-trace.json) preserves the current three-car, six-bogie/twelve-axle reference. Its 78,750 kg tare is an unclosed planning control. Equal car loading, midpoint CG and equal bogie axle sharing are explicitly assumed. Bogie locations follow the existing CAD rule. The shared-bogie alternative has an explicit four-support graph with unknown redesign masses. Buying an articulation creates no bogie-count, mass, energy or cost reduction. Exact joint/bogie selection, low-floor clearances, yaw/pitch/roll, stiffness/damping, fatigue/crash and maintenance/recovery require a joint interface freeze.

The same axle pattern feeds sampled static Pi20/Pi25 live-load demand. Dynamic augmentation, permanent capacity, prestress, bearings and launcher loads need independent design. [Identified Baghdad spans](../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/connected-build/span-layout.json) remain the quantity authority. No vehicle/civil loading baseline is overwritten.

## Bogie localisation and first articles

First article → repeat assembly with qualified bought-in subcomponents → released frame cutting/forming/welding/machining/NDT/coating → further component localisation where economics justify qualification. Initially buy precision articulation assemblies and make approved surrounding adapters locally. Assess existing Iraqi fabrication and machining processes. Prioritise fixtures, metrology, weld quality, inspection and test equipment. Transfer rights, fees, tooling, qualification, imported components, labour, rejects, warranty and repeat prices have separate scopes.

## Civil catalogue and urban delivery

Two single-track full-span beams share a pier: 25 m primary, 20 m secondary, and separately engineered exceptional crossings. Standardise column/cap connections, bearing/jacking/lifting seats, direct-fixation datums, removable walkway/service cassettes and island-station transitions. Ground zones, depth, capacity, utility clearances and working platforms remain site-specific.

[Support packets and urban controls](support-release-and-urban-access.json) keep foundation mobilisation and launcher support acceptance distinct. Compare precast columns/caps with reusable-form in-situ columns/precast caps by measured accepted supports/week and complete installed cost. Require inspectable connections, temporary stability, grout and verified release strength. Maintain shop/pedestrian/emergency access, appointment-based deliveries/spoil, booked lifting exclusions and prompt reinstatement. Lane-hours, access interruptions and occupation days are unioned by resource and bound to accepted completed bays; absent observations stay unknown.

## Production chain and 18-launcher scenario

[Production balance](production-balance.json) treats one accepted double-track bay as the planning unit. Eighteen active independent fronts at 1/1.5/2 bays per working day give 18/27/36 bays, 36/54/72 beams and 450/675/900 m under the illustrative all-25 m assumption. Actual 20/25 m mixes and special spans retain identified quantities. At 54 beams/day, 48-hour occupation needs 108 casting positions before availability/reject allowances; a long-line bed can hold several positions. A five-working-day buffer needs 270 beams. None is a production commitment.

Released foundations → accepted piers → accepted serialized beams → transport → erection → completed-bay acceptance limit output together. Casting alone cannot release a bay. Mobilise only against a sufficiently long released run, qualified supply, access, authorised crew and compatible inspected machinery. Coordinate existing Iraqi precast facilities and expertise; allocate qualified products/slots and add only demonstrated necessary tooling/capacity.

## Work, training, programme gates and finance

[Linked work packages and ERP handoffs](work-packages-and-erp-handoffs.json) connect the existing supplier, civil and execution structures. The first 30 and 30–90 day windows are proposed planning targets, followed by accepted pilot trials, controlled ramp-up and up-to-18-machine deployment. Responsible roles are named; appointments, funded recruitment and dated rosters remain open. Training attendance is separate from assessed equipment-specific work authority. Future reviewed reservations must undergo the same live machinery/worker exclusivity checks.

[Installed costs and delivered-service finance](installed-cost-and-service-finance.json) separates priced scopes and missing amounts. The [Baghdad delivery/finance bridge](baghdad-delivery-finance-bridge.json) joins each line's conditional running-span date, retained finance opening month/fleet deadline, controlled required fleet and energy/service diagnostics. A common financial-close anchor, supplier vehicle deliveries and accepted station/special/system handovers are still missing. Dispatch completion does not automatically scale paid journeys. Running-bay completion is not railway revenue opening. Unique paid journeys/collection and operating acceptance are required before revised receipts can be considered. Transfers do not multiply paid journeys. [Further elevation comparisons](further-elevation-comparison.json) expose marginal civil reference allowances for explicit scope sensitivities, with complete installed costs, disruption values, financing and net benefit unknown. No additional alignment, beam order, price or accelerated saving is adopted.

## Possible component and equipment vendors

{vendors['method']} Related group brands are not independent offers. Product-family listings establish neither OSR fit nor regional availability, rights, prices, capacity or acceptance. Gangways are not automatically structural joints; segmental gantries are not whole-beam launchers. [Machine-readable candidates](vendor-candidates.json) · [RFQ comparison CSV](vendor-candidates.csv).

| Possible vendor | Scope | Official product/reference source |
|---|---|---|
{supplier_lines}

## Regeneration

Run `.venv/bin/python tools/automation/industrialisation-study.py`; add `--check` for source/output drift. [Manifest](manifest.json) records exact inputs and output bytes. Missing supplier or engineering evidence never becomes acceptance.
'''.encode()
