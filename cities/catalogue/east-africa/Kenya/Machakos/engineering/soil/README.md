# Machakos civil soil screening

248 route/station sample locations; 248 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 176 |
| fine-soil-plasticity-and-shrink-swell-tests | 248 |
| granular-density-and-groundwater-tests | 42 |
| organic-content-and-compressibility-tests | 6 |
| silt-moisture-frost-and-erosion-review | 6 |

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
| 0..30cm | clay | % | 28–37 | 16–49 | 248 |
| 0..30cm | sand | % | 32–47 | 12–76 | 248 |
| 0..30cm | silt | % | 24–33 | 9–45 | 248 |
| 0..30cm | bd.core | kg/m3 | 1110–1360 | 910–1520 | 248 |
| 0..30cm | soc | g/kg | 7.5–25.5 | 3.9–57.9 | 248 |
| 0..30cm | ph.h2o | pH | 5.4–7.3 | 4.7–8.2 | 248 |
| 30..60cm | clay | % | 26–39 | 14–50 | 248 |
| 30..60cm | sand | % | 27–48 | 8–75 | 248 |
| 30..60cm | silt | % | 24–37 | 6–48 | 248 |
| 30..60cm | bd.core | kg/m3 | 1120–1350 | 950–1530 | 248 |
| 30..60cm | soc | g/kg | 5.6–16.6 | 2.9–65.3 | 248 |
| 30..60cm | ph.h2o | pH | 5.6–7.4 | 4.7–8.2 | 248 |
| 60..100cm | clay | % | 25–39 | 11–52 | 248 |
| 60..100cm | sand | % | 26–50 | 8–78 | 248 |
| 60..100cm | silt | % | 24–38 | 6–50 | 248 |
| 60..100cm | bd.core | kg/m3 | 1100–1360 | 790–1600 | 248 |
| 60..100cm | soc | g/kg | 4.8–13.2 | 2.2–50.8 | 248 |
| 60..100cm | ph.h2o | pH | 5.8–7.4 | 4.5–8.2 | 248 |
