# Aden civil soil screening

708 route/station sample locations; 331 complete profiles; 377 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 377 |
| fine-soil-plasticity-and-shrink-swell-tests | 16 |
| granular-density-and-groundwater-tests | 331 |

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
| 0..30cm | clay | % | 11–18 | 0–32 | 331 |
| 0..30cm | sand | % | 59–72 | 28–96 | 331 |
| 0..30cm | silt | % | 16–23 | 2–41 | 331 |
| 0..30cm | bd.core | kg/m3 | 1370–1490 | 1020–1720 | 331 |
| 0..30cm | soc | g/kg | 2.5–7.8 | 0.5–23.9 | 331 |
| 0..30cm | ph.h2o | pH | 8–8.8 | 7.1–9.6 | 331 |
| 30..60cm | clay | % | 11–20 | 0–34 | 331 |
| 30..60cm | sand | % | 57–72 | 24–97 | 331 |
| 30..60cm | silt | % | 15–23 | 0–42 | 331 |
| 30..60cm | bd.core | kg/m3 | 1380–1540 | 980–1730 | 331 |
| 30..60cm | soc | g/kg | 1.4–8.1 | 0–48.4 | 331 |
| 30..60cm | ph.h2o | pH | 8.1–8.8 | 7.4–9.5 | 331 |
| 60..100cm | clay | % | 12–21 | 0–35 | 331 |
| 60..100cm | sand | % | 56–72 | 24–96 | 331 |
| 60..100cm | silt | % | 16–23 | 0–44 | 331 |
| 60..100cm | bd.core | kg/m3 | 1280–1560 | 750–1770 | 331 |
| 60..100cm | soc | g/kg | 1.2–6 | 0–38.8 | 331 |
| 60..100cm | ph.h2o | pH | 8.1–9 | 7.5–9.5 | 331 |
