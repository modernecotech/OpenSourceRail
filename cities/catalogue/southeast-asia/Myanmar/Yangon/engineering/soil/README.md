# Yangon civil soil screening

852 route/station sample locations; 811 complete profiles; 41 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 811 |
| coverage-gap | 41 |
| fine-soil-plasticity-and-shrink-swell-tests | 811 |
| granular-density-and-groundwater-tests | 800 |
| organic-content-and-compressibility-tests | 8 |
| silt-moisture-frost-and-erosion-review | 34 |

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
| 0..30cm | clay | % | 23–32 | 4–51 | 811 |
| 0..30cm | sand | % | 38–56 | 8–88 | 811 |
| 0..30cm | silt | % | 19–31 | 0–51 | 811 |
| 0..30cm | bd.core | kg/m3 | 880–1290 | 570–1590 | 811 |
| 0..30cm | soc | g/kg | 7.4–20.1 | 2.5–52.2 | 811 |
| 0..30cm | ph.h2o | pH | 5.5–6.6 | 4.4–7.8 | 811 |
| 30..60cm | clay | % | 22–32 | 5–51 | 811 |
| 30..60cm | sand | % | 37–57 | 8–89 | 811 |
| 30..60cm | silt | % | 21–32 | 0–51 | 811 |
| 30..60cm | bd.core | kg/m3 | 980–1370 | 510–1730 | 811 |
| 30..60cm | soc | g/kg | 4.2–15.9 | 1–61.2 | 811 |
| 30..60cm | ph.h2o | pH | 5.6–6.9 | 4.7–8.1 | 811 |
| 60..100cm | clay | % | 22–32 | 5–51 | 811 |
| 60..100cm | sand | % | 38–59 | 8–89 | 811 |
| 60..100cm | silt | % | 20–31 | 0–52 | 811 |
| 60..100cm | bd.core | kg/m3 | 990–1390 | 540–1790 | 811 |
| 60..100cm | soc | g/kg | 2.4–12.7 | 0.6–53.1 | 811 |
| 60..100cm | ph.h2o | pH | 5.7–7.1 | 4.6–8.3 | 811 |
