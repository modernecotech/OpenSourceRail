# Zarqa civil soil screening

121 route/station sample locations; 98 complete profiles; 23 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 23 |
| fine-soil-plasticity-and-shrink-swell-tests | 95 |
| granular-density-and-groundwater-tests | 93 |

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
| 0..30cm | clay | % | 18–27 | 4–43 | 98 |
| 0..30cm | sand | % | 44–56 | 14–80 | 98 |
| 0..30cm | silt | % | 24–32 | 8–47 | 98 |
| 0..30cm | bd.core | kg/m3 | 1360–1460 | 1220–1640 | 98 |
| 0..30cm | soc | g/kg | 2.4–9.1 | 0.9–17.5 | 98 |
| 0..30cm | ph.h2o | pH | 7.5–8.2 | 6.9–8.8 | 98 |
| 30..60cm | clay | % | 19–28 | 4–45 | 98 |
| 30..60cm | sand | % | 43–57 | 13–89 | 98 |
| 30..60cm | silt | % | 22–30 | 5–47 | 98 |
| 30..60cm | bd.core | kg/m3 | 1450–1530 | 1270–1730 | 98 |
| 30..60cm | soc | g/kg | 1.5–4.6 | 0.2–9.5 | 98 |
| 30..60cm | ph.h2o | pH | 7.4–8.5 | 6.6–9.5 | 98 |
| 60..100cm | clay | % | 19–29 | 4–46 | 98 |
| 60..100cm | sand | % | 42–57 | 9–90 | 98 |
| 60..100cm | silt | % | 22–31 | 3–48 | 98 |
| 60..100cm | bd.core | kg/m3 | 1480–1560 | 1280–1750 | 98 |
| 60..100cm | soc | g/kg | 1.2–2.9 | 0.1–6.1 | 98 |
| 60..100cm | ph.h2o | pH | 7.5–8.7 | 6.5–9.5 | 98 |
