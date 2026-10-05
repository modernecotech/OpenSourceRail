# Hofuf civil soil screening

132 route/station sample locations; 102 complete profiles; 30 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 30 |
| fine-soil-plasticity-and-shrink-swell-tests | 26 |
| granular-density-and-groundwater-tests | 90 |
| silt-moisture-frost-and-erosion-review | 3 |

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
| 0..30cm | clay | % | 11–25 | 0–37 | 102 |
| 0..30cm | sand | % | 41–68 | 13–94 | 102 |
| 0..30cm | silt | % | 20–34 | 4–49 | 102 |
| 0..30cm | bd.core | kg/m3 | 1430–1530 | 1250–1710 | 102 |
| 0..30cm | soc | g/kg | 2.6–4.7 | 0.4–10.3 | 102 |
| 0..30cm | ph.h2o | pH | 8–8.4 | 7.4–9.2 | 102 |
| 30..60cm | clay | % | 15–26 | 0–41 | 102 |
| 30..60cm | sand | % | 41–63 | 14–94 | 102 |
| 30..60cm | silt | % | 22–34 | 3–50 | 102 |
| 30..60cm | bd.core | kg/m3 | 1370–1510 | 1190–1710 | 102 |
| 30..60cm | soc | g/kg | 1.9–3 | 0.1–8.4 | 102 |
| 30..60cm | ph.h2o | pH | 8.2–8.7 | 7.5–9.8 | 102 |
| 60..100cm | clay | % | 15–25 | 0–39 | 102 |
| 60..100cm | sand | % | 41–63 | 14–93 | 102 |
| 60..100cm | silt | % | 22–34 | 3–47 | 102 |
| 60..100cm | bd.core | kg/m3 | 1410–1550 | 1230–1770 | 102 |
| 60..100cm | soc | g/kg | 1.5–3 | 0–8.3 | 102 |
| 60..100cm | ph.h2o | pH | 8.2–8.8 | 7.6–10.1 | 102 |
