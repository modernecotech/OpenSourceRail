# Lahij civil soil screening

343 route/station sample locations; 294 complete profiles; 49 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 49 |
| fine-soil-plasticity-and-shrink-swell-tests | 5 |
| granular-density-and-groundwater-tests | 294 |

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
| 0..30cm | clay | % | 11–20 | 0–32 | 294 |
| 0..30cm | sand | % | 58–75 | 37–92 | 294 |
| 0..30cm | silt | % | 14–22 | 2–35 | 294 |
| 0..30cm | bd.core | kg/m3 | 1420–1500 | 1260–1680 | 294 |
| 0..30cm | soc | g/kg | 2.2–4.3 | 0.6–9 | 294 |
| 0..30cm | ph.h2o | pH | 7.9–8.7 | 7–9.4 | 294 |
| 30..60cm | clay | % | 11–21 | 1–37 | 294 |
| 30..60cm | sand | % | 56–76 | 23–95 | 294 |
| 30..60cm | silt | % | 13–23 | 0–40 | 294 |
| 30..60cm | bd.core | kg/m3 | 1460–1560 | 1240–1770 | 294 |
| 30..60cm | soc | g/kg | 1.3–2.6 | 0–5.8 | 294 |
| 30..60cm | ph.h2o | pH | 8.4–8.7 | 7.8–9.3 | 294 |
| 60..100cm | clay | % | 11–21 | 1–37 | 294 |
| 60..100cm | sand | % | 55–76 | 23–95 | 294 |
| 60..100cm | silt | % | 12–24 | 0–41 | 294 |
| 60..100cm | bd.core | kg/m3 | 1490–1580 | 1240–1800 | 294 |
| 60..100cm | soc | g/kg | 1.1–2.3 | 0–5.6 | 294 |
| 60..100cm | ph.h2o | pH | 8.4–8.7 | 7.9–9.4 | 294 |
