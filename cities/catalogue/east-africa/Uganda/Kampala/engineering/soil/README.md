# Kampala civil soil screening

6,004 route/station sample locations; 6,004 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 2881 |
| fine-soil-plasticity-and-shrink-swell-tests | 6004 |
| granular-density-and-groundwater-tests | 281 |
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
| 0..30cm | clay | % | 29–44 | 15–53 | 6004 |
| 0..30cm | sand | % | 26–49 | 9–79 | 6004 |
| 0..30cm | silt | % | 18–34 | 2–48 | 6004 |
| 0..30cm | bd.core | kg/m3 | 1090–1330 | 840–1540 | 6004 |
| 0..30cm | soc | g/kg | 8.4–23.5 | 4–50.7 | 6004 |
| 0..30cm | ph.h2o | pH | 5.8–6.4 | 5.1–7.1 | 6004 |
| 30..60cm | clay | % | 31–47 | 15–59 | 6004 |
| 30..60cm | sand | % | 23–48 | 8–81 | 6004 |
| 30..60cm | silt | % | 18–30 | 0–46 | 6004 |
| 30..60cm | bd.core | kg/m3 | 1140–1380 | 850–1600 | 6004 |
| 30..60cm | soc | g/kg | 4.9–12 | 1.9–26.9 | 6004 |
| 30..60cm | ph.h2o | pH | 5.7–6.4 | 5–7.3 | 6004 |
| 60..100cm | clay | % | 32–48 | 15–59 | 6004 |
| 60..100cm | sand | % | 23–48 | 6–80 | 6004 |
| 60..100cm | silt | % | 18–30 | 0–45 | 6004 |
| 60..100cm | bd.core | kg/m3 | 1160–1420 | 830–1640 | 6004 |
| 60..100cm | soc | g/kg | 4.8–11.7 | 1.2–40.5 | 6004 |
| 60..100cm | ph.h2o | pH | 5.7–6.5 | 4.8–7.7 | 6004 |
