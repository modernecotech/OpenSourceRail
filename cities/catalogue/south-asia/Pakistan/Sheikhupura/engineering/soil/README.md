# Sheikhupura civil soil screening

29 route/station sample locations; 29 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 29 |
| granular-density-and-groundwater-tests | 20 |
| silt-moisture-frost-and-erosion-review | 4 |

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
| 0..30cm | clay | % | 22–26 | 6–39 | 29 |
| 0..30cm | sand | % | 44–50 | 16–81 | 29 |
| 0..30cm | silt | % | 28–31 | 13–47 | 29 |
| 0..30cm | bd.core | kg/m3 | 1420–1510 | 1270–1660 | 29 |
| 0..30cm | soc | g/kg | 4.3–5.5 | 1.4–14.8 | 29 |
| 0..30cm | ph.h2o | pH | 7.5–7.7 | 6.6–8.5 | 29 |
| 30..60cm | clay | % | 24–28 | 6–41 | 29 |
| 30..60cm | sand | % | 41–48 | 10–79 | 29 |
| 30..60cm | silt | % | 28–32 | 8–50 | 29 |
| 30..60cm | bd.core | kg/m3 | 1440–1560 | 1160–1740 | 29 |
| 30..60cm | soc | g/kg | 1.8–4 | 0.3–7.6 | 29 |
| 30..60cm | ph.h2o | pH | 7.7–7.9 | 6.5–8.8 | 29 |
| 60..100cm | clay | % | 25–28 | 6–41 | 29 |
| 60..100cm | sand | % | 40–48 | 13–79 | 29 |
| 60..100cm | silt | % | 28–32 | 8–50 | 29 |
| 60..100cm | bd.core | kg/m3 | 1510–1600 | 1200–1870 | 29 |
| 60..100cm | soc | g/kg | 1.2–2.8 | 0.1–6.8 | 29 |
| 60..100cm | ph.h2o | pH | 7.9–8 | 6.8–9 | 29 |
