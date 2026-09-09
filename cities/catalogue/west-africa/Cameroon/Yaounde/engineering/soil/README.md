# Yaounde civil soil screening

854 route/station sample locations; 854 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 854 |
| fine-soil-plasticity-and-shrink-swell-tests | 523 |
| granular-density-and-groundwater-tests | 808 |
| organic-content-and-compressibility-tests | 11 |

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
| 0..30cm | clay | % | 20–30 | 10–43 | 854 |
| 0..30cm | sand | % | 43–60 | 20–80 | 854 |
| 0..30cm | silt | % | 17–27 | 4–44 | 854 |
| 0..30cm | bd.core | kg/m3 | 1080–1290 | 810–1500 | 854 |
| 0..30cm | soc | g/kg | 7.9–28.6 | 2.7–69.2 | 854 |
| 0..30cm | ph.h2o | pH | 5.1–6.3 | 3.9–7.9 | 854 |
| 30..60cm | clay | % | 21–34 | 11–46 | 854 |
| 30..60cm | sand | % | 40–63 | 12–82 | 854 |
| 30..60cm | silt | % | 15–28 | 1–46 | 854 |
| 30..60cm | bd.core | kg/m3 | 1110–1310 | 800–1580 | 854 |
| 30..60cm | soc | g/kg | 4.3–11.2 | 1.8–21.3 | 854 |
| 30..60cm | ph.h2o | pH | 5.1–6.3 | 3.9–7.9 | 854 |
| 60..100cm | clay | % | 21–36 | 10–49 | 854 |
| 60..100cm | sand | % | 38–64 | 9–82 | 854 |
| 60..100cm | silt | % | 15–30 | 0–48 | 854 |
| 60..100cm | bd.core | kg/m3 | 1080–1320 | 680–1600 | 854 |
| 60..100cm | soc | g/kg | 3.7–7.3 | 1.5–22.4 | 854 |
| 60..100cm | ph.h2o | pH | 5.2–6.4 | 3.9–8 | 854 |
