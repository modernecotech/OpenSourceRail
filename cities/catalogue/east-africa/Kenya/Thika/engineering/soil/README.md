# Thika civil soil screening

156 route/station sample locations; 156 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 17 |
| fine-soil-plasticity-and-shrink-swell-tests | 156 |
| granular-density-and-groundwater-tests | 13 |

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
| 0..30cm | clay | % | 32–40 | 16–53 | 156 |
| 0..30cm | sand | % | 30–42 | 10–67 | 156 |
| 0..30cm | silt | % | 23–31 | 10–44 | 156 |
| 0..30cm | bd.core | kg/m3 | 1200–1360 | 980–1500 | 156 |
| 0..30cm | soc | g/kg | 6.8–18.8 | 3.7–31.2 | 156 |
| 0..30cm | ph.h2o | pH | 5.8–7.1 | 4.8–8.1 | 156 |
| 30..60cm | clay | % | 32–41 | 14–52 | 156 |
| 30..60cm | sand | % | 31–44 | 7–73 | 156 |
| 30..60cm | silt | % | 22–32 | 6–47 | 156 |
| 30..60cm | bd.core | kg/m3 | 1240–1350 | 1010–1500 | 156 |
| 30..60cm | soc | g/kg | 5.7–10 | 2.3–18.5 | 156 |
| 30..60cm | ph.h2o | pH | 5.9–7.2 | 5–8.2 | 156 |
| 60..100cm | clay | % | 31–40 | 13–53 | 156 |
| 60..100cm | sand | % | 31–45 | 7–77 | 156 |
| 60..100cm | silt | % | 23–33 | 6–48 | 156 |
| 60..100cm | bd.core | kg/m3 | 1210–1370 | 970–1560 | 156 |
| 60..100cm | soc | g/kg | 4.2–7.7 | 1.4–13.9 | 156 |
| 60..100cm | ph.h2o | pH | 6–7.3 | 4.8–8.2 | 156 |
