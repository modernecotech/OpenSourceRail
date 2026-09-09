# Patna civil soil screening

394 route/station sample locations; 383 complete profiles; 11 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 123 |
| coverage-gap | 11 |
| fine-soil-plasticity-and-shrink-swell-tests | 361 |
| granular-density-and-groundwater-tests | 382 |

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
| 0..30cm | clay | % | 17–26 | 0–40 | 383 |
| 0..30cm | sand | % | 44–63 | 14–97 | 383 |
| 0..30cm | silt | % | 20–31 | 0–47 | 383 |
| 0..30cm | bd.core | kg/m3 | 1290–1500 | 1010–1710 | 383 |
| 0..30cm | soc | g/kg | 4–11.2 | 1.6–22.9 | 383 |
| 0..30cm | ph.h2o | pH | 6.3–6.9 | 5.2–8.1 | 383 |
| 30..60cm | clay | % | 18–28 | 1–43 | 383 |
| 30..60cm | sand | % | 40–61 | 12–94 | 383 |
| 30..60cm | silt | % | 20–31 | 1–49 | 383 |
| 30..60cm | bd.core | kg/m3 | 1380–1560 | 1090–1770 | 383 |
| 30..60cm | soc | g/kg | 2.3–5.3 | 0.4–12.8 | 383 |
| 30..60cm | ph.h2o | pH | 6.4–7.1 | 5.3–8.2 | 383 |
| 60..100cm | clay | % | 19–29 | 1–44 | 383 |
| 60..100cm | sand | % | 38–60 | 11–95 | 383 |
| 60..100cm | silt | % | 21–32 | 0–49 | 383 |
| 60..100cm | bd.core | kg/m3 | 1460–1610 | 1080–1880 | 383 |
| 60..100cm | soc | g/kg | 1.8–5 | 0.3–11.7 | 383 |
| 60..100cm | ph.h2o | pH | 6.6–7.3 | 5.3–8.5 | 383 |
