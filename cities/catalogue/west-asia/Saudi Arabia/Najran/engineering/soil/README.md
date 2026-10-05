# Najran civil soil screening

118 route/station sample locations; 109 complete profiles; 9 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 9 |
| fine-soil-plasticity-and-shrink-swell-tests | 46 |
| granular-density-and-groundwater-tests | 109 |

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
| 0..30cm | clay | % | 13–22 | 3–34 | 109 |
| 0..30cm | sand | % | 51–69 | 27–91 | 109 |
| 0..30cm | silt | % | 17–28 | 6–40 | 109 |
| 0..30cm | bd.core | kg/m3 | 1440–1520 | 1270–1700 | 109 |
| 0..30cm | soc | g/kg | 1.6–5.1 | 0.5–9.3 | 109 |
| 0..30cm | ph.h2o | pH | 7.9–8.9 | 7.1–9.8 | 109 |
| 30..60cm | clay | % | 15–24 | 3–41 | 109 |
| 30..60cm | sand | % | 49–68 | 17–94 | 109 |
| 30..60cm | silt | % | 17–27 | 3–42 | 109 |
| 30..60cm | bd.core | kg/m3 | 1460–1550 | 1230–1790 | 109 |
| 30..60cm | soc | g/kg | 1.1–2.9 | 0.1–6.1 | 109 |
| 30..60cm | ph.h2o | pH | 8.3–8.9 | 7.6–9.9 | 109 |
| 60..100cm | clay | % | 15–25 | 3–40 | 109 |
| 60..100cm | sand | % | 47–67 | 18–94 | 109 |
| 60..100cm | silt | % | 17–28 | 4–43 | 109 |
| 60..100cm | bd.core | kg/m3 | 1450–1570 | 1240–1840 | 109 |
| 60..100cm | soc | g/kg | 0.9–2.6 | 0.2–5.4 | 109 |
| 60..100cm | ph.h2o | pH | 8.3–8.9 | 7.7–9.9 | 109 |
