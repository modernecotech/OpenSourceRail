# Najran civil soil screening

1,510 route/station sample locations; 1,304 complete profiles; 206 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 206 |
| fine-soil-plasticity-and-shrink-swell-tests | 342 |
| granular-density-and-groundwater-tests | 1304 |

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
| 0..30cm | clay | % | 12–22 | 0–34 | 1304 |
| 0..30cm | sand | % | 51–69 | 26–92 | 1304 |
| 0..30cm | silt | % | 18–28 | 6–41 | 1304 |
| 0..30cm | bd.core | kg/m3 | 1420–1510 | 1180–1700 | 1304 |
| 0..30cm | soc | g/kg | 1.3–5.3 | 0.3–11.2 | 1304 |
| 0..30cm | ph.h2o | pH | 7.8–8.9 | 7–9.8 | 1304 |
| 30..60cm | clay | % | 14–24 | 0–42 | 1304 |
| 30..60cm | sand | % | 49–69 | 15–96 | 1304 |
| 30..60cm | silt | % | 17–27 | 3–44 | 1304 |
| 30..60cm | bd.core | kg/m3 | 1460–1560 | 1240–1840 | 1304 |
| 30..60cm | soc | g/kg | 1.1–2.8 | 0.1–6.9 | 1304 |
| 30..60cm | ph.h2o | pH | 8.2–8.9 | 7.4–9.8 | 1304 |
| 60..100cm | clay | % | 15–24 | 0–42 | 1304 |
| 60..100cm | sand | % | 49–67 | 16–96 | 1304 |
| 60..100cm | silt | % | 18–27 | 3–46 | 1304 |
| 60..100cm | bd.core | kg/m3 | 1460–1570 | 1240–1840 | 1304 |
| 60..100cm | soc | g/kg | 0.8–2.5 | 0.1–6 | 1304 |
| 60..100cm | ph.h2o | pH | 8.2–8.9 | 7.4–9.9 | 1304 |
