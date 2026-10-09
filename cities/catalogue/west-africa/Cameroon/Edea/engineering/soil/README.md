# Edea civil soil screening

142 route/station sample locations; 139 complete profiles; 3 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 139 |
| coverage-gap | 3 |
| fine-soil-plasticity-and-shrink-swell-tests | 139 |
| granular-density-and-groundwater-tests | 33 |
| organic-content-and-compressibility-tests | 55 |
| silt-moisture-frost-and-erosion-review | 27 |

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
| 0..30cm | clay | % | 26–33 | 11–45 | 139 |
| 0..30cm | sand | % | 34–47 | 16–74 | 139 |
| 0..30cm | silt | % | 27–33 | 8–48 | 139 |
| 0..30cm | bd.core | kg/m3 | 870–1100 | 430–1380 | 139 |
| 0..30cm | soc | g/kg | 11.2–28.2 | 5.2–63.7 | 139 |
| 0..30cm | ph.h2o | pH | 5.5–5.8 | 4.3–6.9 | 139 |
| 30..60cm | clay | % | 28–35 | 8–48 | 139 |
| 30..60cm | sand | % | 36–46 | 14–75 | 139 |
| 30..60cm | silt | % | 25–32 | 3–51 | 139 |
| 30..60cm | bd.core | kg/m3 | 870–1190 | 420–1500 | 139 |
| 30..60cm | soc | g/kg | 5.2–15.6 | 1.5–31.4 | 139 |
| 30..60cm | ph.h2o | pH | 5.5–5.8 | 4.3–6.9 | 139 |
| 60..100cm | clay | % | 28–36 | 8–49 | 139 |
| 60..100cm | sand | % | 34–45 | 7–78 | 139 |
| 60..100cm | silt | % | 25–32 | 4–53 | 139 |
| 60..100cm | bd.core | kg/m3 | 880–1240 | 280–1530 | 139 |
| 60..100cm | soc | g/kg | 5–17.9 | 2–49.1 | 139 |
| 60..100cm | ph.h2o | pH | 5.6–5.9 | 4.4–7 | 139 |
