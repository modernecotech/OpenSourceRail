# Sukkur civil soil screening

168 route/station sample locations; 167 complete profiles; 1 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 20 |
| granular-density-and-groundwater-tests | 167 |

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
| 0..30cm | clay | % | 13–20 | 0–35 | 167 |
| 0..30cm | sand | % | 52–66 | 28–92 | 167 |
| 0..30cm | silt | % | 20–27 | 6–43 | 167 |
| 0..30cm | bd.core | kg/m3 | 1410–1560 | 1210–1710 | 167 |
| 0..30cm | soc | g/kg | 3–5.4 | 0.9–11.9 | 167 |
| 0..30cm | ph.h2o | pH | 7.8–8.3 | 6.9–9.1 | 167 |
| 30..60cm | clay | % | 16–22 | 0–40 | 167 |
| 30..60cm | sand | % | 51–64 | 16–94 | 167 |
| 30..60cm | silt | % | 21–27 | 3–45 | 167 |
| 30..60cm | bd.core | kg/m3 | 1460–1570 | 1210–1770 | 167 |
| 30..60cm | soc | g/kg | 1.7–2.7 | 0.3–9.7 | 167 |
| 30..60cm | ph.h2o | pH | 8–8.6 | 6.9–9.5 | 167 |
| 60..100cm | clay | % | 16–22 | 0–38 | 167 |
| 60..100cm | sand | % | 51–63 | 16–93 | 167 |
| 60..100cm | silt | % | 21–28 | 4–44 | 167 |
| 60..100cm | bd.core | kg/m3 | 1480–1590 | 1210–1780 | 167 |
| 60..100cm | soc | g/kg | 1.6–2.5 | 0.3–6.9 | 167 |
| 60..100cm | ph.h2o | pH | 8–8.6 | 7–9.6 | 167 |
