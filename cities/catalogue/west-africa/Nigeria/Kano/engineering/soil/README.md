# Kano civil soil screening

1,239 route/station sample locations; 1,239 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1197 |
| fine-soil-plasticity-and-shrink-swell-tests | 1079 |
| granular-density-and-groundwater-tests | 1239 |

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
| 0..30cm | clay | % | 17–28 | 6–42 | 1239 |
| 0..30cm | sand | % | 45–67 | 20–88 | 1239 |
| 0..30cm | silt | % | 15–28 | 1–44 | 1239 |
| 0..30cm | bd.core | kg/m3 | 1380–1530 | 1110–1720 | 1239 |
| 0..30cm | soc | g/kg | 3.5–7.5 | 1.5–15.8 | 1239 |
| 0..30cm | ph.h2o | pH | 5.7–6.3 | 4.9–7.1 | 1239 |
| 30..60cm | clay | % | 19–27 | 4–45 | 1239 |
| 30..60cm | sand | % | 49–65 | 15–91 | 1239 |
| 30..60cm | silt | % | 15–26 | 0–45 | 1239 |
| 30..60cm | bd.core | kg/m3 | 1400–1540 | 1100–1760 | 1239 |
| 30..60cm | soc | g/kg | 2.6–4.9 | 0.9–10.5 | 1239 |
| 30..60cm | ph.h2o | pH | 6.1–6.6 | 5.1–7.4 | 1239 |
| 60..100cm | clay | % | 20–28 | 3–45 | 1239 |
| 60..100cm | sand | % | 47–64 | 15–90 | 1239 |
| 60..100cm | silt | % | 16–26 | 0–47 | 1239 |
| 60..100cm | bd.core | kg/m3 | 1360–1520 | 770–1790 | 1239 |
| 60..100cm | soc | g/kg | 1.8–4 | 0.5–7.8 | 1239 |
| 60..100cm | ph.h2o | pH | 6.4–6.9 | 5.2–8.1 | 1239 |
