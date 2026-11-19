# v0.7 digital railway reference

This is the **single 30 km digital design and cost reference** for v0.7. The
[selected candidate](digital/selected.toml) combines the [vehicle mass and CAD
screen](digital/vehicle/README.md), [native 10 m beam analysis](digital/civil/README.md),
[production handoff](digital/production/README.md), [system arrangement](integration/arrangement.svg)
and [one cost and delivery ledger](cost/README.md). The vehicle and civil
studies retain their component ancestry. The selected beam has thirteen
prestress strands; its changed mass and price are counted in the active cost.

| Output | Planning result |
|---|---:|
| Service | Two tracks, twelve stations, 51 six-car trains including reserve; 8,280 offered normal places/hour/direction at the 120 s control headway |
| Train | Six 17 m cars, 276 normal places, 24 motorised axles, 1.5 kV DC overhead and independent rail-brake concept |
| Structure | Joint-free 10 m beam with thirteen strands, 6,000 beam placements and 6,002 support positions over the synthetic 30 km |
| Installed capital | **US$1.0252272bn** in 2026 dollars, **US$34.17m/route-km** |
| Whole-life present cost | **US$1.667647bn** for 30 years at 4% real |
| Delivery | **43 months** after an approved route and funding decision |

The 30 km case is a synthetic, fully elevated pricing control. Baghdad has a [separate 700-place train and costed network concept](../../cities/Baghdad/COST-AND-DELIVERY.md); it does not inherit the 276-place train's equipment rating, stations or route price. Samawah remains a separate city case. The v0.6 passive-wheel vehicle remains the historical selected reference and is not silently replaced by this planning configuration.

Use `./osr reference v07` to reproduce the reference quantities and costs;
`./osr reference v07 --stations 13` calculates a changed corridor with a new
physical and evaluation identity. The Workbench shows the same edit and links
the vehicle, civil, production and cost outputs. This package supports design
development and comparable supplier quotations. Fabrication and passenger
operation require later physical qualification.

## Inspect the core railway with an operator

In the workshop kit, open **Train and station models**, select **Core v0.7** and inspect a bogie, then the platform and viaduct. Both the viewer and IFC4 export show a 140 m station window with 28 running beams and 30 support positions. Use the corridor schedule for the full 6,000 placements. The selected beam’s thirteen strands affect mass, the lift plan and its unit price. [Twin guide and core IFC4](../operator-review/twins/README.md) · [Beam design and load cases](digital/civil/README.md)

| Review | What the core case provides | Evidence to obtain from a supplier or site |
|---|---|---|
| Train and station | Six 17 m cars per set, step-free boarding geometry and a 125 m platform allowance. The 51 sets include seven reserves. | A loaded door-threshold and boarding trial, the swept vehicle envelope and a timed turnback with recovery margin. [Vehicle and station interfaces](integration/README.md) |
| Bogies, brakes and power | Driven axles, overhead collection and a separate independent brake demand. The brake fixture links the reaction at the mounting pins to the rail fastening. | Weighed assemblies, brake force and delay on the stated grade, thermal recovery, isolation and an observed bogie exchange. [Brake reaction fixture](../../engineering/interface_studies/REFERENCE-RIGS.md) |
| Production and erection | The factory study allocates five assembly lines to 306 cars. Two casting yards and two erection fronts supply the viaduct. | Pilot cycle times, ready foundations, haul routes and storage. The proposed dates require at least 440 pre-erection beam places per yard. The example yard holds 180. [Vehicle works and precast yard drawings](../operator-review/delivery/README.md) |
| Operation and finance | The annual operations and maintenance allowance is $30.5m. At 50% borrowing over 20 years at 4% real, first full-year buyer cash reaches $68.2m before receipts. | Evidence for paid journeys, local pay, energy prices, debt terms and renewal budgets. Match quoted labour to the costs already included in the estimate. [Funding guide](../operator-review/finance/README.md) |

A change to the service or station count can change fleet, grid and platform quantities together. Give each bidder the same revised quantities, route assumptions and drawing revision. Record exceptions and price the first article before agreeing a series order. [Selected production handoff](digital/production/README.md) · [Core delivery workplan](../operator-review/WORKPLAN.md#building-the-core-railway)
