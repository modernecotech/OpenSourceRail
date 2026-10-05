# Masaka civil soil screening

50 route/station sample locations; 50 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 50 |
| fine-soil-plasticity-and-shrink-swell-tests | 50 |
| granular-density-and-groundwater-tests | 1 |

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
| 0..30cm | clay | % | 34–42 | 19–52 | 50 |
| 0..30cm | sand | % | 33–45 | 12–68 | 50 |
| 0..30cm | silt | % | 20–28 | 9–38 | 50 |
| 0..30cm | bd.core | kg/m3 | 1070–1240 | 820–1410 | 50 |
| 0..30cm | soc | g/kg | 11.2–23.5 | 6.9–39.8 | 50 |
| 0..30cm | ph.h2o | pH | 5.8–6.2 | 4.8–7.2 | 50 |
| 30..60cm | clay | % | 35–43 | 19–53 | 50 |
| 30..60cm | sand | % | 33–45 | 12–75 | 50 |
| 30..60cm | silt | % | 19–26 | 7–38 | 50 |
| 30..60cm | bd.core | kg/m3 | 1150–1270 | 930–1460 | 50 |
| 30..60cm | soc | g/kg | 8–13 | 4.2–28.1 | 50 |
| 30..60cm | ph.h2o | pH | 5.9–6.2 | 4.8–7.3 | 50 |
| 60..100cm | clay | % | 35–43 | 20–54 | 50 |
| 60..100cm | sand | % | 32–45 | 12–75 | 50 |
| 60..100cm | silt | % | 19–25 | 5–38 | 50 |
| 60..100cm | bd.core | kg/m3 | 1160–1290 | 850–1540 | 50 |
| 60..100cm | soc | g/kg | 6.7–13.3 | 2.5–31.2 | 50 |
| 60..100cm | ph.h2o | pH | 5.9–6.3 | 5–7.5 | 50 |
