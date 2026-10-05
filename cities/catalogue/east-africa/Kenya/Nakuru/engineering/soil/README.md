# Nakuru civil soil screening

86 route/station sample locations; 86 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 3 |
| fine-soil-plasticity-and-shrink-swell-tests | 71 |
| granular-density-and-groundwater-tests | 67 |

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
| 0..30cm | clay | % | 21–36 | 9–48 | 86 |
| 0..30cm | sand | % | 37–63 | 11–83 | 86 |
| 0..30cm | silt | % | 16–29 | 5–45 | 86 |
| 0..30cm | bd.core | kg/m3 | 1060–1300 | 730–1490 | 86 |
| 0..30cm | soc | g/kg | 8.2–21.2 | 3–38.6 | 86 |
| 0..30cm | ph.h2o | pH | 6.1–7.4 | 5–8.3 | 86 |
| 30..60cm | clay | % | 20–36 | 10–48 | 86 |
| 30..60cm | sand | % | 36–63 | 13–80 | 86 |
| 30..60cm | silt | % | 16–28 | 3–44 | 86 |
| 30..60cm | bd.core | kg/m3 | 1160–1340 | 840–1540 | 86 |
| 30..60cm | soc | g/kg | 6.4–10.7 | 2.7–17.1 | 86 |
| 30..60cm | ph.h2o | pH | 6.4–7.5 | 5.3–8.6 | 86 |
| 60..100cm | clay | % | 17–36 | 7–47 | 86 |
| 60..100cm | sand | % | 36–69 | 12–85 | 86 |
| 60..100cm | silt | % | 13–28 | 1–47 | 86 |
| 60..100cm | bd.core | kg/m3 | 1190–1340 | 930–1600 | 86 |
| 60..100cm | soc | g/kg | 4.5–7.4 | 1.4–12.7 | 86 |
| 60..100cm | ph.h2o | pH | 6.6–7.7 | 5.5–9 | 86 |
