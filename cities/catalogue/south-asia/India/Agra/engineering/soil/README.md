# Agra civil soil screening

311 route/station sample locations; 309 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 82 |
| granular-density-and-groundwater-tests | 309 |

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
| 0..30cm | clay | % | 11–18 | 1–34 | 309 |
| 0..30cm | sand | % | 60–74 | 23–93 | 309 |
| 0..30cm | silt | % | 14–22 | 3–39 | 309 |
| 0..30cm | bd.core | kg/m3 | 1420–1540 | 1220–1690 | 309 |
| 0..30cm | soc | g/kg | 3.4–7.2 | 1.1–17.9 | 309 |
| 0..30cm | ph.h2o | pH | 7.2–7.7 | 6.1–8.8 | 309 |
| 30..60cm | clay | % | 12–20 | 2–39 | 309 |
| 30..60cm | sand | % | 55–72 | 16–92 | 309 |
| 30..60cm | silt | % | 15–25 | 2–43 | 309 |
| 30..60cm | bd.core | kg/m3 | 1450–1580 | 1190–1780 | 309 |
| 30..60cm | soc | g/kg | 2–3.4 | 0.3–9.5 | 309 |
| 30..60cm | ph.h2o | pH | 7.4–7.9 | 6.3–9.1 | 309 |
| 60..100cm | clay | % | 13–20 | 1–40 | 309 |
| 60..100cm | sand | % | 54–73 | 16–92 | 309 |
| 60..100cm | silt | % | 15–26 | 0–43 | 309 |
| 60..100cm | bd.core | kg/m3 | 1520–1610 | 1210–1840 | 309 |
| 60..100cm | soc | g/kg | 1.4–3.3 | 0.3–7.7 | 309 |
| 60..100cm | ph.h2o | pH | 7.6–8 | 6.4–8.9 | 309 |
