# Kitale civil soil screening

917 route/station sample locations; 917 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 440 |
| fine-soil-plasticity-and-shrink-swell-tests | 917 |
| granular-density-and-groundwater-tests | 216 |

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
| 0..30cm | clay | % | 29–39 | 15–50 | 917 |
| 0..30cm | sand | % | 30–49 | 9–76 | 917 |
| 0..30cm | silt | % | 22–31 | 6–44 | 917 |
| 0..30cm | bd.core | kg/m3 | 1100–1280 | 880–1450 | 917 |
| 0..30cm | soc | g/kg | 7.1–25.6 | 2.3–48.9 | 917 |
| 0..30cm | ph.h2o | pH | 5.7–6.7 | 4.8–8 | 917 |
| 30..60cm | clay | % | 30–39 | 15–52 | 917 |
| 30..60cm | sand | % | 32–51 | 9–75 | 917 |
| 30..60cm | silt | % | 19–29 | 3–45 | 917 |
| 30..60cm | bd.core | kg/m3 | 1180–1340 | 980–1540 | 917 |
| 30..60cm | soc | g/kg | 6.1–10.8 | 2.4–18.3 | 917 |
| 30..60cm | ph.h2o | pH | 5.8–6.8 | 4.8–8.1 | 917 |
| 60..100cm | clay | % | 30–38 | 11–50 | 917 |
| 60..100cm | sand | % | 33–53 | 9–80 | 917 |
| 60..100cm | silt | % | 18–29 | 3–46 | 917 |
| 60..100cm | bd.core | kg/m3 | 1220–1330 | 980–1550 | 917 |
| 60..100cm | soc | g/kg | 4.4–8 | 1.6–15.6 | 917 |
| 60..100cm | ph.h2o | pH | 5.9–7 | 4.8–8.1 | 917 |
