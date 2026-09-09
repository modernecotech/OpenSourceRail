# Cuenca civil soil screening

297 route/station sample locations; 297 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 13 |
| fine-soil-plasticity-and-shrink-swell-tests | 297 |
| granular-density-and-groundwater-tests | 164 |
| organic-content-and-compressibility-tests | 2 |

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
| 0..30cm | clay | % | 24–39 | 11–48 | 297 |
| 0..30cm | sand | % | 29–56 | 10–82 | 297 |
| 0..30cm | silt | % | 19–33 | 6–44 | 297 |
| 0..30cm | bd.core | kg/m3 | 1060–1370 | 900–1600 | 297 |
| 0..30cm | soc | g/kg | 6.2–32.3 | 2.1–52.9 | 297 |
| 0..30cm | ph.h2o | pH | 5.7–7.5 | 5.1–8.2 | 297 |
| 30..60cm | clay | % | 25–41 | 11–52 | 297 |
| 30..60cm | sand | % | 29–55 | 11–82 | 297 |
| 30..60cm | silt | % | 20–32 | 5–43 | 297 |
| 30..60cm | bd.core | kg/m3 | 1120–1390 | 850–1610 | 297 |
| 30..60cm | soc | g/kg | 5.3–25.9 | 1.4–46 | 297 |
| 30..60cm | ph.h2o | pH | 5.7–7.6 | 5.1–8.2 | 297 |
| 60..100cm | clay | % | 25–41 | 12–52 | 297 |
| 60..100cm | sand | % | 28–55 | 13–82 | 297 |
| 60..100cm | silt | % | 20–32 | 4–44 | 297 |
| 60..100cm | bd.core | kg/m3 | 1150–1460 | 700–1680 | 297 |
| 60..100cm | soc | g/kg | 3.5–26.3 | 0.7–64 | 297 |
| 60..100cm | ph.h2o | pH | 5.7–7.6 | 5–8.3 | 297 |
