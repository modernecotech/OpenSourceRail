# Huambo civil soil screening

551 route/station sample locations; 551 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 551 |
| fine-soil-plasticity-and-shrink-swell-tests | 551 |
| granular-density-and-groundwater-tests | 317 |

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
| 0..30cm | clay | % | 30–38 | 14–51 | 551 |
| 0..30cm | sand | % | 38–54 | 12–85 | 551 |
| 0..30cm | silt | % | 17–24 | 0–39 | 551 |
| 0..30cm | bd.core | kg/m3 | 1190–1390 | 930–1570 | 551 |
| 0..30cm | soc | g/kg | 6.3–17.4 | 2.2–35.3 | 551 |
| 0..30cm | ph.h2o | pH | 5.4–5.9 | 4.5–7.1 | 551 |
| 30..60cm | clay | % | 32–42 | 13–57 | 551 |
| 30..60cm | sand | % | 33–52 | 7–85 | 551 |
| 30..60cm | silt | % | 16–26 | 0–47 | 551 |
| 30..60cm | bd.core | kg/m3 | 1290–1420 | 1040–1600 | 551 |
| 30..60cm | soc | g/kg | 4–8.7 | 1.4–17.9 | 551 |
| 30..60cm | ph.h2o | pH | 5.5–6 | 4.5–7 | 551 |
| 60..100cm | clay | % | 32–42 | 12–58 | 551 |
| 60..100cm | sand | % | 32–50 | 4–84 | 551 |
| 60..100cm | silt | % | 18–27 | 0–46 | 551 |
| 60..100cm | bd.core | kg/m3 | 1280–1440 | 910–1690 | 551 |
| 60..100cm | soc | g/kg | 3.6–7.3 | 0.8–16.8 | 551 |
| 60..100cm | ph.h2o | pH | 5.6–6.1 | 4.4–7.4 | 551 |
