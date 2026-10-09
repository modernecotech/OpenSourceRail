# Buraidah civil soil screening

464 route/station sample locations; 328 complete profiles; 136 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 136 |
| fine-soil-plasticity-and-shrink-swell-tests | 205 |
| granular-density-and-groundwater-tests | 325 |
| silt-moisture-frost-and-erosion-review | 19 |

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
| 0..30cm | clay | % | 16–26 | 0–39 | 328 |
| 0..30cm | sand | % | 40–59 | 15–85 | 328 |
| 0..30cm | silt | % | 25–34 | 6–51 | 328 |
| 0..30cm | bd.core | kg/m3 | 1450–1510 | 1270–1690 | 328 |
| 0..30cm | soc | g/kg | 2.1–4.5 | 0.5–8.1 | 328 |
| 0..30cm | ph.h2o | pH | 8.1–8.5 | 7.4–9.4 | 328 |
| 30..60cm | clay | % | 17–28 | 2–43 | 328 |
| 30..60cm | sand | % | 39–61 | 14–92 | 328 |
| 30..60cm | silt | % | 22–33 | 3–50 | 328 |
| 30..60cm | bd.core | kg/m3 | 1420–1520 | 1210–1750 | 328 |
| 30..60cm | soc | g/kg | 1.5–2.9 | 0–7.3 | 328 |
| 30..60cm | ph.h2o | pH | 8.2–8.8 | 7.6–10 | 328 |
| 60..100cm | clay | % | 17–28 | 1–42 | 328 |
| 60..100cm | sand | % | 39–61 | 14–92 | 328 |
| 60..100cm | silt | % | 23–33 | 3–53 | 328 |
| 60..100cm | bd.core | kg/m3 | 1450–1550 | 1230–1820 | 328 |
| 60..100cm | soc | g/kg | 1.3–2.4 | 0–6.5 | 328 |
| 60..100cm | ph.h2o | pH | 8.2–8.9 | 7.6–10.1 | 328 |
