# Deir-Ez-Zor civil soil screening

112 route/station sample locations; 102 complete profiles; 10 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 10 |
| fine-soil-plasticity-and-shrink-swell-tests | 100 |
| granular-density-and-groundwater-tests | 93 |

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
| 0..30cm | clay | % | 17–27 | 3–39 | 102 |
| 0..30cm | sand | % | 41–61 | 17–87 | 102 |
| 0..30cm | silt | % | 22–34 | 7–49 | 102 |
| 0..30cm | bd.core | kg/m3 | 1450–1510 | 1270–1700 | 102 |
| 0..30cm | soc | g/kg | 1.7–6.6 | 0.5–12.9 | 102 |
| 0..30cm | ph.h2o | pH | 7.8–8.1 | 7.1–9 | 102 |
| 30..60cm | clay | % | 18–28 | 3–41 | 102 |
| 30..60cm | sand | % | 42–60 | 17–92 | 102 |
| 30..60cm | silt | % | 21–32 | 5–44 | 102 |
| 30..60cm | bd.core | kg/m3 | 1440–1540 | 1200–1770 | 102 |
| 30..60cm | soc | g/kg | 1.2–3.5 | 0–7.4 | 102 |
| 30..60cm | ph.h2o | pH | 8.1–8.6 | 7.1–10.1 | 102 |
| 60..100cm | clay | % | 19–29 | 3–42 | 102 |
| 60..100cm | sand | % | 43–61 | 17–90 | 102 |
| 60..100cm | silt | % | 20–31 | 2–45 | 102 |
| 60..100cm | bd.core | kg/m3 | 1440–1580 | 1230–1820 | 102 |
| 60..100cm | soc | g/kg | 1–2.2 | 0–5.3 | 102 |
| 60..100cm | ph.h2o | pH | 8.1–8.8 | 7.3–10.1 | 102 |
