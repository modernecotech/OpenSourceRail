# Beirut civil soil screening

1,131 route/station sample locations; 1,127 complete profiles; 4 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 632 |
| coverage-gap | 4 |
| fine-soil-plasticity-and-shrink-swell-tests | 1127 |
| granular-density-and-groundwater-tests | 929 |
| organic-content-and-compressibility-tests | 10 |
| silt-moisture-frost-and-erosion-review | 60 |

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
| 0..30cm | clay | % | 21–31 | 3–45 | 1127 |
| 0..30cm | sand | % | 40–61 | 9–89 | 1127 |
| 0..30cm | silt | % | 18–34 | 1–54 | 1127 |
| 0..30cm | bd.core | kg/m3 | 1180–1400 | 900–1610 | 1127 |
| 0..30cm | soc | g/kg | 4.1–31.5 | 1.4–75 | 1127 |
| 0..30cm | ph.h2o | pH | 6.2–7.7 | 5–8.2 | 1127 |
| 30..60cm | clay | % | 22–32 | 2–51 | 1127 |
| 30..60cm | sand | % | 38–61 | 11–92 | 1127 |
| 30..60cm | silt | % | 16–34 | 0–52 | 1127 |
| 30..60cm | bd.core | kg/m3 | 1330–1510 | 1060–1740 | 1127 |
| 30..60cm | soc | g/kg | 2.3–10.9 | 0.7–36 | 1127 |
| 30..60cm | ph.h2o | pH | 6.2–7.7 | 4.9–8.3 | 1127 |
| 60..100cm | clay | % | 22–33 | 3–54 | 1127 |
| 60..100cm | sand | % | 38–62 | 12–93 | 1127 |
| 60..100cm | silt | % | 15–35 | 0–52 | 1127 |
| 60..100cm | bd.core | kg/m3 | 1360–1550 | 1000–1800 | 1127 |
| 60..100cm | soc | g/kg | 1.5–8.3 | 0.1–33.8 | 1127 |
| 60..100cm | ph.h2o | pH | 6.3–7.7 | 4.9–8.3 | 1127 |
