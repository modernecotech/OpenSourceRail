# Benguela civil soil screening

591 route/station sample locations; 486 complete profiles; 105 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 23 |
| coverage-gap | 105 |
| fine-soil-plasticity-and-shrink-swell-tests | 257 |
| granular-density-and-groundwater-tests | 486 |

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
| 0..30cm | clay | % | 16–24 | 1–38 | 486 |
| 0..30cm | sand | % | 55–70 | 22–94 | 486 |
| 0..30cm | silt | % | 13–24 | 0–44 | 486 |
| 0..30cm | bd.core | kg/m3 | 1280–1490 | 1030–1670 | 486 |
| 0..30cm | soc | g/kg | 2.3–9.2 | 0.6–26.5 | 486 |
| 0..30cm | ph.h2o | pH | 7–7.9 | 5.9–9.1 | 486 |
| 30..60cm | clay | % | 17–25 | 0–44 | 486 |
| 30..60cm | sand | % | 55–67 | 22–95 | 486 |
| 30..60cm | silt | % | 14–24 | 0–46 | 486 |
| 30..60cm | bd.core | kg/m3 | 1310–1530 | 1020–1750 | 486 |
| 30..60cm | soc | g/kg | 1.9–5.2 | 0.4–22.1 | 486 |
| 30..60cm | ph.h2o | pH | 7.1–7.9 | 5.2–9.3 | 486 |
| 60..100cm | clay | % | 17–27 | 1–46 | 486 |
| 60..100cm | sand | % | 54–67 | 19–97 | 486 |
| 60..100cm | silt | % | 14–24 | 0–45 | 486 |
| 60..100cm | bd.core | kg/m3 | 1320–1550 | 790–1890 | 486 |
| 60..100cm | soc | g/kg | 1.6–6.2 | 0.1–24.7 | 486 |
| 60..100cm | ph.h2o | pH | 7.2–8 | 5.2–9.4 | 486 |
