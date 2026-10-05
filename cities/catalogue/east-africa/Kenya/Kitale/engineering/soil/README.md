# Kitale civil soil screening

159 route/station sample locations; 159 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 54 |
| fine-soil-plasticity-and-shrink-swell-tests | 159 |
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
| 0..30cm | clay | % | 32–39 | 16–49 | 159 |
| 0..30cm | sand | % | 32–46 | 10–73 | 159 |
| 0..30cm | silt | % | 22–31 | 6–44 | 159 |
| 0..30cm | bd.core | kg/m3 | 1140–1280 | 920–1470 | 159 |
| 0..30cm | soc | g/kg | 11–25.6 | 5.8–48.9 | 159 |
| 0..30cm | ph.h2o | pH | 5.7–6.5 | 4.8–7.8 | 159 |
| 30..60cm | clay | % | 31–39 | 15–51 | 159 |
| 30..60cm | sand | % | 33–49 | 10–75 | 159 |
| 30..60cm | silt | % | 20–29 | 4–45 | 159 |
| 30..60cm | bd.core | kg/m3 | 1210–1340 | 990–1530 | 159 |
| 30..60cm | soc | g/kg | 7.3–10.8 | 3.8–18.8 | 159 |
| 30..60cm | ph.h2o | pH | 5.8–6.7 | 4.8–7.8 | 159 |
| 60..100cm | clay | % | 30–38 | 11–50 | 159 |
| 60..100cm | sand | % | 34–50 | 10–79 | 159 |
| 60..100cm | silt | % | 19–29 | 3–45 | 159 |
| 60..100cm | bd.core | kg/m3 | 1220–1300 | 980–1550 | 159 |
| 60..100cm | soc | g/kg | 5.4–8 | 2.7–16 | 159 |
| 60..100cm | ph.h2o | pH | 5.9–7 | 4.8–8.1 | 159 |
