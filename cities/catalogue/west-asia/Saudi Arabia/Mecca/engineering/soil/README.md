# Mecca civil soil screening

385 route/station sample locations; 284 complete profiles; 101 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 101 |
| fine-soil-plasticity-and-shrink-swell-tests | 108 |
| granular-density-and-groundwater-tests | 284 |

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
| 0..30cm | clay | % | 13–21 | 3–34 | 284 |
| 0..30cm | sand | % | 59–74 | 33–91 | 284 |
| 0..30cm | silt | % | 13–20 | 0–35 | 284 |
| 0..30cm | bd.core | kg/m3 | 1430–1510 | 1200–1720 | 284 |
| 0..30cm | soc | g/kg | 1.7–3.1 | 0.3–9.5 | 284 |
| 0..30cm | ph.h2o | pH | 8.1–8.7 | 7.7–9.5 | 284 |
| 30..60cm | clay | % | 13–23 | 1–39 | 284 |
| 30..60cm | sand | % | 55–73 | 20–94 | 284 |
| 30..60cm | silt | % | 14–22 | 0–40 | 284 |
| 30..60cm | bd.core | kg/m3 | 1460–1580 | 1190–1800 | 284 |
| 30..60cm | soc | g/kg | 1–2.5 | 0–7.5 | 284 |
| 30..60cm | ph.h2o | pH | 8.3–8.9 | 7.8–9.8 | 284 |
| 60..100cm | clay | % | 13–23 | 1–41 | 284 |
| 60..100cm | sand | % | 54–73 | 20–94 | 284 |
| 60..100cm | silt | % | 14–23 | 0–41 | 284 |
| 60..100cm | bd.core | kg/m3 | 1490–1600 | 1230–1900 | 284 |
| 60..100cm | soc | g/kg | 1–2.7 | 0–9.8 | 284 |
| 60..100cm | ph.h2o | pH | 8.3–8.9 | 7.6–10.2 | 284 |
