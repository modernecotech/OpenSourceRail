# Moshi civil soil screening

973 route/station sample locations; 973 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 9 |
| fine-soil-plasticity-and-shrink-swell-tests | 973 |
| granular-density-and-groundwater-tests | 271 |

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
| 0..30cm | clay | % | 28–46 | 14–58 | 973 |
| 0..30cm | sand | % | 22–51 | 4–85 | 973 |
| 0..30cm | silt | % | 21–34 | 3–48 | 973 |
| 0..30cm | bd.core | kg/m3 | 1120–1370 | 950–1540 | 973 |
| 0..30cm | soc | g/kg | 7.1–20.9 | 3.8–43.3 | 973 |
| 0..30cm | ph.h2o | pH | 6.2–7.3 | 5.2–8.2 | 973 |
| 30..60cm | clay | % | 31–48 | 13–61 | 973 |
| 30..60cm | sand | % | 20–48 | 5–83 | 973 |
| 30..60cm | silt | % | 21–34 | 3–49 | 973 |
| 30..60cm | bd.core | kg/m3 | 1240–1410 | 1070–1580 | 973 |
| 30..60cm | soc | g/kg | 5.1–9.2 | 2.6–17.7 | 973 |
| 30..60cm | ph.h2o | pH | 6.3–7.3 | 5.3–8.2 | 973 |
| 60..100cm | clay | % | 31–48 | 13–62 | 973 |
| 60..100cm | sand | % | 21–49 | 5–81 | 973 |
| 60..100cm | silt | % | 20–33 | 3–49 | 973 |
| 60..100cm | bd.core | kg/m3 | 1280–1380 | 1030–1610 | 973 |
| 60..100cm | soc | g/kg | 4.2–6.9 | 1.8–14.1 | 973 |
| 60..100cm | ph.h2o | pH | 6.4–7.3 | 5.4–8.2 | 973 |
