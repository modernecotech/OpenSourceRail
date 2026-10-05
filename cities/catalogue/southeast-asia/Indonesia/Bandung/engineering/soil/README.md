# Bandung civil soil screening

967 route/station sample locations; 967 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 967 |
| fine-soil-plasticity-and-shrink-swell-tests | 967 |
| granular-density-and-groundwater-tests | 122 |
| organic-content-and-compressibility-tests | 92 |
| silt-moisture-frost-and-erosion-review | 322 |

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
| 0..30cm | clay | % | 24–36 | 8–49 | 967 |
| 0..30cm | sand | % | 30–51 | 7–85 | 967 |
| 0..30cm | silt | % | 22–39 | 1–56 | 967 |
| 0..30cm | bd.core | kg/m3 | 740–1360 | 310–1570 | 967 |
| 0..30cm | soc | g/kg | 7.9–45.6 | 2.1–102 | 967 |
| 0..30cm | ph.h2o | pH | 5–5.8 | 3.9–6.8 | 967 |
| 30..60cm | clay | % | 28–42 | 7–57 | 967 |
| 30..60cm | sand | % | 28–53 | 4–88 | 967 |
| 30..60cm | silt | % | 19–34 | 0–55 | 967 |
| 30..60cm | bd.core | kg/m3 | 810–1410 | 470–1660 | 967 |
| 30..60cm | soc | g/kg | 4.6–25.6 | 1–75.8 | 967 |
| 30..60cm | ph.h2o | pH | 5.2–5.9 | 4.2–6.9 | 967 |
| 60..100cm | clay | % | 27–45 | 7–61 | 967 |
| 60..100cm | sand | % | 25–53 | 2–87 | 967 |
| 60..100cm | silt | % | 20–35 | 0–54 | 967 |
| 60..100cm | bd.core | kg/m3 | 870–1460 | 330–1700 | 967 |
| 60..100cm | soc | g/kg | 4.6–28.5 | 0.4–135.1 | 967 |
| 60..100cm | ph.h2o | pH | 5.3–5.9 | 4.2–7.3 | 967 |
