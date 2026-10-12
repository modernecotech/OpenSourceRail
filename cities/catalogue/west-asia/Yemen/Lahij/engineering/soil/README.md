# Lahij civil soil screening

342 route/station sample locations; 303 complete profiles; 39 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 39 |
| fine-soil-plasticity-and-shrink-swell-tests | 3 |
| granular-density-and-groundwater-tests | 303 |

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
| 0..30cm | clay | % | 10–20 | 0–32 | 303 |
| 0..30cm | sand | % | 58–77 | 33–92 | 303 |
| 0..30cm | silt | % | 13–22 | 5–36 | 303 |
| 0..30cm | bd.core | kg/m3 | 1440–1500 | 1260–1680 | 303 |
| 0..30cm | soc | g/kg | 2.2–4 | 0.6–8.6 | 303 |
| 0..30cm | ph.h2o | pH | 8–8.6 | 7.1–9.4 | 303 |
| 30..60cm | clay | % | 11–21 | 1–37 | 303 |
| 30..60cm | sand | % | 56–75 | 23–96 | 303 |
| 30..60cm | silt | % | 13–23 | 2–40 | 303 |
| 30..60cm | bd.core | kg/m3 | 1490–1560 | 1320–1770 | 303 |
| 30..60cm | soc | g/kg | 1.3–2.6 | 0–5.9 | 303 |
| 30..60cm | ph.h2o | pH | 8.4–8.7 | 7.9–9.3 | 303 |
| 60..100cm | clay | % | 11–21 | 0–37 | 303 |
| 60..100cm | sand | % | 55–75 | 23–95 | 303 |
| 60..100cm | silt | % | 14–24 | 1–41 | 303 |
| 60..100cm | bd.core | kg/m3 | 1490–1580 | 1250–1800 | 303 |
| 60..100cm | soc | g/kg | 1.2–2 | 0–5.5 | 303 |
| 60..100cm | ph.h2o | pH | 8.4–8.8 | 7.9–9.4 | 303 |
