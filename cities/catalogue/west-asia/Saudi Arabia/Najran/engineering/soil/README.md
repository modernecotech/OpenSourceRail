# Najran civil soil screening

549 route/station sample locations; 492 complete profiles; 57 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 57 |
| fine-soil-plasticity-and-shrink-swell-tests | 131 |
| granular-density-and-groundwater-tests | 492 |

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
| 0..30cm | clay | % | 13–23 | 0–34 | 492 |
| 0..30cm | sand | % | 50–69 | 26–91 | 492 |
| 0..30cm | silt | % | 17–28 | 5–42 | 492 |
| 0..30cm | bd.core | kg/m3 | 1420–1520 | 1200–1700 | 492 |
| 0..30cm | soc | g/kg | 1.4–5.7 | 0.3–10.4 | 492 |
| 0..30cm | ph.h2o | pH | 7.8–8.9 | 7–9.8 | 492 |
| 30..60cm | clay | % | 15–25 | 1–41 | 492 |
| 30..60cm | sand | % | 48–68 | 16–94 | 492 |
| 30..60cm | silt | % | 17–28 | 3–42 | 492 |
| 30..60cm | bd.core | kg/m3 | 1450–1560 | 1190–1840 | 492 |
| 30..60cm | soc | g/kg | 1.1–2.9 | 0.1–6.5 | 492 |
| 30..60cm | ph.h2o | pH | 8.3–8.9 | 7.4–9.9 | 492 |
| 60..100cm | clay | % | 15–25 | 1–41 | 492 |
| 60..100cm | sand | % | 47–67 | 16–94 | 492 |
| 60..100cm | silt | % | 17–28 | 3–43 | 492 |
| 60..100cm | bd.core | kg/m3 | 1450–1570 | 1240–1870 | 492 |
| 60..100cm | soc | g/kg | 0.8–2.6 | 0.1–5.9 | 492 |
| 60..100cm | ph.h2o | pH | 8.2–8.9 | 7.4–10 | 492 |
