# Mombasa civil soil screening

316 route/station sample locations; 298 complete profiles; 18 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 278 |
| coverage-gap | 18 |
| fine-soil-plasticity-and-shrink-swell-tests | 90 |
| granular-density-and-groundwater-tests | 298 |
| organic-content-and-compressibility-tests | 7 |

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
| 0..30cm | clay | % | 9–36 | 1–50 | 298 |
| 0..30cm | sand | % | 38–82 | 7–93 | 298 |
| 0..30cm | silt | % | 9–29 | 0–45 | 298 |
| 0..30cm | bd.core | kg/m3 | 860–1470 | 590–1630 | 298 |
| 0..30cm | soc | g/kg | 4.9–43.5 | 2.1–90.9 | 298 |
| 0..30cm | ph.h2o | pH | 6.1–7 | 5–8 | 298 |
| 30..60cm | clay | % | 8–36 | 1–50 | 298 |
| 30..60cm | sand | % | 38–85 | 4–97 | 298 |
| 30..60cm | silt | % | 6–29 | 0–46 | 298 |
| 30..60cm | bd.core | kg/m3 | 860–1500 | 620–1730 | 298 |
| 30..60cm | soc | g/kg | 3.2–42.9 | 1.1–87.3 | 298 |
| 30..60cm | ph.h2o | pH | 6.1–7.1 | 5.1–8.1 | 298 |
| 60..100cm | clay | % | 8–35 | 1–49 | 298 |
| 60..100cm | sand | % | 39–84 | 4–97 | 298 |
| 60..100cm | silt | % | 7–29 | 0–46 | 298 |
| 60..100cm | bd.core | kg/m3 | 860–1510 | 620–1750 | 298 |
| 60..100cm | soc | g/kg | 2.2–35.9 | 0.7–94.9 | 298 |
| 60..100cm | ph.h2o | pH | 6.1–7.1 | 4.7–8.5 | 298 |
