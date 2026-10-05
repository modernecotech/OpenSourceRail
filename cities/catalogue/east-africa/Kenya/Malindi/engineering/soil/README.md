# Malindi civil soil screening

56 route/station sample locations; 56 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 45 |
| fine-soil-plasticity-and-shrink-swell-tests | 19 |
| granular-density-and-groundwater-tests | 56 |

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
| 0..30cm | clay | % | 10–27 | 3–43 | 56 |
| 0..30cm | sand | % | 48–82 | 14–90 | 56 |
| 0..30cm | silt | % | 8–26 | 0–43 | 56 |
| 0..30cm | bd.core | kg/m3 | 1310–1430 | 1070–1590 | 56 |
| 0..30cm | soc | g/kg | 5.6–13.8 | 2.2–29.9 | 56 |
| 0..30cm | ph.h2o | pH | 6.5–7.1 | 5.6–8.3 | 56 |
| 30..60cm | clay | % | 10–28 | 2–45 | 56 |
| 30..60cm | sand | % | 46–85 | 11–93 | 56 |
| 30..60cm | silt | % | 5–26 | 0–45 | 56 |
| 30..60cm | bd.core | kg/m3 | 1340–1470 | 1060–1660 | 56 |
| 30..60cm | soc | g/kg | 3.7–7.2 | 1.4–14.5 | 56 |
| 30..60cm | ph.h2o | pH | 6.5–7.2 | 5.5–8.5 | 56 |
| 60..100cm | clay | % | 10–29 | 2–47 | 56 |
| 60..100cm | sand | % | 45–84 | 12–94 | 56 |
| 60..100cm | silt | % | 6–26 | 0–46 | 56 |
| 60..100cm | bd.core | kg/m3 | 1330–1490 | 940–1740 | 56 |
| 60..100cm | soc | g/kg | 3–6.7 | 1.2–14.5 | 56 |
| 60..100cm | ph.h2o | pH | 6.6–7.2 | 5.3–8.6 | 56 |
