# Tangier civil soil screening

286 route/station sample locations; 271 complete profiles; 15 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 24 |
| coverage-gap | 15 |
| fine-soil-plasticity-and-shrink-swell-tests | 211 |
| granular-density-and-groundwater-tests | 255 |
| organic-content-and-compressibility-tests | 1 |
| silt-moisture-frost-and-erosion-review | 1 |

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
| 0..30cm | clay | % | 16–31 | 3–43 | 271 |
| 0..30cm | sand | % | 34–64 | 7–93 | 271 |
| 0..30cm | silt | % | 20–35 | 4–50 | 271 |
| 0..30cm | bd.core | kg/m3 | 1090–1440 | 890–1610 | 271 |
| 0..30cm | soc | g/kg | 4.3–19.1 | 1.9–52.2 | 271 |
| 0..30cm | ph.h2o | pH | 6.4–7.9 | 5.3–8.3 | 271 |
| 30..60cm | clay | % | 17–31 | 1–44 | 271 |
| 30..60cm | sand | % | 35–64 | 7–94 | 271 |
| 30..60cm | silt | % | 19–34 | 0–48 | 271 |
| 30..60cm | bd.core | kg/m3 | 1280–1590 | 1100–1730 | 271 |
| 30..60cm | soc | g/kg | 2.9–7.1 | 1.2–18.3 | 271 |
| 30..60cm | ph.h2o | pH | 6.4–7.9 | 5.1–8.5 | 271 |
| 60..100cm | clay | % | 18–31 | 1–44 | 271 |
| 60..100cm | sand | % | 35–63 | 11–93 | 271 |
| 60..100cm | silt | % | 18–34 | 0–49 | 271 |
| 60..100cm | bd.core | kg/m3 | 1380–1620 | 1060–1800 | 271 |
| 60..100cm | soc | g/kg | 1.9–5.9 | 0.5–25.7 | 271 |
| 60..100cm | ph.h2o | pH | 6.3–7.9 | 5.2–8.6 | 271 |
