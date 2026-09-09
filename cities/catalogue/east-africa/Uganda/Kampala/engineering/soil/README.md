# Kampala civil soil screening

652 route/station sample locations; 652 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 318 |
| fine-soil-plasticity-and-shrink-swell-tests | 652 |
| granular-density-and-groundwater-tests | 27 |

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
| 0..30cm | clay | % | 30–44 | 17–53 | 652 |
| 0..30cm | sand | % | 26–48 | 9–78 | 652 |
| 0..30cm | silt | % | 19–34 | 2–46 | 652 |
| 0..30cm | bd.core | kg/m3 | 1100–1280 | 880–1540 | 652 |
| 0..30cm | soc | g/kg | 8.4–21 | 4.5–37.6 | 652 |
| 0..30cm | ph.h2o | pH | 5.8–6.4 | 5.2–7.1 | 652 |
| 30..60cm | clay | % | 33–47 | 19–58 | 652 |
| 30..60cm | sand | % | 24–46 | 9–79 | 652 |
| 30..60cm | silt | % | 19–30 | 2–46 | 652 |
| 30..60cm | bd.core | kg/m3 | 1150–1270 | 850–1540 | 652 |
| 30..60cm | soc | g/kg | 5–11.8 | 2.2–24.5 | 652 |
| 30..60cm | ph.h2o | pH | 5.7–6.4 | 5.1–7.5 | 652 |
| 60..100cm | clay | % | 32–47 | 19–60 | 652 |
| 60..100cm | sand | % | 24–46 | 6–77 | 652 |
| 60..100cm | silt | % | 18–30 | 2–44 | 652 |
| 60..100cm | bd.core | kg/m3 | 1160–1300 | 840–1590 | 652 |
| 60..100cm | soc | g/kg | 4.8–10.4 | 1.5–32 | 652 |
| 60..100cm | ph.h2o | pH | 5.7–6.5 | 5–7.7 | 652 |
