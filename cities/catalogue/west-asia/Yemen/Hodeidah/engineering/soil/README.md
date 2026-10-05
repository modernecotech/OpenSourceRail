# Hodeidah civil soil screening

146 route/station sample locations; 50 complete profiles; 96 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 96 |
| granular-density-and-groundwater-tests | 50 |

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
| 0..30cm | clay | % | 11–15 | 0–30 | 50 |
| 0..30cm | sand | % | 66–74 | 37–94 | 50 |
| 0..30cm | silt | % | 15–19 | 2–35 | 50 |
| 0..30cm | bd.core | kg/m3 | 1390–1440 | 1050–1690 | 50 |
| 0..30cm | soc | g/kg | 2.5–6.6 | 0.8–20.7 | 50 |
| 0..30cm | ph.h2o | pH | 8.4–8.7 | 7.8–9.3 | 50 |
| 30..60cm | clay | % | 12–16 | 0–30 | 50 |
| 30..60cm | sand | % | 65–74 | 31–96 | 50 |
| 30..60cm | silt | % | 14–19 | 0–37 | 50 |
| 30..60cm | bd.core | kg/m3 | 1490–1540 | 1260–1720 | 50 |
| 30..60cm | soc | g/kg | 1.3–6.5 | 0–41.5 | 50 |
| 30..60cm | ph.h2o | pH | 8.4–8.7 | 7.5–9.3 | 50 |
| 60..100cm | clay | % | 12–17 | 0–34 | 50 |
| 60..100cm | sand | % | 63–75 | 26–96 | 50 |
| 60..100cm | silt | % | 14–20 | 0–40 | 50 |
| 60..100cm | bd.core | kg/m3 | 1520–1570 | 1330–1770 | 50 |
| 60..100cm | soc | g/kg | 1.2–4.6 | 0–27.6 | 50 |
| 60..100cm | ph.h2o | pH | 8.4–8.8 | 7.6–9.3 | 50 |
