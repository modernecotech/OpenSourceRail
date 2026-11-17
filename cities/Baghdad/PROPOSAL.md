# OpenSourceRail Baghdad urban rail proposal

**For Amanat Baghdad | 17 November 2026 | Planning and engineering concept**

OpenSourceRail proposes an open, repairable urban railway with locally fabricated civil works, vehicle structures and replaceable equipment. Two connected networks are shown: a seven-line **148.2 km first programme** and a **605.65 km metropolitan concept** within a 500–800 km 2035 planning ambition. Their single planning capital estimates are **US$8.341bn** and **US$32.557bn** respectively; the latter includes the former. The proposal seeks a sponsored route, demand and engineering study.

## Network

| | First programme | Metropolitan concept |
|---|---|---|
| Scale | Seven named lines, 148.2 km in the [2024 government RFI](https://investpromo.gov.iq/wp-content/uploads/2024/03/3.-RFI-English-%D9%86%D8%A8%D8%B0%D8%A9-%D8%B9%D9%86-%D9%85%D8%AA%D8%B1%D9%88-%D8%A8%D8%BA%D8%AF%D8%A7%D8%AF-E-20.2.2024.pdf) | 605.65 km schematic network; 500–800 km long-term planning range |
| Route | [Named-place map](maps/network-148km.geojson) | [Schematic network map](maps/network-606km.geojson) |
| Airport | Require a landside stop linked to the passenger terminal entrance, with security and accessible access agreed with the airport | Require through-network terminal service |
| Sadr City | Blue/Purple service and three stop-area tests | Multiple through routes and transfer points across both districts |
| Jadriya | Yellow line and two university/medical catchment tests | Through service integrated with the metropolitan network |
| Short services | No standalone 6–8 km shuttles | Five short physical links are mapped as provisional connectors or branches, with no standalone shuttle service selected |

The first programme follows the RFI's Green 19 km, Red 27.7 km, Blue 22 km, Purple 14.5 km, Yellow 30 km, White 23 km and Airport 12 km corridors. The RFI also describes 64 stations, four depots and two control centres as planning inputs. Its distances and sites require feasibility work and owner approval. [RFI waypoints](maps/rfi-waypoints.json) retain unresolved named places without invented coordinates.

The metropolitan map combines the 513.3355 km source-declared research geometry, a 3.110 km straight-line airport-terminal extension and 89.206 km of six infill corridors. The **605.652 km** sum is a schematic screen, not a measured buildable alignment. Five short geometries total 34.3631 km within that sum. They are shown as physical connectors or branches to preserve their catchments; junction layouts and through/branch timetables remain to be designed. The six infill corridors test Sadr access, eastern and western cross-city travel and network connections. The airport marker is a terminal-area map centroid, not a selected entrance or station site. All station sites, crossings and interchanges need field verification.

## Service and railway

The [Baghdad planning train](VEHICLE.md) has six 17 m cars and approximately **700 places**, with wide accessible doors on both sides. A **150-second** interval offers **16,800 places/hour/direction per line** and 4.234 million scheduled places/day across seven lines and 18 hours before service losses and demand distribution. The [design and cost basis](COST-AND-DELIVERY.md) counts the larger fleet, doors, platform envelope, power and braking as a separate configuration. Measured origin–destination demand and dwell will set the final timetable.

The proposed architecture is wheel-supported trains with **powered bogies and overhead supply**, standard precast elevated spans and simple accessible stations. The [v0.7 vehicle](../../docs/reference-v07/vehicle/README.md) and [civil module](../../docs/reference-v07/civil/README.md) set the reference interfaces; Baghdad's 700-place variant has its own higher traction and braking equipment requests. Route-specific ground, river crossings, airport access and station sites determine the final civil quantities. Safety, accessibility, evacuation and independent stopping are required throughout.

## OpenSourceRail cost and delivery

The [single-estimate Baghdad ledger](COST-AND-DELIVERY.md) counts fourteen capital scopes, a 20% project allowance, fleet and 30-year operation and renewal on a declared civil and service basis. The 148.2 km first programme is **US$8.341bn installed** (**US$56.28m/km**) with **US$14.798bn** 30-year present cost. The complete 605.65 km metropolitan concept is **US$32.557bn installed** (**US$53.76m/km**) with **US$58.088bn** 30-year present cost. A five-year first programme targets 2031; parallel expansion to the full concept targets 2035. The physical mix is predominantly elevated and at grade with 8 km and 30 km of tunnel respectively.

These are OpenSourceRail quantity-and-rate planning estimates, including the 700-place train and site allowances. Surveyed routes, ground and utilities, station sites, supplier prices and financing terms establish the investment case. The [30 km reference budget](../../docs/reference-v07/cost/README.md) is a separate engineering control.

## Delivery and finance

1. **Sponsor and rights:** Amanat Baghdad and the National Investment Commission confirm the procuring authority, existing concession rights, airport access, land and data-sharing position.
2. **Measured network:** obtain origin–destination data, accessible walking surveys, utility/ground/flood records, Tigris crossing options and depot sites; select staged through routes and a 2035 delivery programme that can operate after each opening.
3. **Prototype and procurement:** specify one candidate-bound car, brake and power system, viaduct span and station module; seek Iraqi fabrication, equipment and construction quotes with tooling, inspection, spares and maintenance terms.
4. **Investment case:** reconcile the fourteen capital scopes, 30-year operating and renewal cash flows, local and imported content, land and environmental/social duties, funding sources and debt repayment support. An independent technical adviser reviews the same candidate.

[UKEF Buyer Credit](https://www.gov.uk/guidance/buyer-credit-facility) may support an eligible UK export contract through an acceptable bank and buyer; eligibility and terms are transaction specific. It does not finance the whole network by assumption. The [Iraqi Ministry of Planning's November 2026 workshop](https://mop.gov.iq/archives/40342) explicitly considered route changes and further feasibility study. The present decision sought from Amanat Baghdad is authority to develop and compare the two OpenSourceRail concepts on surveyed, capacity-matched and priced engineering.
