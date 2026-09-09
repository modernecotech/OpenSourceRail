# Bamako civil soil screening

374 route/station sample locations; 351 complete profiles; 23 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 351 |
| coverage-gap | 23 |
| fine-soil-plasticity-and-shrink-swell-tests | 351 |
| granular-density-and-groundwater-tests | 340 |

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
| 0..30cm | clay | % | 26–38 | 6–53 | 351 |
| 0..30cm | sand | % | 36–58 | 8–91 | 351 |
| 0..30cm | silt | % | 16–27 | 0–46 | 351 |
| 0..30cm | bd.core | kg/m3 | 1390–1550 | 1140–1710 | 351 |
| 0..30cm | soc | g/kg | 3.9–10 | 1.9–17.6 | 351 |
| 0..30cm | ph.h2o | pH | 5.2–6.5 | 4–7.8 | 351 |
| 30..60cm | clay | % | 27–39 | 6–55 | 351 |
| 30..60cm | sand | % | 36–55 | 7–91 | 351 |
| 30..60cm | silt | % | 16–27 | 0–46 | 351 |
| 30..60cm | bd.core | kg/m3 | 1380–1530 | 1100–1750 | 351 |
| 30..60cm | soc | g/kg | 2.8–5.1 | 0.9–9.5 | 351 |
| 30..60cm | ph.h2o | pH | 5.7–7.1 | 4.8–8.3 | 351 |
| 60..100cm | clay | % | 27–40 | 6–56 | 351 |
| 60..100cm | sand | % | 35–55 | 7–91 | 351 |
| 60..100cm | silt | % | 16–28 | 0–47 | 351 |
| 60..100cm | bd.core | kg/m3 | 1380–1530 | 1090–1760 | 351 |
| 60..100cm | soc | g/kg | 1.9–4.3 | 0.6–10.6 | 351 |
| 60..100cm | ph.h2o | pH | 6.1–7.4 | 5–8.6 | 351 |
