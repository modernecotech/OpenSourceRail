# LM3 controlled mass budget

Generated from the promoted design candidate and baseline constants. This
record resolves the earlier ambiguity between the optimizer subtotal and the
planning tare; it is not a substitute for drawing-level or as-built weighing.

- Candidate: `light-metro-3car__16p5m__reference-body__reference-bogie__motor-350kw-hm47-class__battery-225kwh-lfp-800v__hvac-24kw-direct-hv-dc__pv12`
- Document revision: `A-DRAFT`
- Release status: `planning-control`

| Category | Modeled mass (kg) |
|---|---:|
| carbody primary structure | 25,623.53 |
| bogie frames, wheelsets, brakes, and suspension | 20,190.00 |
| traction motors, gearboxes, and controllers | 3,360.00 |
| traction batteries | 4,350.00 |
| roof HVAC | 1,530.00 |
| roof PV | 864.00 |
| doors, glazing, interior, and auxiliaries | 16,350.00 |
| end cowls and interfaces | 1,240.00 |
| inter-car articulation | 1,800.00 |
| **Modeled subtotal** | **75,308** |
| Engineering reserve (4.57 %) | 3,442 |
| **Controlled planning tare** | **78,750** |

## Closure rule

Replace category estimates with weighed, supplier-frozen, or CAD-derived masses; transfer consumed reserve to the affected category; do not reduce controlled tare until the signed trainset weigh establishes the as-built value.

The reserve currently covers unclosed wiring, fluids, fasteners, coatings,
production tolerances, and supplier mass growth. Every released drawing or
supplier selection must update its category without hiding growth in another
line. Final closure requires individual car weights and a complete trainset
weight recorded by serial number.
