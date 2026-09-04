# Light-Metro 3-Car V2 Release Checklist

The v1 package is a complete concept envelope and procurement BOM.
The v2 package is the fabrication release. This checklist defines the
missing artifacts that must exist before the trainset can be treated
as production-ready.

| Gate | Required artifacts | Closure criterion |
|---|---|---|
| Design baseline freeze | Signed LM3 configuration sheet covering 3 repeated 16.5 m cars, 3 powered bogies, 3 trailer bogies, 540 kWh usable onboard battery, 78.75 t controlled planning tare (75.308 t modeled subtotal + 3.442 t engineering reserve), two door pairs per side per car, and no city-specific train variant | Drawing register, mass budget, product mass-closure ledger, BOM, RFC 0008, RFC 0021, RFC 0022, and `trainset.py` all agree |
| Supplier envelope freeze | Door, window, HVAC, articulation, coupler, battery, inverter, motor, brake, bearing, sensor, and charging connector interface drawings | Every selected supplier part fits without changing primary steel datums |
| Structural analysis | EN 15227 crashworthiness, EN 12663 carbody static/fatigue, EN 13749 bogie frame FEA, plus closure of the current lateral-sway screen review | Reports reviewed and linked from `compliance.md`; revised body model is <= 20 mm lateral displacement or has an approved target change |
| Weld package | Weld maps, WPS/PQR register, weld classes, NDT plan, fixture-control plan | EN 15085 CL1/CL2 joints have inspection method and acceptance criteria |
| Bogie frame and recovered-component acceptance | Fresh powered/trailer bogie-frame drawings, supplier certificates for new safety-critical parts, and any donor axle/axlebox quarantine + NDT + metrology sheets | No recovered freight bogie frame enters the OSR consist; recovered components are accepted only line-by-line |
| Manufacturing drawings | 2D controlled drawings for body, bogie, brackets, panels, battery trays, door portals, coupler pockets, HVAC rails, and identical fiberglass end-cowl casts | Drawing register reaches rev A with owner, material, tolerance, and inspection method |
| Factory drawing/interface packages | Sixteen generated work packages covering every locally made row across chassis, structural interfaces, exterior modules, panoramic glass, lamps, configurable ends, bogies, battery/HV hardware, trainlines, roof equipment, interiors, fixture rails, livery film, trial roof coating and recovery | Every package has frozen inputs, approved controlled outputs, characteristic list, verification owner and evidence route; the generated package itself is not an approval |
| Flat-pattern and NC output | DXF/neutral CAD flat patterns, bend tables, nesting sheets, drilling/cutting programs | Shop can cut and bend one carbody kit without interpreting 3D envelopes |
| Harness and pipe routing | Clamp locations, bend radii, connector access, HV segregation, coolant bleed/drain points, EMC bonding plan | Routing pack passes maintainability and electrical safety review |
| Weight and balance | Close all 117 active rows in generated `mass-closure-ledger.md`; per-line mass rollup, individual-car and complete-train calibrated weighs, axle loads by AW0/AW2/AW3, roof equipment CG, battery mass distribution | Nine categories reconcile, the signed tare/CG report supports the controlled mass, and <= 14 t AW3 axle load is verified; the 73.376 t modeled lightweight candidate cannot change tare before its separate substantiation gates close |
| First-car build hold point | One 16.5 m carbody shell, one powered bogie, one trailer bogie, one battery enclosure set, one door bay, and one roof/HVAC/PV bay built and inspected before committing all three cars | Dimensional/NDT findings are closed or fed back into rev B tooling before repeat production |
| First-article inspection | Dimensional survey, water ingress, door fit, HVAC drain, battery isolation, brake/static tests | Results accepted into certification evidence register |

## COTS CAD Rule

Parametric CAD and FreeCAD review models may stay supplier-neutral until procurement
freeze. After freeze, each selected supplier module gets a named
envelope model with revision, datasheet source, keep-out zones, and
service-removal path. Generic envelope models remain useful for early
design review but do not close v2.
