# Lusaka civil soil screening

658 route/station sample locations; 658 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 655 |
| fine-soil-plasticity-and-shrink-swell-tests | 658 |
| granular-density-and-groundwater-tests | 651 |
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
| 0..30cm | clay | % | 22–34 | 11–46 | 658 |
| 0..30cm | sand | % | 45–60 | 23–84 | 658 |
| 0..30cm | silt | % | 15–23 | 1–40 | 658 |
| 0..30cm | bd.core | kg/m3 | 1290–1450 | 1090–1600 | 658 |
| 0..30cm | soc | g/kg | 4.5–15 | 1.7–29.1 | 658 |
| 0..30cm | ph.h2o | pH | 5.9–6.5 | 4.9–7.5 | 658 |
| 30..60cm | clay | % | 26–36 | 10–48 | 658 |
| 30..60cm | sand | % | 39–55 | 14–81 | 658 |
| 30..60cm | silt | % | 17–27 | 0–48 | 658 |
| 30..60cm | bd.core | kg/m3 | 1320–1480 | 1090–1670 | 658 |
| 30..60cm | soc | g/kg | 3–5.8 | 1.1–9.5 | 658 |
| 30..60cm | ph.h2o | pH | 5.9–6.7 | 5.2–7.7 | 658 |
| 60..100cm | clay | % | 26–36 | 8–51 | 658 |
| 60..100cm | sand | % | 38–57 | 11–84 | 658 |
| 60..100cm | silt | % | 16–28 | 0–50 | 658 |
| 60..100cm | bd.core | kg/m3 | 1320–1530 | 750–1730 | 658 |
| 60..100cm | soc | g/kg | 3–5 | 0.8–9.5 | 658 |
| 60..100cm | ph.h2o | pH | 6–6.9 | 5.2–8.3 | 658 |
