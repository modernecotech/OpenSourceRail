# Kisumu civil soil screening

1,374 route/station sample locations; 1,374 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1374 |
| fine-soil-plasticity-and-shrink-swell-tests | 1374 |
| granular-density-and-groundwater-tests | 3 |
| silt-moisture-frost-and-erosion-review | 389 |

- No bearing capacity, CBR, friction angle, cohesion, groundwater, contamination, sulfate/chloride or deep stratigraphy is inferred from these maps.
- Desert, water, urban fill and other nodata remain unknown; no nearest-pixel or climate-based substitution.
- Texture fractions are independent predictions; they are not renormalised or converted to a geotechnical soil class.
- Prioritisation thresholds are editable OSR screening rules, not statutory limits or evidence of a hazard.
- No excavation depths, foundation dimensions, treatment quantities or civil costs are changed from pedological predictions.

Source: [OpenLandMap soilDB](https://github.com/openlandmap/soildb), Hengl et al., DOI 10.5194/essd-2025-336, CC BY 4.0. Exact source revision, URLs and raster metadata are retained in the receipt.

## Sampled property ranges

Ranges below span the sampled locations; they are not a city-wide characteristic soil value. The uncertainty envelope spans the lowest p16 to highest p84.

| Depth | Property | Unit | Mean range | Uncertainty envelope | Available locations |
|---|---|---|---:|---:|---:|
| 0..30cm | clay | % | 29–44 | 18–54 | 1374 |
| 0..30cm | sand | % | 23–46 | 8–65 | 1374 |
| 0..30cm | silt | % | 24–35 | 10–49 | 1374 |
| 0..30cm | bd.core | kg/m3 | 1100–1290 | 850–1490 | 1374 |
| 0..30cm | soc | g/kg | 8.8–19.9 | 4–36.4 | 1374 |
| 0..30cm | ph.h2o | pH | 5.6–6.1 | 5–7.1 | 1374 |
| 30..60cm | clay | % | 29–46 | 17–56 | 1374 |
| 30..60cm | sand | % | 22–44 | 6–70 | 1374 |
| 30..60cm | silt | % | 25–36 | 9–56 | 1374 |
| 30..60cm | bd.core | kg/m3 | 1130–1330 | 860–1620 | 1374 |
| 30..60cm | soc | g/kg | 4.8–11.7 | 2–24.6 | 1374 |
| 30..60cm | ph.h2o | pH | 5.6–6.1 | 5–6.9 | 1374 |
| 60..100cm | clay | % | 29–46 | 17–56 | 1374 |
| 60..100cm | sand | % | 22–43 | 6–70 | 1374 |
| 60..100cm | silt | % | 25–36 | 8–56 | 1374 |
| 60..100cm | bd.core | kg/m3 | 1160–1350 | 890–1660 | 1374 |
| 60..100cm | soc | g/kg | 4.1–10.2 | 1.5–30.4 | 1374 |
| 60..100cm | ph.h2o | pH | 5.6–6.2 | 5–7.4 | 1374 |
