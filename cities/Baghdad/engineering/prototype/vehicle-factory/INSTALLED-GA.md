# Airport representative car general arrangement

The nominee layout uses the first-article 17.0 × 2.70 m nominal body, the two powered bogie datums at x = ±6.40 m and the 1.00 m nominal floor above railhead. Four door centres per side sit at x = −6.30, −2.10, +2.10 and +6.30 m. The arrangement uses x forward, y left and z up from railhead, with the origin midway between the bogie centres. The plan and side elevation use the same scale. The elevation excludes brace and gusset projections for legibility. Their coordinates remain in the geometry register. [Scaled plan and elevation](installed-ga.svg)

The arrangement positions gross stock, axle planes, primary pad faces, paired secondary interfaces, eight steel door openings and sixteen nominal leaf sweeps. The remaining distances between adjacent sweeps define interior study intervals. The layout uses the outer two intervals to nominate two roof HVAC study points and puts the central service study point at x = 0. These points and intervals carry no equipment dimensions, usable floor width, mount rating or removal allowance. The arrangement therefore preserves the physical candidate and carries its own drafting evaluation identity. [Machine-readable geometry and source hashes](installed-ga.json)

## Control the critical interfaces

| Interface | Design datum and allocation | Measurement or design work still needed |
|---|---|---|
| Door aperture | The 1,360 mm steel opening allocates **25 mm inward per edge**. Per edge this is 8 mm liner, 8 mm projecting seal, 3 mm fabrication, 4 mm loaded movement and 2 mm fit/wear. The resulting 1,310 mm budgeted clear width leaves **10 mm** relative to the 1,300 mm requirement. Verify each opening using the sum of all applicable losses across both edges. | Release the jamb and lining detail with actual supplier stack. Survey at the floor, mid-height and header in installed, loaded and worn states. Retain the signed margin per opening. |
| Moving leaf | The 700 × 30 × 1,990 mm stock reservation travels 680 mm per leaf. The source nominal model has a minimum **21 mm** separation between the full leaf sweep and any stock bounding box. The adverse deviation, mounted equipment projection and required residual clearance together must fit within the corresponding actual separation. | Set a positive residual by supplier, hazard assessment and inspection method. Add guides, locks, stops, retention, anti-trap, wiring and seals. Sweep at loaded/twisted extremes and verify the governing obstruction. |
| Suspension faces | Primary pad faces sit at x = ±1.050 m and y = ±1.040 m relative to each bogie centre. Secondary faces sit at x = 0 and y = ±0.850 m. Their railhead heights are +0.602 and +0.758 m for a **156 mm nominal full stack**. Installed spring, isolator and shim height at the documented load and the fit tolerance must be compatible with each surveyed pair. Reserve the approved jounce, rebound and retention margins across the selected service load range. | Obtain the load-deflection and material data, seat fit and machining tolerances, retainer geometry and motion stops. Measure each paired face under tare and loaded conditions. |
| Straight boarding | Nominal straight body-to-platform gap **75 mm** and nominal floor/platform elevation **+1.000 m**. Budget actual horizontal and vertical gaps from threshold detail, track position, wheel wear, curve throw, suspension deflection/roll and installation position. | Establish approved gap and step limits for the boarding interface. Survey actual edges and fit, test loaded and worn cases, and review accessible boarding at all 24 door zones on the boarding side. |
| Bogie exchange | Bare frame travels **3.820 m** outward to provide 300 mm longitudinal standoff. The lane planning budget is **3.10 m**, including 2.50 m pallet and 300 mm each side. Revising the pallet or its equipment projection changes the required lane width. | Size the shop for the larger measured equipped sweep, including lift supports, tool access and lateral transfer. Verify approved lift loads, check dynamic load cases and witness both removal and restoration. |
| Structural loads and conditioned assemblies | Keep the **201.551 t** crowd-loaded train as a planning sensitivity and the **82.36 kN** equal static axle as its screening input. These values support interface sizing enquiries. | Resolve installed equipment masses and CG, then calculate tare, normal and crowd distributions and governing dynamic, braking, recovery, fatigue and accidental loads. Set approved proof, fatigue and dimensional limits for each mating/load interface. |

[First-article dimensions](../mechanical.md) · [Suspension and fitted sweep procedure](../fitout-guide.md) · [Platform datum](../civil-guide.md) · [Installed mass and axle evidence](../weight-guide.md)

Use the [body-to-bogie mating and joint inspection sheet](BODY-BOGIE.md) for the locating and seating datums, supplier hole-pattern return and signed fit measurements.

## Complete the installed boundary

Use the [grouped fitout BOM](installed-fitout-bom.csv) to identify stock, positioned interfaces, reserved sweeps, partial fits, study zones and unlocated groups. Quantities retain their source basis by car, train or opening. For example, the 24 conductor contact sets are a fleet quantity. Their allocation among cars remains open. Door-detail rows cover content inside the complete door assembly and must be counted once. The same applies to bogie-frame stock versus complete bogie and to service components inside larger supplier assemblies.

Require vendor geometry in the stated datum. Carry complete equipment, retaining and joining hardware, connectors, cabling, cooling, nominal and worst-case swept volumes, accessible zones, removal direction, lifting points, load application and mass/CG in the installed assembly register. Assign fitted locations and interfaces for saloon seating and wheelchair fittings, skins/glazing, gangways/couplers, rescue attachments, service power and batteries, collectors, brakes, wiring, HVAC, fire and emergency equipment. Approve mounting strength, service durability, fire and evacuation performance, gauge, running dynamics, measured axle loads and coupled power/thermal behaviour against the same installation. A supplier fit or altered physical drawing requires fresh candidate bindings across vehicle, civil, propulsion, service and cost before release.

## Verify the draft

From the repository root run:

```sh
python3 cities/Baghdad/engineering/prototype/vehicle-factory/installed_ga.py --check
```

The generator checks the source packet hashes and candidate, frame, mechanical and weighing bindings. It reproduces the JSON coordinates and artifact hashes, SVG and BOM using the standard library. The appendices retain missing installed mass and supplier evidence as open.
