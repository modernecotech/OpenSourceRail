# Eldoret civil soil screening

97 route/station sample locations; 97 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 97 |
| fine-soil-plasticity-and-shrink-swell-tests | 97 |
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
| 0..30cm | clay | % | 31–40 | 14–51 | 97 |
| 0..30cm | sand | % | 29–47 | 11–76 | 97 |
| 0..30cm | silt | % | 22–31 | 6–44 | 97 |
| 0..30cm | bd.core | kg/m3 | 1090–1190 | 880–1390 | 97 |
| 0..30cm | soc | g/kg | 9–22.5 | 3.7–47.3 | 97 |
| 0..30cm | ph.h2o | pH | 5.6–6 | 5–6.9 | 97 |
| 30..60cm | clay | % | 32–41 | 16–52 | 97 |
| 30..60cm | sand | % | 28–47 | 10–77 | 97 |
| 30..60cm | silt | % | 21–31 | 4–45 | 97 |
| 30..60cm | bd.core | kg/m3 | 1130–1260 | 930–1450 | 97 |
| 30..60cm | soc | g/kg | 6–12.2 | 2.8–21.9 | 97 |
| 30..60cm | ph.h2o | pH | 5.5–6 | 4.9–6.8 | 97 |
| 60..100cm | clay | % | 31–42 | 13–54 | 97 |
| 60..100cm | sand | % | 28–48 | 10–79 | 97 |
| 60..100cm | silt | % | 21–30 | 0–44 | 97 |
| 60..100cm | bd.core | kg/m3 | 1160–1270 | 960–1520 | 97 |
| 60..100cm | soc | g/kg | 4.7–8 | 1.6–14.1 | 97 |
| 60..100cm | ph.h2o | pH | 5.5–6.2 | 4.8–7.2 | 97 |
