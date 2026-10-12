# Kumba civil soil screening

1,402 route/station sample locations; 1,402 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1402 |
| fine-soil-plasticity-and-shrink-swell-tests | 1382 |
| granular-density-and-groundwater-tests | 1355 |
| organic-content-and-compressibility-tests | 372 |

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
| 0..30cm | clay | % | 19–34 | 8–51 | 1402 |
| 0..30cm | sand | % | 39–68 | 4–84 | 1402 |
| 0..30cm | silt | % | 13–28 | 1–43 | 1402 |
| 0..30cm | bd.core | kg/m3 | 970–1170 | 670–1390 | 1402 |
| 0..30cm | soc | g/kg | 10.2–39.4 | 2.9–84.1 | 1402 |
| 0..30cm | ph.h2o | pH | 5.4–5.8 | 4.7–6.4 | 1402 |
| 30..60cm | clay | % | 21–36 | 10–53 | 1402 |
| 30..60cm | sand | % | 37–63 | 6–80 | 1402 |
| 30..60cm | silt | % | 17–30 | 3–47 | 1402 |
| 30..60cm | bd.core | kg/m3 | 1020–1250 | 740–1590 | 1402 |
| 30..60cm | soc | g/kg | 6.1–20.1 | 2.1–43 | 1402 |
| 30..60cm | ph.h2o | pH | 5.5–5.8 | 4.8–6.4 | 1402 |
| 60..100cm | clay | % | 21–38 | 11–57 | 1402 |
| 60..100cm | sand | % | 34–61 | 1–78 | 1402 |
| 60..100cm | silt | % | 17–29 | 2–47 | 1402 |
| 60..100cm | bd.core | kg/m3 | 1070–1310 | 740–1600 | 1402 |
| 60..100cm | soc | g/kg | 5.2–12.4 | 2.4–27.7 | 1402 |
| 60..100cm | ph.h2o | pH | 5.5–5.9 | 4.8–6.5 | 1402 |
