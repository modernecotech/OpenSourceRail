# Mecca civil soil screening

324 route/station sample locations; 231 complete profiles; 93 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 93 |
| fine-soil-plasticity-and-shrink-swell-tests | 86 |
| granular-density-and-groundwater-tests | 231 |

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
| 0..30cm | clay | % | 13–20 | 3–34 | 231 |
| 0..30cm | sand | % | 60–75 | 33–91 | 231 |
| 0..30cm | silt | % | 12–20 | 0–35 | 231 |
| 0..30cm | bd.core | kg/m3 | 1430–1510 | 1210–1720 | 231 |
| 0..30cm | soc | g/kg | 1.7–3.1 | 0.3–9.5 | 231 |
| 0..30cm | ph.h2o | pH | 8.2–8.7 | 7.7–9.6 | 231 |
| 30..60cm | clay | % | 13–22 | 2–39 | 231 |
| 30..60cm | sand | % | 56–74 | 19–94 | 231 |
| 30..60cm | silt | % | 12–21 | 0–40 | 231 |
| 30..60cm | bd.core | kg/m3 | 1460–1580 | 1190–1800 | 231 |
| 30..60cm | soc | g/kg | 1–2.6 | 0–7.5 | 231 |
| 30..60cm | ph.h2o | pH | 8.3–8.8 | 7.8–9.8 | 231 |
| 60..100cm | clay | % | 14–23 | 1–41 | 231 |
| 60..100cm | sand | % | 55–73 | 17–95 | 231 |
| 60..100cm | silt | % | 12–22 | 0–40 | 231 |
| 60..100cm | bd.core | kg/m3 | 1490–1600 | 1230–1880 | 231 |
| 60..100cm | soc | g/kg | 1–2.6 | 0–8 | 231 |
| 60..100cm | ph.h2o | pH | 8.3–8.9 | 7.8–9.9 | 231 |
