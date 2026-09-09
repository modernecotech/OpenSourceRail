# Kenitra civil soil screening

105 route/station sample locations; 102 complete profiles; 3 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 3 |
| fine-soil-plasticity-and-shrink-swell-tests | 99 |
| granular-density-and-groundwater-tests | 102 |

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
| 0..30cm | clay | % | 18–28 | 2–46 | 102 |
| 0..30cm | sand | % | 43–63 | 11–91 | 102 |
| 0..30cm | silt | % | 19–31 | 3–46 | 102 |
| 0..30cm | bd.core | kg/m3 | 1340–1480 | 1100–1660 | 102 |
| 0..30cm | soc | g/kg | 5–15.5 | 2.3–34.1 | 102 |
| 0..30cm | ph.h2o | pH | 6.8–7.8 | 5.9–8.3 | 102 |
| 30..60cm | clay | % | 18–28 | 3–49 | 102 |
| 30..60cm | sand | % | 44–64 | 11–95 | 102 |
| 30..60cm | silt | % | 18–28 | 0–47 | 102 |
| 30..60cm | bd.core | kg/m3 | 1470–1580 | 1230–1810 | 102 |
| 30..60cm | soc | g/kg | 2.8–6.8 | 1.2–13.6 | 102 |
| 30..60cm | ph.h2o | pH | 7–7.8 | 5.6–8.6 | 102 |
| 60..100cm | clay | % | 19–28 | 2–49 | 102 |
| 60..100cm | sand | % | 45–63 | 12–92 | 102 |
| 60..100cm | silt | % | 17–28 | 0–47 | 102 |
| 60..100cm | bd.core | kg/m3 | 1490–1620 | 1230–1830 | 102 |
| 60..100cm | soc | g/kg | 1.7–5.3 | 0.1–11.4 | 102 |
| 60..100cm | ph.h2o | pH | 7.2–8 | 5.5–8.9 | 102 |
