# Mahalla civil soil screening

87 route/station sample locations; 87 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 24 |
| fine-soil-plasticity-and-shrink-swell-tests | 83 |
| granular-density-and-groundwater-tests | 87 |

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
| 0..30cm | clay | % | 16–24 | 4–39 | 87 |
| 0..30cm | sand | % | 49–67 | 18–90 | 87 |
| 0..30cm | silt | % | 18–27 | 6–43 | 87 |
| 0..30cm | bd.core | kg/m3 | 1180–1450 | 970–1650 | 87 |
| 0..30cm | soc | g/kg | 2.5–15.9 | 1.1–43.1 | 87 |
| 0..30cm | ph.h2o | pH | 7.5–8.4 | 6.5–9.2 | 87 |
| 30..60cm | clay | % | 18–25 | 4–41 | 87 |
| 30..60cm | sand | % | 49–64 | 17–89 | 87 |
| 30..60cm | silt | % | 18–26 | 4–42 | 87 |
| 30..60cm | bd.core | kg/m3 | 1300–1550 | 940–1780 | 87 |
| 30..60cm | soc | g/kg | 1.3–9.2 | 0.1–25.5 | 87 |
| 30..60cm | ph.h2o | pH | 7–8.6 | 4.4–9.5 | 87 |
| 60..100cm | clay | % | 18–25 | 4–40 | 87 |
| 60..100cm | sand | % | 49–63 | 17–88 | 87 |
| 60..100cm | silt | % | 18–26 | 4–41 | 87 |
| 60..100cm | bd.core | kg/m3 | 1340–1570 | 1030–1930 | 87 |
| 60..100cm | soc | g/kg | 1.1–8.5 | 0.2–26.1 | 87 |
| 60..100cm | ph.h2o | pH | 6.7–8.5 | 3.3–9.5 | 87 |
