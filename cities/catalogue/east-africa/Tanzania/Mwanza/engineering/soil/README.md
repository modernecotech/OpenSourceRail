# Mwanza civil soil screening

2,459 route/station sample locations; 2,452 complete profiles; 7 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 2414 |
| coverage-gap | 7 |
| fine-soil-plasticity-and-shrink-swell-tests | 2452 |
| granular-density-and-groundwater-tests | 2031 |

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
| 0..30cm | clay | % | 25–36 | 10–50 | 2452 |
| 0..30cm | sand | % | 37–59 | 13–83 | 2452 |
| 0..30cm | silt | % | 16–28 | 4–44 | 2452 |
| 0..30cm | bd.core | kg/m3 | 1180–1520 | 890–1720 | 2452 |
| 0..30cm | soc | g/kg | 6–16.8 | 2.1–31.8 | 2452 |
| 0..30cm | ph.h2o | pH | 5.6–6.9 | 4.8–8 | 2452 |
| 30..60cm | clay | % | 24–37 | 7–54 | 2452 |
| 30..60cm | sand | % | 39–61 | 13–90 | 2452 |
| 30..60cm | silt | % | 14–25 | 0–43 | 2452 |
| 30..60cm | bd.core | kg/m3 | 1200–1550 | 960–1740 | 2452 |
| 30..60cm | soc | g/kg | 4.1–13.5 | 1.5–32.4 | 2452 |
| 30..60cm | ph.h2o | pH | 5.7–6.9 | 4.8–8 | 2452 |
| 60..100cm | clay | % | 23–37 | 7–55 | 2452 |
| 60..100cm | sand | % | 40–62 | 12–90 | 2452 |
| 60..100cm | silt | % | 14–25 | 0–44 | 2452 |
| 60..100cm | bd.core | kg/m3 | 1180–1520 | 920–1780 | 2452 |
| 60..100cm | soc | g/kg | 3.7–12.7 | 1.4–42.7 | 2452 |
| 60..100cm | ph.h2o | pH | 6–6.9 | 4.6–8.3 | 2452 |
