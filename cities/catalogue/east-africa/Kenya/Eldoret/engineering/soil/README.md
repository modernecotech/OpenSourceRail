# Eldoret civil soil screening

107 route/station sample locations; 107 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 107 |
| fine-soil-plasticity-and-shrink-swell-tests | 107 |
| granular-density-and-groundwater-tests | 48 |

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
| 0..30cm | clay | % | 29–40 | 14–51 | 107 |
| 0..30cm | sand | % | 30–49 | 11–78 | 107 |
| 0..30cm | silt | % | 21–31 | 4–45 | 107 |
| 0..30cm | bd.core | kg/m3 | 1090–1290 | 920–1440 | 107 |
| 0..30cm | soc | g/kg | 10.4–24.3 | 4.4–48.1 | 107 |
| 0..30cm | ph.h2o | pH | 5.6–5.9 | 5–6.7 | 107 |
| 30..60cm | clay | % | 31–41 | 13–52 | 107 |
| 30..60cm | sand | % | 31–49 | 11–78 | 107 |
| 30..60cm | silt | % | 20–30 | 3–45 | 107 |
| 30..60cm | bd.core | kg/m3 | 1130–1390 | 920–1640 | 107 |
| 30..60cm | soc | g/kg | 6.4–12.1 | 2.8–19.5 | 107 |
| 30..60cm | ph.h2o | pH | 5.5–5.9 | 4.9–6.7 | 107 |
| 60..100cm | clay | % | 31–42 | 12–53 | 107 |
| 60..100cm | sand | % | 31–49 | 8–82 | 107 |
| 60..100cm | silt | % | 20–30 | 3–46 | 107 |
| 60..100cm | bd.core | kg/m3 | 1160–1440 | 960–1690 | 107 |
| 60..100cm | soc | g/kg | 4.8–8.5 | 2–14.6 | 107 |
| 60..100cm | ph.h2o | pH | 5.5–6.2 | 4.8–7.2 | 107 |
