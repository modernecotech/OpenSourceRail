# Baghdad station sites and prices

The seven-corridor and citywide options each carry an installed allowance for accessible stations. Compare offers against each network independently. A plotted place or entrance can support a site investigation. The budget carries one allowance per physical station.

| Independent option | Budgeted stations | Point records | Budget less point count¹ | Unique map coordinates | Approved station sites | Direct station budget |
|---|---:|---:|---:|---:|---:|---:|
| Seven corridors | 64 | 37 | 27 | 27 | 0 | $832m |
| Citywide | 280 | 220 | 60 | 177 | 0 | $3,640m |

¹ Subtraction shows the gap only if each mapped point eventually becomes one station. All budget slots currently have a generic price and unresolved site/class allocation. A surveyed station may have several entrances or serve several lines.

The seven-corridor register’s 37 occurrences identify 27 source groups when both the map object and coordinates match. The separate corridor review locates 39 named occurrences and records 13 unresolved occurrences. It also proposes 5 population-access anchors. These layers describe overlapping evidence. Their counts must be kept separate. In the citywide map, 43 coordinates occur more than once. Preserve every route and point ID until a surveyed transfer layout establishes whether they serve one station.

## Survey and purchasing return

Give each approved physical station one site reference and one generic allowance slot. Record all linked mapped point IDs, access routes, wheelchair approach, vertical circulation, platform width, emergency egress and interchange paths. A separately surveyed location can cite its own evidence and leave the point list empty. Consult landowners and the operator, and obtain a priced scope against the surveyed footprint.

| Station class | Scope for comparison |
|---|---|
| `typical_elevated` | Through station with street access to a straight platform |
| `interchange` | Transfer between routes with passenger circulation and step-free connections |
| `terminal` | Passenger terminus with reversal and stabling interfaces |
| `airport` | Passenger terminal with airport circulation, security and access interfaces |
| `constrained` | Station with a crossing, unusual ground, restricted footprint or difficult access |

Each matched full station displaces one $13m direct allowance. A return must include the survey and chainage, approved station identity, step-free access and egress, platform/structure/equipment scope, boundary reconciliation and a priced offer. Identify station controllers already included in the station price. Keep separately priced viaduct, line systems, land, utilities and train movements outside the matched scope unless the buyer documents an equivalent transfer. Record a shared interchange once, including all entrances and transfer passages in its agreed scope. Partial entrance or lift offers can inform design while the station keeps its full generic allowance.

From the repository root, use the following commands. The inventory exports the individual location records, source groups, unresolved names and unallocated budget slots. The blank form makes no price substitutions. Add one station row per documented full-scope offer.

```sh
python3 cities/Baghdad/maps/station_pricing.py --inventory > build/baghdad-station-inventory.json
python3 cities/Baghdad/maps/station_pricing.py --network first --template > build/station-return.json
python3 cities/Baghdad/maps/station_pricing.py --row
python3 cities/Baghdad/maps/station_pricing.py --network first --return-file build/station-return.json
```

Use `--network metropolitan` for the citywide option. Each result reports class totals, the replaced and retained direct allowances, and the change in station scope. A buyer must verify the supplied references and cost boundaries before accepting a return. [Station register](../station-register.json) · [Corridor review](corridor-review.geojson) · [City cost ledger](../COST-AND-DELIVERY.md)
