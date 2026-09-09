# Marrakech civil soil screening

389 route/station sample locations; 376 complete profiles; 13 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 13 |
| fine-soil-plasticity-and-shrink-swell-tests | 280 |
| granular-density-and-groundwater-tests | 364 |

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
| 0..30cm | clay | % | 18–27 | 7–39 | 376 |
| 0..30cm | sand | % | 46–61 | 26–82 | 376 |
| 0..30cm | silt | % | 20–28 | 6–42 | 376 |
| 0..30cm | bd.core | kg/m3 | 1270–1480 | 1010–1670 | 376 |
| 0..30cm | soc | g/kg | 3.1–9.3 | 1.4–18.9 | 376 |
| 0..30cm | ph.h2o | pH | 7.6–8.2 | 7–8.6 | 376 |
| 30..60cm | clay | % | 20–28 | 7–42 | 376 |
| 30..60cm | sand | % | 46–60 | 23–85 | 376 |
| 30..60cm | silt | % | 20–27 | 5–43 | 376 |
| 30..60cm | bd.core | kg/m3 | 1450–1600 | 1260–1840 | 376 |
| 30..60cm | soc | g/kg | 2.3–4.7 | 0.9–9.9 | 376 |
| 30..60cm | ph.h2o | pH | 7.6–8.4 | 6.6–8.9 | 376 |
| 60..100cm | clay | % | 20–28 | 7–43 | 376 |
| 60..100cm | sand | % | 46–61 | 20–89 | 376 |
| 60..100cm | silt | % | 19–26 | 3–45 | 376 |
| 60..100cm | bd.core | kg/m3 | 1490–1630 | 1290–1850 | 376 |
| 60..100cm | soc | g/kg | 1.8–3.7 | 0.5–7.3 | 376 |
| 60..100cm | ph.h2o | pH | 7.6–8.5 | 6.5–9 | 376 |
