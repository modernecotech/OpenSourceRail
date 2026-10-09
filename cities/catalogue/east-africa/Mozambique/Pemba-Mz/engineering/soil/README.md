# Pemba-Mz civil soil screening

528 route/station sample locations; 508 complete profiles; 20 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 8 |
| coverage-gap | 20 |
| fine-soil-plasticity-and-shrink-swell-tests | 508 |
| granular-density-and-groundwater-tests | 508 |

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
| 0..30cm | clay | % | 19–29 | 4–43 | 508 |
| 0..30cm | sand | % | 54–73 | 28–95 | 508 |
| 0..30cm | silt | % | 8–17 | 0–33 | 508 |
| 0..30cm | bd.core | kg/m3 | 1290–1470 | 1060–1620 | 508 |
| 0..30cm | soc | g/kg | 5.4–11.2 | 2–22 | 508 |
| 0..30cm | ph.h2o | pH | 6.3–6.8 | 5.3–8.1 | 508 |
| 30..60cm | clay | % | 21–32 | 4–48 | 508 |
| 30..60cm | sand | % | 51–72 | 23–95 | 508 |
| 30..60cm | silt | % | 7–17 | 0–35 | 508 |
| 30..60cm | bd.core | kg/m3 | 1280–1540 | 1020–1730 | 508 |
| 30..60cm | soc | g/kg | 3.6–6.5 | 1.3–14.2 | 508 |
| 30..60cm | ph.h2o | pH | 6.5–6.9 | 5.5–7.9 | 508 |
| 60..100cm | clay | % | 22–33 | 4–49 | 508 |
| 60..100cm | sand | % | 49–71 | 23–95 | 508 |
| 60..100cm | silt | % | 7–18 | 0–37 | 508 |
| 60..100cm | bd.core | kg/m3 | 1230–1550 | 810–1770 | 508 |
| 60..100cm | soc | g/kg | 2.6–4.9 | 1.2–10 | 508 |
| 60..100cm | ph.h2o | pH | 6.8–7.4 | 5.1–8.6 | 508 |
