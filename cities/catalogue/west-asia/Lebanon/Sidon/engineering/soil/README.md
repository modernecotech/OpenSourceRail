# Sidon civil soil screening

64 route/station sample locations; 64 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 6 |
| fine-soil-plasticity-and-shrink-swell-tests | 64 |
| granular-density-and-groundwater-tests | 46 |
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
| 0..30cm | clay | % | 23–34 | 7–46 | 64 |
| 0..30cm | sand | % | 34–56 | 15–84 | 64 |
| 0..30cm | silt | % | 21–32 | 4–50 | 64 |
| 0..30cm | bd.core | kg/m3 | 1210–1390 | 920–1580 | 64 |
| 0..30cm | soc | g/kg | 4.5–14.5 | 1.3–34 | 64 |
| 0..30cm | ph.h2o | pH | 6.5–7.7 | 5.3–8.2 | 64 |
| 30..60cm | clay | % | 23–37 | 4–50 | 64 |
| 30..60cm | sand | % | 34–59 | 10–88 | 64 |
| 30..60cm | silt | % | 18–30 | 1–50 | 64 |
| 30..60cm | bd.core | kg/m3 | 1310–1510 | 1120–1690 | 64 |
| 30..60cm | soc | g/kg | 2.6–7.1 | 1–13.8 | 64 |
| 30..60cm | ph.h2o | pH | 6.6–7.6 | 5.5–8.3 | 64 |
| 60..100cm | clay | % | 23–37 | 4–49 | 64 |
| 60..100cm | sand | % | 35–60 | 10–88 | 64 |
| 60..100cm | silt | % | 17–30 | 0–49 | 64 |
| 60..100cm | bd.core | kg/m3 | 1310–1550 | 1040–1740 | 64 |
| 60..100cm | soc | g/kg | 1.7–6.3 | 0.4–16.9 | 64 |
| 60..100cm | ph.h2o | pH | 6.6–7.6 | 5.5–8.4 | 64 |
