# Niamey civil soil screening

488 route/station sample locations; 481 complete profiles; 7 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 469 |
| coverage-gap | 7 |
| fine-soil-plasticity-and-shrink-swell-tests | 52 |
| granular-density-and-groundwater-tests | 481 |

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
| 0..30cm | clay | % | 8–28 | 3–42 | 481 |
| 0..30cm | sand | % | 43–81 | 14–92 | 481 |
| 0..30cm | silt | % | 10–30 | 2–45 | 481 |
| 0..30cm | bd.core | kg/m3 | 1390–1510 | 1150–1720 | 481 |
| 0..30cm | soc | g/kg | 2.3–6.7 | 0.7–14.9 | 481 |
| 0..30cm | ph.h2o | pH | 5.7–7.7 | 4.9–8.5 | 481 |
| 30..60cm | clay | % | 9–27 | 3–42 | 481 |
| 30..60cm | sand | % | 44–82 | 10–93 | 481 |
| 30..60cm | silt | % | 9–28 | 1–46 | 481 |
| 30..60cm | bd.core | kg/m3 | 1370–1500 | 1090–1730 | 481 |
| 30..60cm | soc | g/kg | 2–3.3 | 0.5–8 | 481 |
| 30..60cm | ph.h2o | pH | 5.5–8 | 4.5–8.7 | 481 |
| 60..100cm | clay | % | 9–28 | 3–43 | 481 |
| 60..100cm | sand | % | 44–83 | 9–93 | 481 |
| 60..100cm | silt | % | 8–29 | 1–48 | 481 |
| 60..100cm | bd.core | kg/m3 | 1330–1500 | 890–1760 | 481 |
| 60..100cm | soc | g/kg | 1.7–3 | 0.4–7.9 | 481 |
| 60..100cm | ph.h2o | pH | 5.5–8.1 | 4.5–9.1 | 481 |
