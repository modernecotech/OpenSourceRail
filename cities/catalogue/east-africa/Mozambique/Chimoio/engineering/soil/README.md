# Chimoio civil soil screening

98 route/station sample locations; 98 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 98 |
| fine-soil-plasticity-and-shrink-swell-tests | 98 |
| granular-density-and-groundwater-tests | 98 |

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
| 0..30cm | clay | % | 25–31 | 10–43 | 98 |
| 0..30cm | sand | % | 53–66 | 32–88 | 98 |
| 0..30cm | silt | % | 9–16 | 0–28 | 98 |
| 0..30cm | bd.core | kg/m3 | 1210–1320 | 1030–1480 | 98 |
| 0..30cm | soc | g/kg | 7.5–17.4 | 4.4–30.5 | 98 |
| 0..30cm | ph.h2o | pH | 5.6–6.3 | 4.8–7.3 | 98 |
| 30..60cm | clay | % | 28–36 | 12–50 | 98 |
| 30..60cm | sand | % | 48–65 | 25–88 | 98 |
| 30..60cm | silt | % | 8–16 | 0–30 | 98 |
| 30..60cm | bd.core | kg/m3 | 1250–1360 | 1040–1500 | 98 |
| 30..60cm | soc | g/kg | 5.3–7.5 | 2.5–12.5 | 98 |
| 30..60cm | ph.h2o | pH | 5.7–6.4 | 4.9–7.2 | 98 |
| 60..100cm | clay | % | 29–37 | 11–51 | 98 |
| 60..100cm | sand | % | 45–62 | 16–88 | 98 |
| 60..100cm | silt | % | 9–18 | 0–35 | 98 |
| 60..100cm | bd.core | kg/m3 | 1180–1390 | 910–1580 | 98 |
| 60..100cm | soc | g/kg | 3.1–5.2 | 1.3–8.8 | 98 |
| 60..100cm | ph.h2o | pH | 5.8–6.5 | 4.8–7.5 | 98 |
