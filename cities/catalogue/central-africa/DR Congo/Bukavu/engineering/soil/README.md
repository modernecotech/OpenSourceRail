# Bukavu civil soil screening

289 route/station sample locations; 278 complete profiles; 11 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 277 |
| coverage-gap | 11 |
| fine-soil-plasticity-and-shrink-swell-tests | 278 |
| granular-density-and-groundwater-tests | 181 |
| organic-content-and-compressibility-tests | 6 |

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
| 0..30cm | clay | % | 30–43 | 16–55 | 278 |
| 0..30cm | sand | % | 28–50 | 6–79 | 278 |
| 0..30cm | silt | % | 19–31 | 4–48 | 278 |
| 0..30cm | bd.core | kg/m3 | 1090–1300 | 750–1540 | 278 |
| 0..30cm | soc | g/kg | 9.5–25.6 | 4.4–71.1 | 278 |
| 0..30cm | ph.h2o | pH | 5.1–6.7 | 4.7–8 | 278 |
| 30..60cm | clay | % | 31–44 | 15–57 | 278 |
| 30..60cm | sand | % | 26–48 | 9–81 | 278 |
| 30..60cm | silt | % | 19–32 | 0–49 | 278 |
| 30..60cm | bd.core | kg/m3 | 1150–1360 | 770–1590 | 278 |
| 30..60cm | soc | g/kg | 6.6–13.1 | 1.9–36.7 | 278 |
| 30..60cm | ph.h2o | pH | 5.4–6.6 | 4.8–8 | 278 |
| 60..100cm | clay | % | 32–44 | 16–57 | 278 |
| 60..100cm | sand | % | 27–48 | 6–79 | 278 |
| 60..100cm | silt | % | 19–31 | 0–48 | 278 |
| 60..100cm | bd.core | kg/m3 | 1120–1350 | 770–1610 | 278 |
| 60..100cm | soc | g/kg | 5.5–14.3 | 1.1–66.8 | 278 |
| 60..100cm | ph.h2o | pH | 5.5–6.7 | 4.6–8.2 | 278 |
