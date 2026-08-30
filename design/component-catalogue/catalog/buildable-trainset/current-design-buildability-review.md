# Current basic design buildability review

This review uses the generated design-system optimum and the current
rolling-stock CAD/BOM/fabrication package to identify what is already
buildable, what is only an envelope, and what must be closed before
first steel cut.

## Summary

| Status | Meaning |
|---|---|
| green | current design is good enough to carry into v2A build package |
| yellow | concept is sound but supplier/CAD/BOM alignment must be closed |
| red | missing build-release evidence or shop-drawing detail |

## Findings

| ID | Status | Scope | Finding | Action |
|---|---|---|---|---|
| `BDR-001` | `green` | architecture | The current design already uses repeated self-contained car modules with one powered and one trailer bogie per car. | Keep repeated-car architecture as the buildable baseline; it simplifies fixtures, spares, and training. |
| `BDR-002` | `green` | COTS/fabricated delineation | The procurement BOM now carries a controlled many-to-many crosswalk from all 100 commercial lines to LM3 product or assembly IDs; definitions and travelers carry the reverse references. | Keep the generated crosswalk mandatory as component kits are split and supplier routes are frozen. |
| `BDR-003` | `green` | candidate/CAD alignment | The promoted FreeCAD/product-tree baseline matches the optimizer target: 16.5 m cars, motor-350kw-hm47-class, battery-225kwh-lfp-800v, hvac-24kw-direct-hv-dc, and 12 PV modules per car. | Treat this as the v2A buildable seed: 250 kW continuous / 350 kW peak motors, 180 kWh usable / 225 kWh gross batteries per car, 24 kW/car HVAC, and supplier-freeze envelopes before drawings. |
| `BDR-004` | `yellow` | supplier freeze | Buildability still depends on supplier-frozen doors, HVAC, batteries, traction, wheelsets, brakes, couplers, and gangways. | Issue RFQ envelopes from the manifest, accept alternates only through fit/power/mass/evidence checks, then lock v2A supplier interfaces. |
| `BDR-005` | `yellow` | definition package / shop travelers / shop drawings | Every product-tree node now has a generated definition and signable shop-traveler template with structured material specs, process specs, labor, tooling, QA gates, revision approvals, and signoff blocks; controlled cut lists, weld maps, tolerance stacks, flat patterns, and harness/plumbing drawings are still v2A drawing-package work. | Use the generated material/process definitions and travelers as the drawing/RFQ/traveler index, then promote each MAKE/BID/SOURCE node into controlled LM3-BDY/BOG/HV/ELC drawings before first steel cut. |
| `BDR-006` | `yellow` | proof evidence | FEA screening exists and the previously coarse local bracket, coupler-pocket, battery-tray, door-portal, roof-equipment, and bogie-frame items now have generated definitions and assembly integration steps; local proof cases are still not complete. | Attach proof load cases to the generated component definitions and make FEM/static-test acceptance a release gate for each affected subassembly. |
| `BDR-007` | `yellow` | mass properties | The generated mass budget now reconciles the 75.308 t optimizer subtotal with the 78.75 t controlled planning tare through an explicit 3.442 t engineering reserve; drawing-level and as-built category closure remains open. | Replace estimates with supplier-frozen, CAD-derived, and weighed values while transferring consumed reserve to the affected category. |
| `BDR-008` | `yellow` | joint and fastener control | Every assembly integration step now carries machine-readable join classes and torque authority. Interior small parts have been rationalised into four fastener families and one common datum rail instead of treating every attachment as a bespoke structural joint; numerical values remain open until the applicable standard, supplier instruction, or load calculation is released. | Close the generated joint-control schedule by joint ID, qualify the common rail/fastener samples, and reference accepted values from interface drawings and shop travelers. |
| `BDR-009` | `green` | small components and serviceability | Door and glazing interfaces, passenger-fixture adapters, lighting cassettes, captive fasteners, seals, drain rails, keyed plugs, and emergency illumination are now explicit CAD/product-tree items rather than an opaque interior-kit allowance. | Keep the simplified interface families fixed while suppliers freeze detailed door, glass, luminaire, connector, and fastener parts; release safety-critical loads and tests through their stated gates. |

## Immediate build-package work

1. Treat the generated definition and shop-traveler packs as the
   product-tree index for parts, external components, subassemblies,
   assemblies, and trainsets.
2. Convert each `MAKE` definition into controlled drawings: cut list,
   flat pattern, weld class, datum scheme, tolerance, and inspection method.
3. Convert each `BID`/`SOURCE` definition into an RFQ envelope: mass, power,
   volume, mounting datum, service clearance, evidence pack, and alternate
   acceptance rule.
4. Close the generated mass-budget categories and joint-control rows as
   supplier, calculation, CAD, and weighing evidence becomes available.
5. Attach local proof cases to the structural subassemblies: underframe,
   bolsters, coupler pocket, door portals, battery tray, roof equipment,
   bogie frames, and articulation adapters.
6. Fill traveler approval/signoff blocks only during a real build; do not
   pre-sign generated templates.
7. Regenerate FreeCAD/FEM only after the promoted candidate parameters are
   reflected in the parametric source.
