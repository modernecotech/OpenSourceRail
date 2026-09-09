# Bandung civil soil screening

1,016 route/station sample locations; 1,016 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1016 |
| fine-soil-plasticity-and-shrink-swell-tests | 1016 |
| granular-density-and-groundwater-tests | 125 |
| organic-content-and-compressibility-tests | 70 |
| silt-moisture-frost-and-erosion-review | 374 |

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
| 0..30cm | clay | % | 26–37 | 10–49 | 1016 |
| 0..30cm | sand | % | 30–51 | 4–86 | 1016 |
| 0..30cm | silt | % | 22–38 | 1–56 | 1016 |
| 0..30cm | bd.core | kg/m3 | 740–1330 | 310–1530 | 1016 |
| 0..30cm | soc | g/kg | 7.9–45.4 | 2.6–100.9 | 1016 |
| 0..30cm | ph.h2o | pH | 5–5.8 | 3.9–6.8 | 1016 |
| 30..60cm | clay | % | 28–42 | 7–57 | 1016 |
| 30..60cm | sand | % | 28–53 | 3–88 | 1016 |
| 30..60cm | silt | % | 19–34 | 0–55 | 1016 |
| 30..60cm | bd.core | kg/m3 | 810–1380 | 470–1660 | 1016 |
| 30..60cm | soc | g/kg | 4.6–25.6 | 1–75.8 | 1016 |
| 30..60cm | ph.h2o | pH | 5.3–5.9 | 4.2–6.9 | 1016 |
| 60..100cm | clay | % | 27–44 | 7–61 | 1016 |
| 60..100cm | sand | % | 25–53 | 2–87 | 1016 |
| 60..100cm | silt | % | 20–35 | 0–53 | 1016 |
| 60..100cm | bd.core | kg/m3 | 870–1430 | 330–1700 | 1016 |
| 60..100cm | soc | g/kg | 4.6–28.5 | 0.4–121.5 | 1016 |
| 60..100cm | ph.h2o | pH | 5.3–5.9 | 4.2–7.2 | 1016 |
