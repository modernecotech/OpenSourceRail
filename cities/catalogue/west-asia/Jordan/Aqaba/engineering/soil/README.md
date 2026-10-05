# Aqaba civil soil screening

86 route/station sample locations; 75 complete profiles; 11 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 11 |
| fine-soil-plasticity-and-shrink-swell-tests | 10 |
| granular-density-and-groundwater-tests | 75 |

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
| 0..30cm | clay | % | 11–19 | 3–35 | 75 |
| 0..30cm | sand | % | 56–74 | 25–90 | 75 |
| 0..30cm | silt | % | 15–25 | 6–40 | 75 |
| 0..30cm | bd.core | kg/m3 | 1480–1520 | 1270–1680 | 75 |
| 0..30cm | soc | g/kg | 2.2–7.7 | 0.6–21.7 | 75 |
| 0..30cm | ph.h2o | pH | 8–8.6 | 7.1–9.4 | 75 |
| 30..60cm | clay | % | 11–21 | 1–38 | 75 |
| 30..60cm | sand | % | 55–75 | 24–95 | 75 |
| 30..60cm | silt | % | 13–24 | 2–40 | 75 |
| 30..60cm | bd.core | kg/m3 | 1480–1560 | 1320–1730 | 75 |
| 30..60cm | soc | g/kg | 1.3–6.7 | 0–41.5 | 75 |
| 30..60cm | ph.h2o | pH | 8–8.9 | 7–9.8 | 75 |
| 60..100cm | clay | % | 11–21 | 1–37 | 75 |
| 60..100cm | sand | % | 56–75 | 25–95 | 75 |
| 60..100cm | silt | % | 14–24 | 2–40 | 75 |
| 60..100cm | bd.core | kg/m3 | 1490–1590 | 1280–1780 | 75 |
| 60..100cm | soc | g/kg | 1.3–4.5 | 0–30.8 | 75 |
| 60..100cm | ph.h2o | pH | 8–8.9 | 6.6–9.8 | 75 |
