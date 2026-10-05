# Suez civil soil screening

93 route/station sample locations; 47 complete profiles; 46 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 46 |
| fine-soil-plasticity-and-shrink-swell-tests | 7 |
| granular-density-and-groundwater-tests | 47 |

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
| 0..30cm | clay | % | 10–21 | 1–38 | 47 |
| 0..30cm | sand | % | 53–75 | 20–92 | 47 |
| 0..30cm | silt | % | 15–26 | 4–42 | 47 |
| 0..30cm | bd.core | kg/m3 | 1460–1530 | 1280–1680 | 47 |
| 0..30cm | soc | g/kg | 1.6–5.2 | 0.6–17 | 47 |
| 0..30cm | ph.h2o | pH | 7.9–8.6 | 7–9.4 | 47 |
| 30..60cm | clay | % | 10–22 | 0–39 | 47 |
| 30..60cm | sand | % | 52–76 | 19–94 | 47 |
| 30..60cm | silt | % | 13–26 | 3–43 | 47 |
| 30..60cm | bd.core | kg/m3 | 1500–1560 | 1360–1700 | 47 |
| 30..60cm | soc | g/kg | 1.4–5.7 | 0–42 | 47 |
| 30..60cm | ph.h2o | pH | 8.1–8.8 | 7.2–9.7 | 47 |
| 60..100cm | clay | % | 10–22 | 0–38 | 47 |
| 60..100cm | sand | % | 53–77 | 19–94 | 47 |
| 60..100cm | silt | % | 13–26 | 3–43 | 47 |
| 60..100cm | bd.core | kg/m3 | 1520–1600 | 1300–1870 | 47 |
| 60..100cm | soc | g/kg | 1.1–4 | 0–30.8 | 47 |
| 60..100cm | ph.h2o | pH | 8–8.8 | 7–9.8 | 47 |
