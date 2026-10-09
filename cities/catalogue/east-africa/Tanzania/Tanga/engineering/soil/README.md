# Tanga civil soil screening

560 route/station sample locations; 560 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 443 |
| fine-soil-plasticity-and-shrink-swell-tests | 327 |
| granular-density-and-groundwater-tests | 560 |
| organic-content-and-compressibility-tests | 12 |

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
| 0..30cm | clay | % | 10–30 | 3–48 | 560 |
| 0..30cm | sand | % | 45–81 | 13–92 | 560 |
| 0..30cm | silt | % | 8–25 | 0–44 | 560 |
| 0..30cm | bd.core | kg/m3 | 610–1470 | 440–1660 | 560 |
| 0..30cm | soc | g/kg | 6.3–56 | 1.1–94 | 560 |
| 0..30cm | ph.h2o | pH | 6–6.8 | 5–8 | 560 |
| 30..60cm | clay | % | 13–32 | 4–49 | 560 |
| 30..60cm | sand | % | 43–80 | 6–94 | 560 |
| 30..60cm | silt | % | 6–25 | 0–44 | 560 |
| 30..60cm | bd.core | kg/m3 | 640–1530 | 460–1730 | 560 |
| 30..60cm | soc | g/kg | 3.9–50.4 | 1.1–112.9 | 560 |
| 30..60cm | ph.h2o | pH | 5.8–6.9 | 5.1–7.9 | 560 |
| 60..100cm | clay | % | 14–33 | 4–54 | 560 |
| 60..100cm | sand | % | 42–78 | 8–94 | 560 |
| 60..100cm | silt | % | 8–25 | 0–45 | 560 |
| 60..100cm | bd.core | kg/m3 | 670–1560 | 410–1810 | 560 |
| 60..100cm | soc | g/kg | 3.1–41.6 | 0.9–113.9 | 560 |
| 60..100cm | ph.h2o | pH | 5.7–7.2 | 4.7–8.4 | 560 |
