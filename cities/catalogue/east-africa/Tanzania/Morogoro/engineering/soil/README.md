# Morogoro civil soil screening

328 route/station sample locations; 328 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 215 |
| fine-soil-plasticity-and-shrink-swell-tests | 324 |
| granular-density-and-groundwater-tests | 301 |
| organic-content-and-compressibility-tests | 5 |

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
| 0..30cm | clay | % | 22–40 | 10–54 | 328 |
| 0..30cm | sand | % | 35–67 | 12–89 | 328 |
| 0..30cm | silt | % | 9–25 | 0–39 | 328 |
| 0..30cm | bd.core | kg/m3 | 1120–1420 | 920–1580 | 328 |
| 0..30cm | soc | g/kg | 5.8–26.9 | 2.6–61.2 | 328 |
| 0..30cm | ph.h2o | pH | 5.6–7.2 | 4.9–8.1 | 328 |
| 30..60cm | clay | % | 23–44 | 10–55 | 328 |
| 30..60cm | sand | % | 30–67 | 12–89 | 328 |
| 30..60cm | silt | % | 9–26 | 0–36 | 328 |
| 30..60cm | bd.core | kg/m3 | 1160–1440 | 960–1620 | 328 |
| 30..60cm | soc | g/kg | 3.8–10.6 | 1.7–17.7 | 328 |
| 30..60cm | ph.h2o | pH | 5.4–7.3 | 4.8–8.2 | 328 |
| 60..100cm | clay | % | 24–44 | 10–54 | 328 |
| 60..100cm | sand | % | 30–67 | 11–89 | 328 |
| 60..100cm | silt | % | 8–26 | 0–39 | 328 |
| 60..100cm | bd.core | kg/m3 | 1180–1450 | 980–1650 | 328 |
| 60..100cm | soc | g/kg | 3.7–7.3 | 1.7–12.5 | 328 |
| 60..100cm | ph.h2o | pH | 5.3–7.4 | 4.6–8.5 | 328 |
