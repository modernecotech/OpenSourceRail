# Hodeidah civil soil screening

514 route/station sample locations; 184 complete profiles; 330 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 330 |
| fine-soil-plasticity-and-shrink-swell-tests | 6 |
| granular-density-and-groundwater-tests | 184 |

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
| 0..30cm | clay | % | 11–17 | 0–31 | 184 |
| 0..30cm | sand | % | 61–74 | 33–97 | 184 |
| 0..30cm | silt | % | 15–21 | 2–38 | 184 |
| 0..30cm | bd.core | kg/m3 | 1390–1440 | 1030–1700 | 184 |
| 0..30cm | soc | g/kg | 2.5–6.6 | 0.7–20.7 | 184 |
| 0..30cm | ph.h2o | pH | 8.4–8.7 | 7.8–9.4 | 184 |
| 30..60cm | clay | % | 12–18 | 0–31 | 184 |
| 30..60cm | sand | % | 60–74 | 29–98 | 184 |
| 30..60cm | silt | % | 14–22 | 0–38 | 184 |
| 30..60cm | bd.core | kg/m3 | 1490–1540 | 1280–1720 | 184 |
| 30..60cm | soc | g/kg | 1.3–6.5 | 0–41.5 | 184 |
| 30..60cm | ph.h2o | pH | 8.4–8.7 | 7.5–9.3 | 184 |
| 60..100cm | clay | % | 12–18 | 0–35 | 184 |
| 60..100cm | sand | % | 60–75 | 26–98 | 184 |
| 60..100cm | silt | % | 14–22 | 0–40 | 184 |
| 60..100cm | bd.core | kg/m3 | 1520–1570 | 1330–1790 | 184 |
| 60..100cm | soc | g/kg | 1.2–4.6 | 0–27.6 | 184 |
| 60..100cm | ph.h2o | pH | 8.4–8.8 | 7.6–9.4 | 184 |
