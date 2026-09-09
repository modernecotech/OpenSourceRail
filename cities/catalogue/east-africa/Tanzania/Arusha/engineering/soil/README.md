# Arusha civil soil screening

161 route/station sample locations; 161 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 161 |
| granular-density-and-groundwater-tests | 43 |

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
| 0..30cm | clay | % | 31–43 | 18–55 | 161 |
| 0..30cm | sand | % | 31–48 | 8–73 | 161 |
| 0..30cm | silt | % | 20–28 | 4–43 | 161 |
| 0..30cm | bd.core | kg/m3 | 1140–1380 | 970–1530 | 161 |
| 0..30cm | soc | g/kg | 5.5–20.3 | 3.2–39.5 | 161 |
| 0..30cm | ph.h2o | pH | 6.5–7.8 | 5.5–8.5 | 161 |
| 30..60cm | clay | % | 29–42 | 15–54 | 161 |
| 30..60cm | sand | % | 28–50 | 6–76 | 161 |
| 30..60cm | silt | % | 20–31 | 5–48 | 161 |
| 30..60cm | bd.core | kg/m3 | 1210–1390 | 1000–1560 | 161 |
| 30..60cm | soc | g/kg | 4.6–9 | 2.3–15.8 | 161 |
| 30..60cm | ph.h2o | pH | 6.5–7.7 | 5.6–8.5 | 161 |
| 60..100cm | clay | % | 24–41 | 10–54 | 161 |
| 60..100cm | sand | % | 29–58 | 6–84 | 161 |
| 60..100cm | silt | % | 18–31 | 2–48 | 161 |
| 60..100cm | bd.core | kg/m3 | 1210–1420 | 950–1610 | 161 |
| 60..100cm | soc | g/kg | 3.3–6.3 | 1.5–13.1 | 161 |
| 60..100cm | ph.h2o | pH | 6.5–7.7 | 5.5–8.5 | 161 |
