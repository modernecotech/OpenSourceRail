# Khulna civil soil screening

5,622 route/station sample locations; 5,613 complete profiles; 9 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 5585 |
| coverage-gap | 9 |
| fine-soil-plasticity-and-shrink-swell-tests | 5613 |
| granular-density-and-groundwater-tests | 5613 |
| organic-content-and-compressibility-tests | 2873 |

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
| 0..30cm | clay | % | 18–29 | 4–46 | 5613 |
| 0..30cm | sand | % | 42–66 | 7–89 | 5613 |
| 0..30cm | silt | % | 17–30 | 2–49 | 5613 |
| 0..30cm | bd.core | kg/m3 | 750–1180 | 400–1540 | 5613 |
| 0..30cm | soc | g/kg | 8.8–46.2 | 3.5–181.8 | 5613 |
| 0..30cm | ph.h2o | pH | 5.9–6.6 | 4.7–7.9 | 5613 |
| 30..60cm | clay | % | 19–29 | 2–47 | 5613 |
| 30..60cm | sand | % | 40–65 | 7–90 | 5613 |
| 30..60cm | silt | % | 16–32 | 3–49 | 5613 |
| 30..60cm | bd.core | kg/m3 | 810–1210 | 510–1560 | 5613 |
| 30..60cm | soc | g/kg | 5.8–28.3 | 1.2–106.5 | 5613 |
| 30..60cm | ph.h2o | pH | 6.2–6.9 | 4.7–8 | 5613 |
| 60..100cm | clay | % | 20–29 | 2–48 | 5613 |
| 60..100cm | sand | % | 39–62 | 7–91 | 5613 |
| 60..100cm | silt | % | 18–32 | 2–49 | 5613 |
| 60..100cm | bd.core | kg/m3 | 890–1210 | 530–1740 | 5613 |
| 60..100cm | soc | g/kg | 4.5–18.4 | 1.2–90.2 | 5613 |
| 60..100cm | ph.h2o | pH | 6.3–7.1 | 4.6–8.2 | 5613 |
