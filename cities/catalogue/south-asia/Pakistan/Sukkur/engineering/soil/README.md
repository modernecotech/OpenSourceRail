# Sukkur civil soil screening

97 route/station sample locations; 85 complete profiles; 12 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 12 |
| fine-soil-plasticity-and-shrink-swell-tests | 16 |
| granular-density-and-groundwater-tests | 85 |

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
| 0..30cm | clay | % | 12–20 | 0–35 | 85 |
| 0..30cm | sand | % | 52–70 | 30–92 | 85 |
| 0..30cm | silt | % | 18–27 | 6–42 | 85 |
| 0..30cm | bd.core | kg/m3 | 1420–1550 | 1220–1700 | 85 |
| 0..30cm | soc | g/kg | 2.9–5.1 | 0.8–13.5 | 85 |
| 0..30cm | ph.h2o | pH | 7.6–8.2 | 6.6–9.1 | 85 |
| 30..60cm | clay | % | 15–22 | 0–39 | 85 |
| 30..60cm | sand | % | 51–66 | 16–94 | 85 |
| 30..60cm | silt | % | 20–27 | 5–45 | 85 |
| 30..60cm | bd.core | kg/m3 | 1470–1580 | 1190–1750 | 85 |
| 30..60cm | soc | g/kg | 1.8–2.9 | 0–7.9 | 85 |
| 30..60cm | ph.h2o | pH | 7.7–8.6 | 6–9.5 | 85 |
| 60..100cm | clay | % | 15–22 | 0–38 | 85 |
| 60..100cm | sand | % | 51–65 | 16–93 | 85 |
| 60..100cm | silt | % | 20–27 | 2–44 | 85 |
| 60..100cm | bd.core | kg/m3 | 1490–1590 | 1240–1890 | 85 |
| 60..100cm | soc | g/kg | 1.5–2.4 | 0.3–6.5 | 85 |
| 60..100cm | ph.h2o | pH | 7.7–8.6 | 6–9.6 | 85 |
