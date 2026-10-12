# Rajkot civil soil screening

1,181 route/station sample locations; 1,179 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 828 |
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 1179 |
| granular-density-and-groundwater-tests | 1179 |
| silt-moisture-frost-and-erosion-review | 8 |

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
| 0..30cm | clay | % | 22–31 | 4–49 | 1179 |
| 0..30cm | sand | % | 42–62 | 9–90 | 1179 |
| 0..30cm | silt | % | 16–27 | 0–47 | 1179 |
| 0..30cm | bd.core | kg/m3 | 1390–1520 | 1080–1700 | 1179 |
| 0..30cm | soc | g/kg | 3.8–9.4 | 1.6–19 | 1179 |
| 0..30cm | ph.h2o | pH | 6.1–7.9 | 5–9.2 | 1179 |
| 30..60cm | clay | % | 24–33 | 5–49 | 1179 |
| 30..60cm | sand | % | 41–56 | 4–90 | 1179 |
| 30..60cm | silt | % | 19–26 | 0–50 | 1179 |
| 30..60cm | bd.core | kg/m3 | 1350–1540 | 1080–1750 | 1179 |
| 30..60cm | soc | g/kg | 2.5–5.4 | 0.7–12.9 | 1179 |
| 30..60cm | ph.h2o | pH | 6.5–8 | 5.4–9.4 | 1179 |
| 60..100cm | clay | % | 24–33 | 4–49 | 1179 |
| 60..100cm | sand | % | 40–56 | 3–92 | 1179 |
| 60..100cm | silt | % | 19–27 | 0–50 | 1179 |
| 60..100cm | bd.core | kg/m3 | 1370–1570 | 960–1830 | 1179 |
| 60..100cm | soc | g/kg | 1.9–3.9 | 0.4–8.7 | 1179 |
| 60..100cm | ph.h2o | pH | 6.8–8.2 | 5.6–9 | 1179 |
