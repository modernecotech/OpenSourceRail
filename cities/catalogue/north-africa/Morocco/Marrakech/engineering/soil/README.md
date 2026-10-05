# Marrakech civil soil screening

2,659 route/station sample locations; 2,586 complete profiles; 73 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 73 |
| fine-soil-plasticity-and-shrink-swell-tests | 1877 |
| granular-density-and-groundwater-tests | 2558 |

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
| 0..30cm | clay | % | 18–28 | 5–38 | 2586 |
| 0..30cm | sand | % | 45–62 | 24–84 | 2586 |
| 0..30cm | silt | % | 19–28 | 6–43 | 2586 |
| 0..30cm | bd.core | kg/m3 | 1270–1480 | 1010–1670 | 2586 |
| 0..30cm | soc | g/kg | 3.3–9.3 | 1.5–19.8 | 2586 |
| 0..30cm | ph.h2o | pH | 7.7–8.2 | 7.1–8.7 | 2586 |
| 30..60cm | clay | % | 19–30 | 4–42 | 2586 |
| 30..60cm | sand | % | 44–61 | 20–87 | 2586 |
| 30..60cm | silt | % | 18–26 | 1–42 | 2586 |
| 30..60cm | bd.core | kg/m3 | 1450–1620 | 1260–1840 | 2586 |
| 30..60cm | soc | g/kg | 2.2–4.8 | 0.8–9.7 | 2586 |
| 30..60cm | ph.h2o | pH | 7.8–8.5 | 6.8–9 | 2586 |
| 60..100cm | clay | % | 19–30 | 5–43 | 2586 |
| 60..100cm | sand | % | 44–61 | 21–87 | 2586 |
| 60..100cm | silt | % | 19–26 | 1–45 | 2586 |
| 60..100cm | bd.core | kg/m3 | 1480–1630 | 1260–1860 | 2586 |
| 60..100cm | soc | g/kg | 1.8–3.6 | 0.5–8 | 2586 |
| 60..100cm | ph.h2o | pH | 7.8–8.5 | 6.9–9 | 2586 |
