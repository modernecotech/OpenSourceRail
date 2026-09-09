# Zarqa civil soil screening

126 route/station sample locations; 110 complete profiles; 16 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 16 |
| fine-soil-plasticity-and-shrink-swell-tests | 108 |
| granular-density-and-groundwater-tests | 102 |
| silt-moisture-frost-and-erosion-review | 1 |

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
| 0..30cm | clay | % | 19–28 | 3–42 | 110 |
| 0..30cm | sand | % | 41–57 | 14–85 | 110 |
| 0..30cm | silt | % | 24–33 | 8–47 | 110 |
| 0..30cm | bd.core | kg/m3 | 1370–1460 | 1220–1620 | 110 |
| 0..30cm | soc | g/kg | 2.4–5.9 | 0.9–9.3 | 110 |
| 0..30cm | ph.h2o | pH | 7.6–8.2 | 7.1–8.8 | 110 |
| 30..60cm | clay | % | 19–30 | 4–44 | 110 |
| 30..60cm | sand | % | 39–57 | 13–89 | 110 |
| 30..60cm | silt | % | 22–31 | 5–48 | 110 |
| 30..60cm | bd.core | kg/m3 | 1440–1540 | 1250–1700 | 110 |
| 30..60cm | soc | g/kg | 1.6–3.3 | 0.3–6.7 | 110 |
| 30..60cm | ph.h2o | pH | 7.5–8.5 | 6.9–9.4 | 110 |
| 60..100cm | clay | % | 20–30 | 3–45 | 110 |
| 60..100cm | sand | % | 38–57 | 9–90 | 110 |
| 60..100cm | silt | % | 22–32 | 3–51 | 110 |
| 60..100cm | bd.core | kg/m3 | 1470–1570 | 1250–1750 | 110 |
| 60..100cm | soc | g/kg | 1.2–2.6 | 0.1–5.4 | 110 |
| 60..100cm | ph.h2o | pH | 7.6–8.7 | 6.7–9.5 | 110 |
