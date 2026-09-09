# Latakia civil soil screening

103 route/station sample locations; 103 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 98 |
| granular-density-and-groundwater-tests | 89 |
| silt-moisture-frost-and-erosion-review | 2 |

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
| 0..30cm | clay | % | 21–28 | 3–44 | 103 |
| 0..30cm | sand | % | 41–57 | 11–92 | 103 |
| 0..30cm | silt | % | 22–33 | 4–48 | 103 |
| 0..30cm | bd.core | kg/m3 | 1260–1390 | 990–1600 | 103 |
| 0..30cm | soc | g/kg | 5.4–13.7 | 2–27.9 | 103 |
| 0..30cm | ph.h2o | pH | 7.1–7.7 | 5.7–8.3 | 103 |
| 30..60cm | clay | % | 21–29 | 1–44 | 103 |
| 30..60cm | sand | % | 41–58 | 12–91 | 103 |
| 30..60cm | silt | % | 21–33 | 0–48 | 103 |
| 30..60cm | bd.core | kg/m3 | 1350–1520 | 1060–1720 | 103 |
| 30..60cm | soc | g/kg | 3.3–6.8 | 1.4–15.7 | 103 |
| 30..60cm | ph.h2o | pH | 7.1–7.6 | 5.8–8.2 | 103 |
| 60..100cm | clay | % | 21–30 | 2–44 | 103 |
| 60..100cm | sand | % | 40–58 | 15–92 | 103 |
| 60..100cm | silt | % | 20–34 | 0–50 | 103 |
| 60..100cm | bd.core | kg/m3 | 1360–1560 | 970–1730 | 103 |
| 60..100cm | soc | g/kg | 1.9–5.5 | 0.5–13.9 | 103 |
| 60..100cm | ph.h2o | pH | 7–7.6 | 5.6–8.3 | 103 |
