# Hail civil soil screening

188 route/station sample locations; 116 complete profiles; 72 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 72 |
| fine-soil-plasticity-and-shrink-swell-tests | 35 |
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
| 0..30cm | clay | % | 13–23 | 3–37 | 116 |
| 0..30cm | sand | % | 45–62 | 15–84 | 116 |
| 0..30cm | silt | % | 24–32 | 10–45 | 116 |
| 0..30cm | bd.core | kg/m3 | 1450–1520 | 1270–1670 | 116 |
| 0..30cm | soc | g/kg | 1.6–2.9 | 0.3–6.1 | 116 |
| 0..30cm | ph.h2o | pH | 8.2–8.5 | 7.5–9.5 | 116 |
| 30..60cm | clay | % | 16–24 | 2–40 | 116 |
| 30..60cm | sand | % | 47–61 | 16–90 | 116 |
| 30..60cm | silt | % | 22–29 | 5–45 | 116 |
| 30..60cm | bd.core | kg/m3 | 1430–1570 | 1240–1800 | 116 |
| 30..60cm | soc | g/kg | 1.2–2.1 | 0–6 | 116 |
| 30..60cm | ph.h2o | pH | 8.4–8.9 | 7.6–10 | 116 |
| 60..100cm | clay | % | 16–23 | 1–38 | 116 |
| 60..100cm | sand | % | 48–60 | 15–90 | 116 |
| 60..100cm | silt | % | 23–29 | 5–49 | 116 |
| 60..100cm | bd.core | kg/m3 | 1480–1610 | 1240–1820 | 116 |
| 60..100cm | soc | g/kg | 0.9–1.7 | 0–5.3 | 116 |
| 60..100cm | ph.h2o | pH | 8.4–9 | 7.6–10.1 | 116 |
