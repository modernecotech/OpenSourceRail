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
