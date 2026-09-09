# Ngaoundere civil soil screening

199 route/station sample locations; 199 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 199 |
| fine-soil-plasticity-and-shrink-swell-tests | 199 |
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
| 0..30cm | clay | % | 21–26 | 8–41 | 199 |
| 0..30cm | sand | % | 48–58 | 18–81 | 199 |
| 0..30cm | silt | % | 19–28 | 3–49 | 199 |
| 0..30cm | bd.core | kg/m3 | 1280–1410 | 1090–1600 | 199 |
| 0..30cm | soc | g/kg | 7.4–14.1 | 2.7–27.2 | 199 |
| 0..30cm | ph.h2o | pH | 5.6–6 | 4.7–6.6 | 199 |
| 30..60cm | clay | % | 23–30 | 7–50 | 199 |
| 30..60cm | sand | % | 43–55 | 13–84 | 199 |
| 30..60cm | silt | % | 20–29 | 1–48 | 199 |
| 30..60cm | bd.core | kg/m3 | 1340–1450 | 1070–1630 | 199 |
| 30..60cm | soc | g/kg | 4.4–7.3 | 1.5–12.5 | 199 |
| 30..60cm | ph.h2o | pH | 5.7–6 | 4.8–6.6 | 199 |
| 60..100cm | clay | % | 24–30 | 8–50 | 199 |
| 60..100cm | sand | % | 42–55 | 13–86 | 199 |
| 60..100cm | silt | % | 20–29 | 0–49 | 199 |
| 60..100cm | bd.core | kg/m3 | 1350–1490 | 1050–1690 | 199 |
| 60..100cm | soc | g/kg | 4.3–5.7 | 1.7–14.3 | 199 |
| 60..100cm | ph.h2o | pH | 5.6–6 | 4.8–6.6 | 199 |
