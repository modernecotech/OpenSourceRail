# Nacala civil soil screening

60 route/station sample locations; 54 complete profiles; 6 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 21 |
| coverage-gap | 6 |
| fine-soil-plasticity-and-shrink-swell-tests | 54 |
| granular-density-and-groundwater-tests | 54 |

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
| 0..30cm | clay | % | 21–26 | 6–40 | 54 |
| 0..30cm | sand | % | 59–70 | 34–93 | 54 |
| 0..30cm | silt | % | 9–15 | 0–30 | 54 |
| 0..30cm | bd.core | kg/m3 | 1330–1440 | 1160–1570 | 54 |
| 0..30cm | soc | g/kg | 5.1–8.7 | 2.7–13.3 | 54 |
| 0..30cm | ph.h2o | pH | 6.4–6.8 | 5.3–8 | 54 |
| 30..60cm | clay | % | 23–28 | 5–50 | 54 |
| 30..60cm | sand | % | 57–68 | 27–94 | 54 |
| 30..60cm | silt | % | 9–16 | 0–32 | 54 |
| 30..60cm | bd.core | kg/m3 | 1400–1540 | 1160–1680 | 54 |
| 30..60cm | soc | g/kg | 3.4–5.4 | 1.6–8.5 | 54 |
| 30..60cm | ph.h2o | pH | 6.5–6.9 | 5.4–8 | 54 |
| 60..100cm | clay | % | 22–28 | 5–46 | 54 |
| 60..100cm | sand | % | 57–68 | 25–94 | 54 |
| 60..100cm | silt | % | 10–16 | 0–37 | 54 |
| 60..100cm | bd.core | kg/m3 | 1430–1580 | 1230–1730 | 54 |
| 60..100cm | soc | g/kg | 2.8–4.2 | 1–8.5 | 54 |
| 60..100cm | ph.h2o | pH | 6.7–7.2 | 5.3–8.6 | 54 |
