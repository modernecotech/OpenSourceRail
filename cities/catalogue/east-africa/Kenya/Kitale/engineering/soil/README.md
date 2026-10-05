# Kitale civil soil screening

96 route/station sample locations; 96 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 36 |
| fine-soil-plasticity-and-shrink-swell-tests | 96 |
| granular-density-and-groundwater-tests | 21 |

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
| 0..30cm | clay | % | 32–38 | 16–49 | 96 |
| 0..30cm | sand | % | 33–46 | 10–73 | 96 |
| 0..30cm | silt | % | 22–30 | 6–44 | 96 |
| 0..30cm | bd.core | kg/m3 | 1140–1270 | 920–1480 | 96 |
| 0..30cm | soc | g/kg | 12.9–25.2 | 7.2–49 | 96 |
| 0..30cm | ph.h2o | pH | 5.7–6.5 | 4.9–7.7 | 96 |
| 30..60cm | clay | % | 31–38 | 15–51 | 96 |
| 30..60cm | sand | % | 33–49 | 11–75 | 96 |
| 30..60cm | silt | % | 20–29 | 4–43 | 96 |
| 30..60cm | bd.core | kg/m3 | 1210–1320 | 990–1510 | 96 |
| 30..60cm | soc | g/kg | 7.6–10.6 | 4.3–18.8 | 96 |
| 30..60cm | ph.h2o | pH | 5.8–6.7 | 4.9–7.8 | 96 |
| 60..100cm | clay | % | 31–38 | 11–50 | 96 |
| 60..100cm | sand | % | 34–50 | 12–79 | 96 |
| 60..100cm | silt | % | 19–28 | 3–44 | 96 |
| 60..100cm | bd.core | kg/m3 | 1220–1310 | 980–1570 | 96 |
| 60..100cm | soc | g/kg | 5.7–7.4 | 2.7–16 | 96 |
| 60..100cm | ph.h2o | pH | 5.9–7 | 4.9–8 | 96 |
