# Lahij civil soil screening

121 route/station sample locations; 116 complete profiles; 5 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 5 |
| fine-soil-plasticity-and-shrink-swell-tests | 13 |
| granular-density-and-groundwater-tests | 116 |

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
| 0..30cm | clay | % | 11–19 | 0–31 | 116 |
| 0..30cm | sand | % | 61–75 | 38–91 | 116 |
| 0..30cm | silt | % | 14–21 | 5–33 | 116 |
| 0..30cm | bd.core | kg/m3 | 1450–1490 | 1280–1700 | 116 |
| 0..30cm | soc | g/kg | 2.3–3.4 | 0.6–8.4 | 116 |
| 0..30cm | ph.h2o | pH | 8.1–8.6 | 7.2–9.3 | 116 |
| 30..60cm | clay | % | 11–20 | 1–37 | 116 |
| 30..60cm | sand | % | 58–76 | 23–95 | 116 |
| 30..60cm | silt | % | 13–22 | 2–39 | 116 |
| 30..60cm | bd.core | kg/m3 | 1500–1550 | 1290–1770 | 116 |
| 30..60cm | soc | g/kg | 1.5–2.3 | 0–5.4 | 116 |
| 30..60cm | ph.h2o | pH | 8.4–8.6 | 7.8–9.3 | 116 |
| 60..100cm | clay | % | 11–21 | 1–37 | 116 |
| 60..100cm | sand | % | 56–76 | 24–95 | 116 |
| 60..100cm | silt | % | 13–23 | 2–41 | 116 |
| 60..100cm | bd.core | kg/m3 | 1510–1600 | 1280–1800 | 116 |
| 60..100cm | soc | g/kg | 1.2–1.8 | 0–5.3 | 116 |
| 60..100cm | ph.h2o | pH | 8.4–8.7 | 7.9–9.4 | 116 |
