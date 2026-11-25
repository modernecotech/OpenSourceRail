# Baghdad railway maps

The current metropolitan map shows one connected passenger network and the destinations used to test trips from housing areas. It marks populated areas beyond a 1,200 m walk. The GIS and line register use the same route lengths as the delivery estimate. [Map](baghdad-network.png) · [GIS](baghdad-network.geojson) · [Coverage results](../NETWORK.md) · [Delivery estimate](../NETWORK-DELIVERY.md)

The ring-and-grid study compares the published network with closed inner and outer rings, near-straight cross-city routes and an inner-ring-only option. [Comparison map](baghdad-ring-grid.png) · [Journey, construction and cost comparison](../RING-GRID.md)

## Retained map sources

The maps below record the original comparison geometry underlying earlier studies and estimates.

| Geographic review | Programme length | Station allowance | Map content |
| --- | ---: | ---: | --- |
| [Seven corridors](Baghdad-148km.png) · [Named-place review](corridor-review.geojson) | 148.2 km | 64 | Original February 2024 NIC satellite route plate |
| [Earlier central access study](baghdad-central-service.png) · [Central routes and stations GIS](central-service.geojson) | 28.21 km | 19 | Both lines end to end, including the Tigris crossing and Tahrir Square interchange |
| [Earlier citywide comparison](Baghdad-606km.png) · [Service and access GIS](central-access.geojson) | 605.652 km costed / 552.562 km timed | 280 budgeted | Passenger paths, deferred branches and reserved guideway |

## How to read the seven corridors

The Iraqi National Investment Commission published a satellite overview on page 3 and a corridor table on page 4. Its seven line lengths sum to 148.2 km. The total printed in the table is 148 km. The brief allows elevated, underground and at-grade sections. OpenSourceRail's cost case assumes elevated double track throughout and protected conductor rail. The authority's plate and a controlled centreline with chainage serve different purposes. [Original RFI and route plate](https://investpromo.gov.iq/wp-content/uploads/2024/03/3.-RFI-English-%D9%86%D8%A8%D8%B0%D8%A9-%D8%B9%D9%86-%D9%85%D8%AA%D8%B1%D9%88-%D8%A8%D8%BA%D8%AF%D8%A7%D8%AF-E-20.2.2024.pdf#page=3)

The comparison displays the full **890 × 632 pixel** satellite map from page 4 of the Commission’s Arabic investment notice, hosted by the Iraqi embassy in Paris. The route colours, bends, river crossings and airport approach come directly from the notice. The imagery and route plate are attributed to their original providers. For surveyed alignment, request the authority’s current centreline, station chainages and revision date. [Original notice and map](https://mofa.gov.iq/paris/wp-content/uploads/sites/55/2024/02/Baghdad-PDF.pdf#page=4)

To reproduce the published PNG, download that notice into a temporary directory as `Baghdad-PDF.pdf` and run the commands below there. Poppler extracts the original map as `plate-000.png` and the separate route table as `plate-001.png`. The Baghdad proposal renderer verifies the map dimensions and decoded RGB pixels before embedding it.

```sh
echo '167c27f381845e78bf3962af637548baf77715e0b5d2a9674f14192261592d2f  Baghdad-PDF.pdf' | sha256sum -c -
pdfimages -f 4 -l 4 -png Baghdad-PDF.pdf plate
```

### Locating the names in the brief

The geographic review uses the **Adhamiya quarter** label at 44.35945° E, 33.36935° N. The previous Red line used the much larger district centroid, about 6.9 km northeast, near Al Shaab. The same city background locates the Saydiyya and Mustansiriya quarters. All three coordinates represent neighbourhoods. Each revised point records its Arabic source label, previous coordinate and reason in the GIS file. The dashed strokes connect adjacent located names in the brief's sequence. Where a name is unresolved the line breaks. A crossing of two strokes supplies no evidence of an interchange. [Retained city background](../../catalogue/west-asia/Iraq/Baghdad/map-context.json.gz)

| Corridor | RFI km | Located / named occurrences | Names awaiting a location |
| --- | ---: | ---: | --- |
| Green | 19 | 6 / 8 | Al Allawi, Doura |
| Red | 27.7 | 5 / 8 | Al Allawi, Antar Sq., Qanat Al Jaish |
| Blue | 22 | 6 / 8 | Al Jamhouriya St., Uqba Bin Nafi Sq. |
| Purple | 14.5 | 5 / 7 | 83 Sq., Nadi Al Naft Int. |
| Yellow | 30 | 5 / 8 | Uqba Bin Nafi Sq., Al Hasanin Sq., Al Chadriya Sq. |
| White | 23 | 7 / 7 | All names in the retained waypoint sequence located |
| Airport | 12 | 5 / 6 | Um Al Tubol |
| **Total** | **148.2** | **39 / 52** | **13 unresolved occurrences** |

Counts follow the retained waypoint table. A shared place counts once for each line, repeated Al Amiriya entries within the RFI's White and Airport rows are collapsed and anonymous “Station” entries have no place identifier. The original station budget is 64. The 1 km circles around the airport terminal building, three Sadr City points and two Jadriya points measure straight-line proximity. River crossings, the street network and airport security determine the accessible walking route. Al Chadriya Sq. remains unresolved independently of the proposed Jadriya access points. [Waypoint table](rfi-waypoints.json) · [Airport terminal OSM feature](https://www.openstreetmap.org/way/28647537)

The cost and service model retains its original source-bound schematic. Its 138.395 km of straight strokes skips unresolved names. The 9.805 km difference from the programme allowance cannot locate missing track or specify a construction contingency. The public geographic review has no route-length takeoff. To advance an individual corridor, obtain the authority's alignment revision and coordinate reference system, confirm terminal and interchange entrances with their owners, and tie survey control, platform sites, river crossings and utility records to chainage before updating the quantities. [Retained model schematic](network-148km.geojson) · [Station budget and location screens](../station-register.json)

## Citywide concept

The [citywide map](Baghdad-606km.png) shows the timetable status of each section and marks the scheduled stops. Open the [walking-access comparison](baghdad-central-access.png) to see both cases in the central area. [Central access review](../CENTRAL-ACCESS.md)

The original 605.652 km drawing and geometry reproduce the earlier estimate. [Original map at the reviewed revision](https://github.com/modernecotech/OpenSourceRail/blob/f403916dc703521f845d4cc1761cf1b1e24f2c6c/cities/Baghdad/maps/Baghdad-606km.png) · [Source guideway geometry](network-606km.geojson)

The citywide model assigns the airport approach to M05, Sadr City approaches to M04 and M09, and Jadriya approaches to M01 and M02. The junction screen identifies gaps at both M04 approaches. The other approaches touch their drawn main lines within the map tolerance. Switches, stop locations, clearances and pier positions require design. This map draws 608.460 km across planning lines and connections against the 605.652 km cost control. [Junction screen](../system-results.json)

The independent citywide map uses the retained 24 October 2026 Protomaps background with OpenStreetMap and Natural Earth data. Rebuild the geographic review with `python3 cities/Baghdad/corridor_review.py`. The timetable uses the resulting GIS file to identify which named locations still require fieldwork. [OpenStreetMap attribution and licence](https://www.openstreetmap.org/copyright)

## Station sites and purchasing

The [station site and price comparison](STATION-PRICING.md) reconciles both independent budgets to the place and access records. It includes a return form for typical stations, interchanges, terminals, airport stations and constrained sites, with a separate row for each documented full-station offer.
