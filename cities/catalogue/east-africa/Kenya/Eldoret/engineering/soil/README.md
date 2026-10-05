# Eldoret civil soil screening

140 route/station sample locations; 140 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 140 |
| fine-soil-plasticity-and-shrink-swell-tests | 140 |
| granular-density-and-groundwater-tests | 46 |

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
| 0..30cm | clay | % | 31–40 | 15–51 | 140 |
| 0..30cm | sand | % | 29–47 | 11–75 | 140 |
| 0..30cm | silt | % | 22–31 | 6–44 | 140 |
| 0..30cm | bd.core | kg/m3 | 1100–1190 | 910–1390 | 140 |
| 0..30cm | soc | g/kg | 9.5–22.5 | 5.2–47.3 | 140 |
| 0..30cm | ph.h2o | pH | 5.6–6 | 5–6.8 | 140 |
| 30..60cm | clay | % | 31–41 | 16–53 | 140 |
| 30..60cm | sand | % | 28–47 | 10–77 | 140 |
| 30..60cm | silt | % | 21–31 | 4–45 | 140 |
| 30..60cm | bd.core | kg/m3 | 1130–1260 | 930–1450 | 140 |
| 30..60cm | soc | g/kg | 6.8–12.2 | 3.5–21.9 | 140 |
| 30..60cm | ph.h2o | pH | 5.5–5.9 | 4.9–6.8 | 140 |
| 60..100cm | clay | % | 31–42 | 10–55 | 140 |
| 60..100cm | sand | % | 28–49 | 10–79 | 140 |
| 60..100cm | silt | % | 21–30 | 4–44 | 140 |
| 60..100cm | bd.core | kg/m3 | 1160–1270 | 960–1520 | 140 |
| 60..100cm | soc | g/kg | 5.7–8.5 | 2.9–15.9 | 140 |
| 60..100cm | ph.h2o | pH | 5.5–6.2 | 4.8–7.4 | 140 |
