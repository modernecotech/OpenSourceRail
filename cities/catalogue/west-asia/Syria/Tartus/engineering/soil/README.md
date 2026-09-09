# Tartus civil soil screening

64 route/station sample locations; 64 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 20 |
| fine-soil-plasticity-and-shrink-swell-tests | 64 |
| granular-density-and-groundwater-tests | 61 |
| silt-moisture-frost-and-erosion-review | 5 |

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
| 0..30cm | clay | % | 18–27 | 1–42 | 64 |
| 0..30cm | sand | % | 43–62 | 14–92 | 64 |
| 0..30cm | silt | % | 19–31 | 0–47 | 64 |
| 0..30cm | bd.core | kg/m3 | 1270–1380 | 980–1620 | 64 |
| 0..30cm | soc | g/kg | 5–14.5 | 1.8–28.9 | 64 |
| 0..30cm | ph.h2o | pH | 6.4–7.6 | 5–8.2 | 64 |
| 30..60cm | clay | % | 18–29 | 2–47 | 64 |
| 30..60cm | sand | % | 41–64 | 11–95 | 64 |
| 30..60cm | silt | % | 16–31 | 0–51 | 64 |
| 30..60cm | bd.core | kg/m3 | 1350–1510 | 1110–1690 | 64 |
| 30..60cm | soc | g/kg | 2.6–8.7 | 1–28.4 | 64 |
| 30..60cm | ph.h2o | pH | 6.5–7.6 | 5.1–8.2 | 64 |
| 60..100cm | clay | % | 19–30 | 1–48 | 64 |
| 60..100cm | sand | % | 39–64 | 8–93 | 64 |
| 60..100cm | silt | % | 16–33 | 0–51 | 64 |
| 60..100cm | bd.core | kg/m3 | 1330–1530 | 1010–1750 | 64 |
| 60..100cm | soc | g/kg | 1.9–7 | 0.4–25.3 | 64 |
| 60..100cm | ph.h2o | pH | 6.6–7.4 | 5.1–8.3 | 64 |
