# Tabuk civil soil screening

130 route/station sample locations; 88 complete profiles; 42 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 42 |
| fine-soil-plasticity-and-shrink-swell-tests | 30 |
| granular-density-and-groundwater-tests | 88 |

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
| 0..30cm | clay | % | 14–25 | 2–37 | 88 |
| 0..30cm | sand | % | 43–66 | 16–89 | 88 |
| 0..30cm | silt | % | 20–31 | 8–45 | 88 |
| 0..30cm | bd.core | kg/m3 | 1470–1530 | 1260–1710 | 88 |
| 0..30cm | soc | g/kg | 1.6–4 | 0.5–8.1 | 88 |
| 0..30cm | ph.h2o | pH | 8.2–8.7 | 7.6–9.6 | 88 |
| 30..60cm | clay | % | 15–27 | 2–41 | 88 |
| 30..60cm | sand | % | 41–65 | 12–91 | 88 |
| 30..60cm | silt | % | 20–31 | 5–47 | 88 |
| 30..60cm | bd.core | kg/m3 | 1480–1550 | 1240–1780 | 88 |
| 30..60cm | soc | g/kg | 1.2–2.4 | 0.1–6.2 | 88 |
| 30..60cm | ph.h2o | pH | 8.4–9 | 7.8–10 | 88 |
| 60..100cm | clay | % | 15–26 | 1–41 | 88 |
| 60..100cm | sand | % | 42–64 | 13–91 | 88 |
| 60..100cm | silt | % | 21–32 | 4–47 | 88 |
| 60..100cm | bd.core | kg/m3 | 1500–1600 | 1270–1840 | 88 |
| 60..100cm | soc | g/kg | 1–2.1 | 0.1–5.3 | 88 |
| 60..100cm | ph.h2o | pH | 8.4–9 | 7.8–10.2 | 88 |
