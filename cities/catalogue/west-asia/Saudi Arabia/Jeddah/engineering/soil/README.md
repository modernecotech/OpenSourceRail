# Jeddah civil soil screening

4,262 route/station sample locations; 3,994 complete profiles; 268 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 268 |
| fine-soil-plasticity-and-shrink-swell-tests | 1706 |
| granular-density-and-groundwater-tests | 3994 |

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
| 0..30cm | clay | % | 10–23 | 1–42 | 3994 |
| 0..30cm | sand | % | 55–82 | 27–96 | 3994 |
| 0..30cm | silt | % | 8–21 | 0–40 | 3994 |
| 0..30cm | bd.core | kg/m3 | 1380–1510 | 1020–1770 | 3994 |
| 0..30cm | soc | g/kg | 1.7–7.3 | 0.3–27.7 | 3994 |
| 0..30cm | ph.h2o | pH | 8–8.6 | 7.2–9.3 | 3994 |
| 30..60cm | clay | % | 11–26 | 0–41 | 3994 |
| 30..60cm | sand | % | 53–81 | 26–95 | 3994 |
| 30..60cm | silt | % | 6–21 | 0–44 | 3994 |
| 30..60cm | bd.core | kg/m3 | 1350–1560 | 980–1780 | 3994 |
| 30..60cm | soc | g/kg | 0.9–7.4 | 0–42 | 3994 |
| 30..60cm | ph.h2o | pH | 7.9–8.8 | 7.2–9.5 | 3994 |
| 60..100cm | clay | % | 11–26 | 0–42 | 3994 |
| 60..100cm | sand | % | 54–81 | 23–96 | 3994 |
| 60..100cm | silt | % | 6–21 | 0–44 | 3994 |
| 60..100cm | bd.core | kg/m3 | 1240–1600 | 590–1820 | 3994 |
| 60..100cm | soc | g/kg | 0.9–5.9 | 0–38.8 | 3994 |
| 60..100cm | ph.h2o | pH | 7.8–8.8 | 7–9.6 | 3994 |
