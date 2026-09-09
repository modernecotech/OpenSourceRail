# Meknes civil soil screening

72 route/station sample locations; 72 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 72 |
| granular-density-and-groundwater-tests | 27 |

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
| 0..30cm | clay | % | 24–33 | 12–42 | 72 |
| 0..30cm | sand | % | 31–48 | 14–74 | 72 |
| 0..30cm | silt | % | 27–36 | 13–47 | 72 |
| 0..30cm | bd.core | kg/m3 | 1350–1440 | 1200–1570 | 72 |
| 0..30cm | soc | g/kg | 5.4–12 | 2.9–22.7 | 72 |
| 0..30cm | ph.h2o | pH | 7.3–7.6 | 6.5–8.2 | 72 |
| 30..60cm | clay | % | 25–35 | 11–44 | 72 |
| 30..60cm | sand | % | 31–47 | 13–76 | 72 |
| 30..60cm | silt | % | 26–34 | 9–46 | 72 |
| 30..60cm | bd.core | kg/m3 | 1480–1550 | 1290–1760 | 72 |
| 30..60cm | soc | g/kg | 3.2–5.7 | 1.3–11.1 | 72 |
| 30..60cm | ph.h2o | pH | 7.3–7.8 | 6.4–8.5 | 72 |
| 60..100cm | clay | % | 26–35 | 12–47 | 72 |
| 60..100cm | sand | % | 33–48 | 13–79 | 72 |
| 60..100cm | silt | % | 25–32 | 7–47 | 72 |
| 60..100cm | bd.core | kg/m3 | 1490–1620 | 1250–1800 | 72 |
| 60..100cm | soc | g/kg | 2.3–3.7 | 1–7 | 72 |
| 60..100cm | ph.h2o | pH | 7.5–8 | 6.6–8.7 | 72 |
