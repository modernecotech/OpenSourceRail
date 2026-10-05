# Yaounde civil soil screening

660 route/station sample locations; 660 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 660 |
| fine-soil-plasticity-and-shrink-swell-tests | 568 |
| granular-density-and-groundwater-tests | 582 |
| organic-content-and-compressibility-tests | 19 |

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
| 0..30cm | clay | % | 20–30 | 9–42 | 660 |
| 0..30cm | sand | % | 45–61 | 20–80 | 660 |
| 0..30cm | silt | % | 17–27 | 1–44 | 660 |
| 0..30cm | bd.core | kg/m3 | 1040–1340 | 800–1530 | 660 |
| 0..30cm | soc | g/kg | 8.3–30.6 | 2.8–69.2 | 660 |
| 0..30cm | ph.h2o | pH | 5.1–6.2 | 3.9–7.9 | 660 |
| 30..60cm | clay | % | 21–34 | 10–47 | 660 |
| 30..60cm | sand | % | 40–64 | 15–81 | 660 |
| 30..60cm | silt | % | 15–28 | 0–46 | 660 |
| 30..60cm | bd.core | kg/m3 | 1090–1380 | 800–1600 | 660 |
| 30..60cm | soc | g/kg | 4.1–12.3 | 1.6–24.7 | 660 |
| 30..60cm | ph.h2o | pH | 5.1–6.2 | 3.9–7.9 | 660 |
| 60..100cm | clay | % | 21–37 | 10–50 | 660 |
| 60..100cm | sand | % | 36–64 | 6–82 | 660 |
| 60..100cm | silt | % | 15–30 | 0–48 | 660 |
| 60..100cm | bd.core | kg/m3 | 1080–1420 | 770–1640 | 660 |
| 60..100cm | soc | g/kg | 3.5–7.3 | 1.5–20.9 | 660 |
| 60..100cm | ph.h2o | pH | 5.2–6.3 | 3.9–8 | 660 |
