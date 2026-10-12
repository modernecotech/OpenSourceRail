# Baghdad mapping inputs and neighbourhood access

Source-selected planning evidence. Population counts remain native; no averaging across datasets or scaling to the catalogue total.

| Population source | Sector | Native population | Within 1 km of a station | Outside station circles |
|---|---|---:|---:|---:|
| worldpop-2026 | city | 8,597,980 | 30.0% | 6,014,797 |
| worldpop-2026 | northeast | 2,197,150 | 38.4% | 1,353,322 |
| worldpop-2026 | west | 1,459,449 | 29.6% | 1,027,430 |
| ghsl-2025 | city | 7,347,247 | 30.7% | 5,090,413 |
| ghsl-2025 | northeast | 1,159,005 | 35.6% | 745,888 |
| ghsl-2025 | west | 1,908,545 | 33.2% | 1,274,202 |
| worldpop-2020 | city | 5,985,974 | 27.7% | 4,325,387 |
| worldpop-2020 | northeast | 665,396 | 35.3% | 430,612 |
| worldpop-2020 | west | 1,673,741 | 25.1% | 1,252,936 |

Sector rectangles are explicit planning areas, not official neighbourhood boundaries. Station circles are radial screens, not surveyed walksheds.

The selected WorldPop 2026 epoch is an **alpha modelled projection**, not a current census. GHSL 2025 is a separate model comparison. Potential graph access within 1 km: **11.5%**, with 105/116 unique stations snapped within 150 m. Snaps, entrances, foot permissions, sidewalks and accessible paths remain unverified. Roads connect only through shared OSM node IDs; paths outside the retained bbox are unavailable.

Dated street extract: 2026-10-09; 308,905 pedestrian graph nodes, 362,348 edges; 53,174 mapped building ways. Incomplete building mapping never means an empty neighbourhood.

Measured traffic counts, speeds and origin–destination data are **unavailable**. Iraq is absent from current TomTom classic and Orbis Traffic API coverage tables. No measured traffic benefit or passenger demand is inferred.

[Selected sources, licences and sector policy](../../../../../../../design/network-planning/baghdad-mapping-sources.json) · [Machine-readable report and hashes](summary.json) · [Street geometry](walking-streets.geojson.gz) · [Research and integration policy](../../../../../../../docs/data/automatic-mapping-sources.md).
