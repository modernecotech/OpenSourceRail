# Damascus civil soil screening

430 route/station sample locations; 427 complete profiles; 3 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 3 |
| fine-soil-plasticity-and-shrink-swell-tests | 426 |
| granular-density-and-groundwater-tests | 326 |
| silt-moisture-frost-and-erosion-review | 10 |

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
| 0..30cm | clay | % | 19–29 | 5–42 | 427 |
| 0..30cm | sand | % | 38–57 | 11–85 | 427 |
| 0..30cm | silt | % | 24–36 | 7–51 | 427 |
| 0..30cm | bd.core | kg/m3 | 1350–1460 | 1180–1640 | 427 |
| 0..30cm | soc | g/kg | 2.4–9.7 | 0.9–25 | 427 |
| 0..30cm | ph.h2o | pH | 7.6–8 | 7.1–8.6 | 427 |
| 30..60cm | clay | % | 22–31 | 7–47 | 427 |
| 30..60cm | sand | % | 37–55 | 10–84 | 427 |
| 30..60cm | silt | % | 24–33 | 5–49 | 427 |
| 30..60cm | bd.core | kg/m3 | 1410–1550 | 1250–1730 | 427 |
| 30..60cm | soc | g/kg | 1.7–5.2 | 0.5–10.2 | 427 |
| 30..60cm | ph.h2o | pH | 7.5–8.3 | 6.6–9.4 | 427 |
| 60..100cm | clay | % | 22–32 | 6–48 | 427 |
| 60..100cm | sand | % | 37–56 | 9–85 | 427 |
| 60..100cm | silt | % | 22–33 | 2–50 | 427 |
| 60..100cm | bd.core | kg/m3 | 1420–1580 | 1210–1840 | 427 |
| 60..100cm | soc | g/kg | 1.4–4.1 | 0.4–11.4 | 427 |
| 60..100cm | ph.h2o | pH | 7.4–8.3 | 6.5–9.5 | 427 |
