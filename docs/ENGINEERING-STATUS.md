# Railway engineering status

## Baghdad decisions on main

| Area | Current digital result | Evidence needed to close the decision |
|---|---|---|
| Airport vehicle | Eight revised doorways leave 10 mm after the proposed fitted allowances. The 144 counted pieces total 5,272.7 kg per car including both bogie frames. | Installed group and axle weights, equipment geometry, loaded door clearance, brake and joint trials. |
| Airport power | The revised load leaves 0.57 V above the floor on the priced radial layout in the published hot case. Six paired-path sites clear the combined adverse screen with one site isolated. | Priced equipment, hot source and path measurements, protection and the response to combined site and branch loss. |
| Citywide service | Fourteen connected services on 552.562 km. A lower-frequency clockface schedule clears the modelled shared resources. Five access sections are deferred. | Surveyed junction/staging sites, directional demand, operator adoption and funding. |
| Prototype delivery | Car, bogie, beam, pier and platform models can be inspected offline. The quotation packet includes return forms, work orders, installation and inspection instructions. | Supplier drawings, independently reviewed limits, contracted local capacity, qualified articles and owner approval. |

[Airport decision register, digital twins and quotations](../cities/Baghdad/engineering/prototype/README.md) · [Citywide service and financial scope](../cities/Baghdad/CITYWIDE-SERVICE.md)

## Synthetic 30 km reference

The [selected digital railway](reference-v07/digital/selected.toml) is a powered-wheel, two-track synthetic 30 km corridor with twelve stations. It uses one six-car vehicle family, a thirteen-strand 10 m precast beam and protected 1.5 kV DC overhead. The [release gate](RELEASE-v0.7.md) concerns the digital design, cost and production plan. Physical manufacture and passenger operation require later qualification.

| Design result | Selected digital basis |
|---|---|
| Service | 276 normal places per six-car train; 120 s peak comparison headway; 44 active plus seven reserve sets; 8,280 offered places/hour/direction. |
| Vehicle | [CAD and mass screen](reference-v07/digital/vehicle/README.md) places 2,482 inherited geometry occurrences and ten powered items, counts the remaining mass, and retains 25.072 t/car normal and 33.622 t/car crowd sizing loads. Full equipment placement and dynamic axle loads require design development. |
| Propulsion | Twenty-four continuously powered axles, six drive groups and a 72 km/h cap. The 2.727 km, +2% sizing leg requests 102.23 kN and at least 3.037 MW train DC input. Station-only launch does not satisfy the tested uphill cases. |
| Braking | Twelve independent rail-contact modules per train. With one unavailable, each of the eleven working modules must deliver 10.89 kN and absorb 3.63 MJ ideal rail-interface energy under the stated normal-load downgrade case. Protected supply, hot duty, parking and rescue are qualification requirements. |
| Civil | The [joined native beam check](reference-v07/digital/civil/README.md) carries the bounded car CG into a 1.107 MNm crowd moving-load case. The selected thirteen-strand child gives 1.576 mm gross-elastic midspan deflection and passes its declared longitudinal screen. One beam per track per 10 m bay yields 6,000 beams and 6,002 supports. The foundation cost module assumes ordinary ground; no actual alignment or soil is claimed. |
| Station | 125 m × 8 m central island, two one-sided doors per car facing the platform, independent platform structure, accessible vertical access and protected egress. Static 75 mm body-to-edge arithmetic is not a dynamic boarding-gap approval. |
| Control electronics | [Equipment schedule](../control-electronics/README.md) counts protection, radio, car, door, brake, station, grid, line-section and control-room equipment for the 30 km candidate and separately for Baghdad. Each allocation sits within its existing capital scope. The door evaluator requires verified station identity and matching platform side for normal release. |
| Production | The [digital handoff](reference-v07/digital/production/README.md) connects 52 BOM rows, 23 route steps, make/buy assumptions, 14 capital scopes and an ERPNext-shaped dry run. Native orders, receipts and repair records require real site masters, supplier and inspection records. |
| Cost and time | [One 2026 USD estimate](reference-v07/cost/README.md): US$1,025.2272m installed capital, US$1,667.647m 30-year present cost and a 43-month construction programme after route approval. The straight 2 km construction module has a twelve-month planning allowance. |

The [v0.6 passive-wheel vehicle](../engineering/development-baseline.toml) remains its own selected development reference. The synthetic corridor, [Samawah](../cities/catalogue/west-asia/Iraq/Samawah/README.md) and [Baghdad](../cities/Baghdad/PROPOSAL.md) are separate applications. Baghdad uses a 700-place planning train and its own [cost and delivery basis](../cities/Baghdad/COST-AND-DELIVERY.md).

The [Baghdad Airport planning selection](../cities/Baghdad/airport-integration.html) joins the timetable, radial supply, six-set fleet, component quantities and funding schedule. Its selection record distinguishes numerical results, engineering screens and procurement authority. The 15-minute timetable includes every passenger working, two empty journeys and the depot lead. The 30-site supply model clears the 1.35 kV planning floor by 0.925 V in its most demanding sensitivity. Obtain a priced six-site lower-resistance offer and measure source, conductor and train performance before deciding how to supply the route.

For the prototype, resolve the zero nominal allowance between the 1.300 m steel door aperture and the required fitted opening, then measure the fitted door under load. The dossier keeps first-article inspection, independent braking, geotechnical investigation, supplier prices and witnessed station-visit tests open. The four unresolved metropolitan groups retain their separate service allowances. [Prototype and delivery roadmap](ROADMAP.md)
