# Sidon civil soil screening

86 route/station sample locations; 86 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 9 |
| fine-soil-plasticity-and-shrink-swell-tests | 86 |
| granular-density-and-groundwater-tests | 67 |
| silt-moisture-frost-and-erosion-review | 3 |

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
| 0..30cm | clay | % | 19–33 | 4–47 | 86 |
| 0..30cm | sand | % | 35–62 | 14–86 | 86 |
| 0..30cm | silt | % | 19–32 | 3–50 | 86 |
| 0..30cm | bd.core | kg/m3 | 1230–1390 | 950–1600 | 86 |
| 0..30cm | soc | g/kg | 4.6–13.8 | 1.4–27 | 86 |
| 0..30cm | ph.h2o | pH | 6.5–7.6 | 5.3–8.2 | 86 |
| 30..60cm | clay | % | 21–34 | 2–49 | 86 |
| 30..60cm | sand | % | 35–62 | 11–91 | 86 |
| 30..60cm | silt | % | 17–32 | 0–50 | 86 |
| 30..60cm | bd.core | kg/m3 | 1310–1510 | 1020–1720 | 86 |
| 30..60cm | soc | g/kg | 2.7–7.1 | 1–13.3 | 86 |
| 30..60cm | ph.h2o | pH | 6.5–7.6 | 5.5–8.2 | 86 |
| 60..100cm | clay | % | 21–34 | 3–48 | 86 |
| 60..100cm | sand | % | 36–62 | 11–92 | 86 |
| 60..100cm | silt | % | 17–31 | 0–52 | 86 |
| 60..100cm | bd.core | kg/m3 | 1320–1550 | 1010–1740 | 86 |
| 60..100cm | soc | g/kg | 1.6–6.4 | 0.1–15.2 | 86 |
| 60..100cm | ph.h2o | pH | 6.6–7.5 | 5.2–8.2 | 86 |
