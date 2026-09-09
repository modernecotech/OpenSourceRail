# Xai-Xai civil soil screening

54 route/station sample locations; 54 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 52 |
| fine-soil-plasticity-and-shrink-swell-tests | 54 |
| granular-density-and-groundwater-tests | 54 |
| organic-content-and-compressibility-tests | 1 |

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
| 0..30cm | clay | % | 22–29 | 7–44 | 54 |
| 0..30cm | sand | % | 50–64 | 22–91 | 54 |
| 0..30cm | silt | % | 14–21 | 0–36 | 54 |
| 0..30cm | bd.core | kg/m3 | 1190–1340 | 950–1550 | 54 |
| 0..30cm | soc | g/kg | 6.9–23.2 | 3.7–65 | 54 |
| 0..30cm | ph.h2o | pH | 6–6.5 | 5–8.1 | 54 |
| 30..60cm | clay | % | 24–32 | 6–49 | 54 |
| 30..60cm | sand | % | 48–63 | 16–94 | 54 |
| 30..60cm | silt | % | 12–20 | 0–36 | 54 |
| 30..60cm | bd.core | kg/m3 | 1270–1470 | 1050–1630 | 54 |
| 30..60cm | soc | g/kg | 3.8–10.5 | 2.1–19.9 | 54 |
| 30..60cm | ph.h2o | pH | 6.2–6.6 | 5.1–7.9 | 54 |
| 60..100cm | clay | % | 25–33 | 7–52 | 54 |
| 60..100cm | sand | % | 47–64 | 12–93 | 54 |
| 60..100cm | silt | % | 10–20 | 0–36 | 54 |
| 60..100cm | bd.core | kg/m3 | 1220–1510 | 820–1700 | 54 |
| 60..100cm | soc | g/kg | 3.1–5.3 | 1.4–12.1 | 54 |
| 60..100cm | ph.h2o | pH | 6.6–7 | 5–8.4 | 54 |
