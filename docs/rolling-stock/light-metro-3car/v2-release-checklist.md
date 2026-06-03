# Light-Metro 3-Car V2 Release Checklist

The v1 package is a complete concept envelope and procurement BOM.
The v2 package is the fabrication release. This checklist defines the
missing artifacts that must exist before the trainset can be treated
as production-ready.

| Gate | Required artifacts | Closure criterion |
|---|---|---|
| Supplier envelope freeze | Door, window, HVAC, articulation, coupler, battery, inverter, motor, brake, bearing, sensor, and charging connector interface drawings | Every selected supplier part fits without changing primary steel datums |
| Structural analysis | EN 15227 crashworthiness, EN 12663 carbody static/fatigue, EN 13749 bogie frame FEA | Reports reviewed and linked from `compliance.md` |
| Weld package | Weld maps, WPS/PQR register, weld classes, NDT plan, fixture-control plan | EN 15085 CL1/CL2 joints have inspection method and acceptance criteria |
| Manufacturing drawings | 2D controlled drawings for body, bogie, brackets, panels, battery trays, door portals, coupler pockets, HVAC rails, and nose cowl | Drawing register reaches rev A with owner, material, tolerance, and inspection method |
| Flat-pattern and NC output | DXF/neutral CAD flat patterns, bend tables, nesting sheets, drilling/cutting programs | Shop can cut and bend one carbody kit without interpreting 3D envelopes |
| Harness and pipe routing | Clamp locations, bend radii, connector access, HV segregation, coolant bleed/drain points, EMC bonding plan | Routing pack passes maintainability and electrical safety review |
| Weight and balance | Per-line mass rollup, axle loads by AW0/AW2/AW3, roof equipment CG, battery mass distribution | Tare target and <= 14 t AW3 axle load are verified |
| First-article inspection | Dimensional survey, water ingress, door fit, HVAC drain, battery isolation, brake/static tests | Results accepted into certification evidence register |

## COTS CAD Rule

Build123d and FreeCAD review models may stay supplier-neutral until procurement
freeze. After freeze, each selected supplier module gets a named
envelope model with revision, datasheet source, keep-out zones, and
service-removal path. Generic envelope models remain useful for early
design review but do not close v2.
