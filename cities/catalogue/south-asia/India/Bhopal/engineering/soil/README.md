# Bhopal civil soil screening

363 route/station sample locations; 360 complete profiles; 3 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 357 |
| coverage-gap | 3 |
| fine-soil-plasticity-and-shrink-swell-tests | 339 |
| granular-density-and-groundwater-tests | 360 |

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
| 0..30cm | clay | % | 19–28 | 4–40 | 360 |
| 0..30cm | sand | % | 44–60 | 16–87 | 360 |
| 0..30cm | silt | % | 21–29 | 4–46 | 360 |
| 0..30cm | bd.core | kg/m3 | 1160–1460 | 810–1670 | 360 |
| 0..30cm | soc | g/kg | 4.4–8.3 | 1.4–21.8 | 360 |
| 0..30cm | ph.h2o | pH | 6.1–6.8 | 5–8.1 | 360 |
| 30..60cm | clay | % | 20–29 | 5–44 | 360 |
| 30..60cm | sand | % | 45–59 | 15–88 | 360 |
| 30..60cm | silt | % | 19–27 | 0–49 | 360 |
| 30..60cm | bd.core | kg/m3 | 1260–1520 | 940–1720 | 360 |
| 30..60cm | soc | g/kg | 2.4–4.7 | 0.7–12.6 | 360 |
| 30..60cm | ph.h2o | pH | 6.2–6.9 | 5.2–8.2 | 360 |
| 60..100cm | clay | % | 21–30 | 5–44 | 360 |
| 60..100cm | sand | % | 45–60 | 12–90 | 360 |
| 60..100cm | silt | % | 19–25 | 0–49 | 360 |
| 60..100cm | bd.core | kg/m3 | 1390–1610 | 1000–1870 | 360 |
| 60..100cm | soc | g/kg | 1.8–3.8 | 0.4–8.1 | 360 |
| 60..100cm | ph.h2o | pH | 6.3–7 | 5–8.4 | 360 |
