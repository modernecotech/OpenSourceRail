# Abha civil soil screening

478 route/station sample locations; 469 complete profiles; 9 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 9 |
| fine-soil-plasticity-and-shrink-swell-tests | 469 |
| granular-density-and-groundwater-tests | 462 |

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
| 0..30cm | clay | % | 20–29 | 8–43 | 469 |
| 0..30cm | sand | % | 42–60 | 16–83 | 469 |
| 0..30cm | silt | % | 20–30 | 3–44 | 469 |
| 0..30cm | bd.core | kg/m3 | 1360–1530 | 1180–1740 | 469 |
| 0..30cm | soc | g/kg | 2.7–10.3 | 1–19.7 | 469 |
| 0..30cm | ph.h2o | pH | 7.8–8.2 | 6.9–8.9 | 469 |
| 30..60cm | clay | % | 22–30 | 6–46 | 469 |
| 30..60cm | sand | % | 42–58 | 14–90 | 469 |
| 30..60cm | silt | % | 20–29 | 0–46 | 469 |
| 30..60cm | bd.core | kg/m3 | 1400–1530 | 1130–1700 | 469 |
| 30..60cm | soc | g/kg | 1.9–7 | 0.4–13.7 | 469 |
| 30..60cm | ph.h2o | pH | 7.8–8.3 | 6.5–9 | 469 |
| 60..100cm | clay | % | 22–30 | 6–45 | 469 |
| 60..100cm | sand | % | 41–58 | 12–89 | 469 |
| 60..100cm | silt | % | 20–29 | 0–47 | 469 |
| 60..100cm | bd.core | kg/m3 | 1390–1530 | 1060–1750 | 469 |
| 60..100cm | soc | g/kg | 1.5–4.3 | 0.2–10.2 | 469 |
| 60..100cm | ph.h2o | pH | 7.9–8.5 | 7.2–9.1 | 469 |
