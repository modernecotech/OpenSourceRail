# Baghdad mapping inputs and neighbourhood access

Source-selected planning evidence. Population counts remain native; no averaging across datasets or scaling to the catalogue total.

| Population source | Sector | Native population | Within 1 km of a station | Outside station circles |
|---|---|---:|---:|---:|
| worldpop-2026 | city | 8,597,980 | 57.0% | 3,699,347 |
| worldpop-2026 | northeast | 2,197,150 | 64.6% | 777,759 |
| worldpop-2026 | west | 1,459,449 | 53.8% | 674,777 |
| ghsl-2025 | city | 7,347,247 | 55.8% | 3,245,919 |
| ghsl-2025 | northeast | 1,159,005 | 54.0% | 532,859 |
| ghsl-2025 | west | 1,908,545 | 61.3% | 738,532 |
| worldpop-2020 | city | 5,985,974 | 49.0% | 3,051,695 |
| worldpop-2020 | northeast | 665,396 | 45.0% | 365,742 |
| worldpop-2020 | west | 1,673,741 | 43.2% | 950,787 |

Sector rectangles are explicit planning areas, not official neighbourhood boundaries. Station circles are radial screens, not surveyed walksheds.

The selected WorldPop 2026 epoch is an **alpha modelled projection**, not a current census. GHSL 2025 is a separate model comparison. Potential graph access within 1 km: **25.2%**, with 179/193 unique stations snapped within 150 m. Snaps, entrances, foot permissions, sidewalks and accessible paths remain unverified. Roads connect only through shared OSM node IDs; paths outside the retained bbox are unavailable.

Dated street extract: 2026-10-09; 308,905 pedestrian graph nodes, 362,348 edges; 53,174 mapped building ways. Incomplete building mapping never means an empty neighbourhood.

Measured traffic counts, speeds and origin–destination data are **unavailable**. Iraq is absent from current TomTom classic and Orbis Traffic API coverage tables. No measured traffic benefit or passenger demand is inferred.

[Selected sources, licences and sector policy](../../../../../../../design/network-planning/baghdad-mapping-sources.json) · [Machine-readable report and hashes](summary.json) · [Street geometry](walking-streets.geojson.gz) · [Research and integration policy](../../../../../../../docs/data/automatic-mapping-sources.md).
