# Onitsha civil soil screening

3,072 route/station sample locations; 3,008 complete profiles; 64 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 3008 |
| coverage-gap | 64 |
| fine-soil-plasticity-and-shrink-swell-tests | 3008 |
| granular-density-and-groundwater-tests | 2516 |
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
| 0..30cm | clay | % | 22–36 | 3–50 | 3008 |
| 0..30cm | sand | % | 40–69 | 13–96 | 3008 |
| 0..30cm | silt | % | 7–26 | 0–41 | 3008 |
| 0..30cm | bd.core | kg/m3 | 790–1480 | 330–1630 | 3008 |
| 0..30cm | soc | g/kg | 5.9–22 | 1.9–59.8 | 3008 |
| 0..30cm | ph.h2o | pH | 5.1–6.2 | 4.5–7 | 3008 |
| 30..60cm | clay | % | 23–39 | 4–52 | 3008 |
| 30..60cm | sand | % | 37–67 | 12–96 | 3008 |
| 30..60cm | silt | % | 7–25 | 0–41 | 3008 |
| 30..60cm | bd.core | kg/m3 | 910–1510 | 500–1660 | 3008 |
| 30..60cm | soc | g/kg | 3.1–16.9 | 0.9–46.1 | 3008 |
| 30..60cm | ph.h2o | pH | 5.1–6.2 | 4.6–7.1 | 3008 |
| 60..100cm | clay | % | 24–41 | 4–58 | 3008 |
| 60..100cm | sand | % | 34–68 | 8–96 | 3008 |
| 60..100cm | silt | % | 7–27 | 0–47 | 3008 |
| 60..100cm | bd.core | kg/m3 | 1020–1510 | 530–1690 | 3008 |
| 60..100cm | soc | g/kg | 2.5–17.8 | 0.6–57.8 | 3008 |
| 60..100cm | ph.h2o | pH | 5.2–6.2 | 4.6–7.2 | 3008 |
