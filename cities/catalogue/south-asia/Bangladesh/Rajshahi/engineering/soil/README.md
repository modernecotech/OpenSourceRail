# Rajshahi civil soil screening

199 route/station sample locations; 199 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 199 |
| fine-soil-plasticity-and-shrink-swell-tests | 48 |
| granular-density-and-groundwater-tests | 199 |

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
| 0..30cm | clay | % | 15–25 | 3–40 | 199 |
| 0..30cm | sand | % | 48–69 | 19–90 | 199 |
| 0..30cm | silt | % | 16–27 | 4–44 | 199 |
| 0..30cm | bd.core | kg/m3 | 1140–1310 | 810–1580 | 199 |
| 0..30cm | soc | g/kg | 7.4–15.6 | 2.7–42.5 | 199 |
| 0..30cm | ph.h2o | pH | 6–6.4 | 4.8–7.7 | 199 |
| 30..60cm | clay | % | 14–25 | 3–38 | 199 |
| 30..60cm | sand | % | 47–70 | 18–92 | 199 |
| 30..60cm | silt | % | 16–28 | 2–45 | 199 |
| 30..60cm | bd.core | kg/m3 | 1210–1400 | 810–1620 | 199 |
| 30..60cm | soc | g/kg | 4.3–10.4 | 1.9–23 | 199 |
| 30..60cm | ph.h2o | pH | 6.1–6.5 | 5–7.9 | 199 |
| 60..100cm | clay | % | 15–26 | 2–39 | 199 |
| 60..100cm | sand | % | 47–69 | 16–92 | 199 |
| 60..100cm | silt | % | 17–28 | 2–47 | 199 |
| 60..100cm | bd.core | kg/m3 | 1270–1470 | 780–1820 | 199 |
| 60..100cm | soc | g/kg | 2.9–7.7 | 1.2–23.4 | 199 |
| 60..100cm | ph.h2o | pH | 6.3–6.7 | 4.8–8.1 | 199 |
