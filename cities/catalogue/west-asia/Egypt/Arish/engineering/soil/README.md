# Arish civil soil screening

355 route/station sample locations; 340 complete profiles; 15 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 15 |
| fine-soil-plasticity-and-shrink-swell-tests | 3 |
| granular-density-and-groundwater-tests | 340 |

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
| 0..30cm | clay | % | 11–21 | 2–34 | 340 |
| 0..30cm | sand | % | 53–75 | 26–92 | 340 |
| 0..30cm | silt | % | 14–26 | 5–40 | 340 |
| 0..30cm | bd.core | kg/m3 | 1400–1510 | 1210–1660 | 340 |
| 0..30cm | soc | g/kg | 1.9–6.4 | 0.7–11.5 | 340 |
| 0..30cm | ph.h2o | pH | 8–8.5 | 7.2–9 | 340 |
| 30..60cm | clay | % | 11–21 | 2–37 | 340 |
| 30..60cm | sand | % | 54–76 | 27–95 | 340 |
| 30..60cm | silt | % | 13–25 | 2–41 | 340 |
| 30..60cm | bd.core | kg/m3 | 1480–1580 | 1310–1760 | 340 |
| 30..60cm | soc | g/kg | 1.4–3.2 | 0.3–7 | 340 |
| 30..60cm | ph.h2o | pH | 8.1–8.5 | 7.6–9.2 | 340 |
| 60..100cm | clay | % | 11–21 | 2–35 | 340 |
| 60..100cm | sand | % | 54–76 | 26–95 | 340 |
| 60..100cm | silt | % | 14–25 | 1–41 | 340 |
| 60..100cm | bd.core | kg/m3 | 1500–1590 | 1280–1780 | 340 |
| 60..100cm | soc | g/kg | 0.9–2.5 | 0.1–5.7 | 340 |
| 60..100cm | ph.h2o | pH | 8.2–8.6 | 7.7–9.5 | 340 |
