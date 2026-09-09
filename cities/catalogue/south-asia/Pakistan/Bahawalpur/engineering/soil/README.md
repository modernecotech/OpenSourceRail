# Bahawalpur civil soil screening

87 route/station sample locations; 87 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 18 |
| granular-density-and-groundwater-tests | 87 |

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
| 0..30cm | clay | % | 12–20 | 1–34 | 87 |
| 0..30cm | sand | % | 52–69 | 27–92 | 87 |
| 0..30cm | silt | % | 18–28 | 7–40 | 87 |
| 0..30cm | bd.core | kg/m3 | 1480–1550 | 1320–1710 | 87 |
| 0..30cm | soc | g/kg | 2.6–5.3 | 0.9–12.4 | 87 |
| 0..30cm | ph.h2o | pH | 8–8.4 | 7.4–9.2 | 87 |
| 30..60cm | clay | % | 15–21 | 0–37 | 87 |
| 30..60cm | sand | % | 52–64 | 21–90 | 87 |
| 30..60cm | silt | % | 21–28 | 5–44 | 87 |
| 30..60cm | bd.core | kg/m3 | 1500–1590 | 1330–1770 | 87 |
| 30..60cm | soc | g/kg | 1.8–2.7 | 0.2–6.7 | 87 |
| 30..60cm | ph.h2o | pH | 8.3–8.7 | 7.5–9.4 | 87 |
| 60..100cm | clay | % | 15–20 | 0–36 | 87 |
| 60..100cm | sand | % | 53–63 | 20–89 | 87 |
| 60..100cm | silt | % | 21–27 | 4–43 | 87 |
| 60..100cm | bd.core | kg/m3 | 1510–1610 | 1260–1790 | 87 |
| 60..100cm | soc | g/kg | 1.7–2.5 | 0.3–5.9 | 87 |
| 60..100cm | ph.h2o | pH | 8.3–8.8 | 7.5–9.7 | 87 |
