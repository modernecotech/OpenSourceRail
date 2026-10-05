# Bukavu civil soil screening

463 route/station sample locations; 452 complete profiles; 11 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 416 |
| coverage-gap | 11 |
| fine-soil-plasticity-and-shrink-swell-tests | 452 |
| granular-density-and-groundwater-tests | 179 |
| organic-content-and-compressibility-tests | 17 |

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
| 0..30cm | clay | % | 30–44 | 15–55 | 452 |
| 0..30cm | sand | % | 28–50 | 7–79 | 452 |
| 0..30cm | silt | % | 19–29 | 3–45 | 452 |
| 0..30cm | bd.core | kg/m3 | 1110–1300 | 780–1510 | 452 |
| 0..30cm | soc | g/kg | 9.1–24.3 | 4.1–55.9 | 452 |
| 0..30cm | ph.h2o | pH | 5.1–6.7 | 4.6–8 | 452 |
| 30..60cm | clay | % | 31–46 | 13–57 | 452 |
| 30..60cm | sand | % | 28–49 | 6–78 | 452 |
| 30..60cm | silt | % | 19–30 | 1–49 | 452 |
| 30..60cm | bd.core | kg/m3 | 1120–1360 | 770–1580 | 452 |
| 30..60cm | soc | g/kg | 6.2–14.8 | 1.8–35.9 | 452 |
| 30..60cm | ph.h2o | pH | 5.4–6.7 | 4.5–8 | 452 |
| 60..100cm | clay | % | 32–47 | 10–57 | 452 |
| 60..100cm | sand | % | 27–49 | 4–80 | 452 |
| 60..100cm | silt | % | 19–28 | 0–49 | 452 |
| 60..100cm | bd.core | kg/m3 | 1110–1370 | 670–1590 | 452 |
| 60..100cm | soc | g/kg | 4–13.6 | 1.1–82.4 | 452 |
| 60..100cm | ph.h2o | pH | 5.4–6.6 | 4.6–8.2 | 452 |
