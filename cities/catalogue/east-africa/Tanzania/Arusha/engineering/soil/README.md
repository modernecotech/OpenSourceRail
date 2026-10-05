# Arusha civil soil screening

369 route/station sample locations; 369 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 369 |
| granular-density-and-groundwater-tests | 207 |

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
| 0..30cm | clay | % | 30–44 | 16–59 | 369 |
| 0..30cm | sand | % | 28–49 | 8–74 | 369 |
| 0..30cm | silt | % | 20–30 | 3–44 | 369 |
| 0..30cm | bd.core | kg/m3 | 1140–1360 | 970–1480 | 369 |
| 0..30cm | soc | g/kg | 6.9–20.3 | 3.9–40.2 | 369 |
| 0..30cm | ph.h2o | pH | 6.5–7.8 | 5.5–8.5 | 369 |
| 30..60cm | clay | % | 29–43 | 15–55 | 369 |
| 30..60cm | sand | % | 26–51 | 6–77 | 369 |
| 30..60cm | silt | % | 20–32 | 4–49 | 369 |
| 30..60cm | bd.core | kg/m3 | 1210–1380 | 990–1560 | 369 |
| 30..60cm | soc | g/kg | 5.4–9 | 2.6–16.4 | 369 |
| 30..60cm | ph.h2o | pH | 6.5–7.8 | 5.5–8.5 | 369 |
| 60..100cm | clay | % | 24–43 | 10–54 | 369 |
| 60..100cm | sand | % | 26–58 | 6–86 | 369 |
| 60..100cm | silt | % | 16–32 | 1–49 | 369 |
| 60..100cm | bd.core | kg/m3 | 1200–1390 | 960–1600 | 369 |
| 60..100cm | soc | g/kg | 4.1–6.3 | 1.7–13.1 | 369 |
| 60..100cm | ph.h2o | pH | 6.5–7.8 | 5.4–8.6 | 369 |
