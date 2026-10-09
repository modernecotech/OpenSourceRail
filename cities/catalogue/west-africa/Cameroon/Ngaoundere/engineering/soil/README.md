# Ngaoundere civil soil screening

409 route/station sample locations; 409 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 409 |
| fine-soil-plasticity-and-shrink-swell-tests | 409 |
| granular-density-and-groundwater-tests | 407 |
| silt-moisture-frost-and-erosion-review | 9 |

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
| 0..30cm | clay | % | 20–27 | 6–41 | 409 |
| 0..30cm | sand | % | 44–59 | 13–81 | 409 |
| 0..30cm | silt | % | 19–29 | 2–50 | 409 |
| 0..30cm | bd.core | kg/m3 | 1240–1420 | 1010–1600 | 409 |
| 0..30cm | soc | g/kg | 6.9–16 | 2.6–29 | 409 |
| 0..30cm | ph.h2o | pH | 5.6–6 | 4.7–6.6 | 409 |
| 30..60cm | clay | % | 22–30 | 7–47 | 409 |
| 30..60cm | sand | % | 42–56 | 11–84 | 409 |
| 30..60cm | silt | % | 20–29 | 0–47 | 409 |
| 30..60cm | bd.core | kg/m3 | 1310–1450 | 1100–1650 | 409 |
| 30..60cm | soc | g/kg | 4–8 | 1.5–15.5 | 409 |
| 30..60cm | ph.h2o | pH | 5.6–6 | 4.8–6.6 | 409 |
| 60..100cm | clay | % | 23–30 | 7–48 | 409 |
| 60..100cm | sand | % | 42–56 | 13–86 | 409 |
| 60..100cm | silt | % | 20–28 | 0–48 | 409 |
| 60..100cm | bd.core | kg/m3 | 1360–1490 | 1070–1700 | 409 |
| 60..100cm | soc | g/kg | 4.1–5.8 | 1.8–12.5 | 409 |
| 60..100cm | ph.h2o | pH | 5.6–6 | 4.8–6.6 | 409 |
