# Bamako civil soil screening

3,346 route/station sample locations; 3,322 complete profiles; 24 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 3270 |
| coverage-gap | 24 |
| fine-soil-plasticity-and-shrink-swell-tests | 3322 |
| granular-density-and-groundwater-tests | 3310 |

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
| 0..30cm | clay | % | 25–37 | 6–54 | 3322 |
| 0..30cm | sand | % | 36–59 | 7–92 | 3322 |
| 0..30cm | silt | % | 16–27 | 0–46 | 3322 |
| 0..30cm | bd.core | kg/m3 | 1390–1550 | 1140–1720 | 3322 |
| 0..30cm | soc | g/kg | 3.9–10 | 1.8–20 | 3322 |
| 0..30cm | ph.h2o | pH | 5.2–6.7 | 4–7.9 | 3322 |
| 30..60cm | clay | % | 27–39 | 6–56 | 3322 |
| 30..60cm | sand | % | 36–56 | 5–92 | 3322 |
| 30..60cm | silt | % | 15–28 | 0–47 | 3322 |
| 30..60cm | bd.core | kg/m3 | 1370–1530 | 1100–1750 | 3322 |
| 30..60cm | soc | g/kg | 2.6–5 | 0.9–10.3 | 3322 |
| 30..60cm | ph.h2o | pH | 5.7–7.4 | 4.7–8.4 | 3322 |
| 60..100cm | clay | % | 27–40 | 6–57 | 3322 |
| 60..100cm | sand | % | 35–57 | 5–92 | 3322 |
| 60..100cm | silt | % | 15–29 | 0–47 | 3322 |
| 60..100cm | bd.core | kg/m3 | 1370–1530 | 1090–1780 | 3322 |
| 60..100cm | soc | g/kg | 2–4.3 | 0.5–10.5 | 3322 |
| 60..100cm | ph.h2o | pH | 6.1–7.7 | 4.9–8.6 | 3322 |
