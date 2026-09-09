# Buraidah civil soil screening

109 route/station sample locations; 90 complete profiles; 19 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 19 |
| fine-soil-plasticity-and-shrink-swell-tests | 51 |
| granular-density-and-groundwater-tests | 89 |
| silt-moisture-frost-and-erosion-review | 2 |

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
| 0..30cm | clay | % | 16–24 | 2–37 | 90 |
| 0..30cm | sand | % | 44–58 | 20–84 | 90 |
| 0..30cm | silt | % | 25–32 | 8–49 | 90 |
| 0..30cm | bd.core | kg/m3 | 1440–1510 | 1270–1710 | 90 |
| 0..30cm | soc | g/kg | 2.3–3.7 | 0.5–9 | 90 |
| 0..30cm | ph.h2o | pH | 8.1–8.5 | 7.5–9.3 | 90 |
| 30..60cm | clay | % | 18–26 | 3–39 | 90 |
| 30..60cm | sand | % | 43–58 | 14–91 | 90 |
| 30..60cm | silt | % | 23–32 | 3–50 | 90 |
| 30..60cm | bd.core | kg/m3 | 1420–1520 | 1210–1750 | 90 |
| 30..60cm | soc | g/kg | 1.6–2.4 | 0–6.5 | 90 |
| 30..60cm | ph.h2o | pH | 8.2–8.7 | 7.5–10 | 90 |
| 60..100cm | clay | % | 18–25 | 2–40 | 90 |
| 60..100cm | sand | % | 43–58 | 14–92 | 90 |
| 60..100cm | silt | % | 24–32 | 3–50 | 90 |
| 60..100cm | bd.core | kg/m3 | 1450–1550 | 1230–1800 | 90 |
| 60..100cm | soc | g/kg | 1.4–2.1 | 0–5.2 | 90 |
| 60..100cm | ph.h2o | pH | 8.2–8.8 | 7.5–10.1 | 90 |
