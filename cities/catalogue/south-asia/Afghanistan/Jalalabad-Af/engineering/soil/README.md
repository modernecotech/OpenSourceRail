# Jalalabad-Af civil soil screening

129 route/station sample locations; 127 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 100 |
| granular-density-and-groundwater-tests | 71 |
| silt-moisture-frost-and-erosion-review | 4 |

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
| 0..30cm | clay | % | 20–24 | 8–36 | 127 |
| 0..30cm | sand | % | 43–51 | 16–75 | 127 |
| 0..30cm | silt | % | 28–33 | 11–50 | 127 |
| 0..30cm | bd.core | kg/m3 | 1350–1500 | 1090–1650 | 127 |
| 0..30cm | soc | g/kg | 4.1–6.6 | 1.8–15.9 | 127 |
| 0..30cm | ph.h2o | pH | 7.4–8.2 | 6.4–8.7 | 127 |
| 30..60cm | clay | % | 22–26 | 7–39 | 127 |
| 30..60cm | sand | % | 42–50 | 17–79 | 127 |
| 30..60cm | silt | % | 28–33 | 9–49 | 127 |
| 30..60cm | bd.core | kg/m3 | 1470–1570 | 1250–1750 | 127 |
| 30..60cm | soc | g/kg | 2.8–4.1 | 1–8.1 | 127 |
| 30..60cm | ph.h2o | pH | 7.5–8.4 | 6.7–9.2 | 127 |
| 60..100cm | clay | % | 22–26 | 7–41 | 127 |
| 60..100cm | sand | % | 42–50 | 14–79 | 127 |
| 60..100cm | silt | % | 28–33 | 8–51 | 127 |
| 60..100cm | bd.core | kg/m3 | 1510–1630 | 1270–1870 | 127 |
| 60..100cm | soc | g/kg | 1.8–3 | 0.4–7.1 | 127 |
| 60..100cm | ph.h2o | pH | 7.6–8.5 | 6.7–9.2 | 127 |
