# Taif civil soil screening

115 route/station sample locations; 76 complete profiles; 39 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 39 |
| fine-soil-plasticity-and-shrink-swell-tests | 75 |
| granular-density-and-groundwater-tests | 76 |

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
| 0..30cm | clay | % | 17–26 | 5–39 | 76 |
| 0..30cm | sand | % | 51–64 | 28–89 | 76 |
| 0..30cm | silt | % | 18–24 | 5–38 | 76 |
| 0..30cm | bd.core | kg/m3 | 1440–1500 | 1310–1630 | 76 |
| 0..30cm | soc | g/kg | 2.4–4.4 | 0.8–10.5 | 76 |
| 0..30cm | ph.h2o | pH | 8–8.6 | 7.6–9.3 | 76 |
| 30..60cm | clay | % | 20–27 | 4–42 | 76 |
| 30..60cm | sand | % | 49–62 | 17–92 | 76 |
| 30..60cm | silt | % | 19–26 | 3–41 | 76 |
| 30..60cm | bd.core | kg/m3 | 1480–1540 | 1290–1720 | 76 |
| 30..60cm | soc | g/kg | 1.6–3.3 | 0.1–6.4 | 76 |
| 30..60cm | ph.h2o | pH | 8.3–8.8 | 7.7–9.5 | 76 |
| 60..100cm | clay | % | 20–26 | 4–44 | 76 |
| 60..100cm | sand | % | 48–62 | 16–91 | 76 |
| 60..100cm | silt | % | 18–26 | 2–44 | 76 |
| 60..100cm | bd.core | kg/m3 | 1470–1580 | 1240–1770 | 76 |
| 60..100cm | soc | g/kg | 1.3–2.6 | 0–4.9 | 76 |
| 60..100cm | ph.h2o | pH | 8.3–8.8 | 7.8–9.7 | 76 |
