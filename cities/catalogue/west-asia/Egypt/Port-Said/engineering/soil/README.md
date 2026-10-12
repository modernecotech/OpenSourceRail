# Port-Said civil soil screening

595 route/station sample locations; 582 complete profiles; 13 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 13 |
| fine-soil-plasticity-and-shrink-swell-tests | 315 |
| granular-density-and-groundwater-tests | 582 |

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
| 0..30cm | clay | % | 15–23 | 0–36 | 582 |
| 0..30cm | sand | % | 51–67 | 26–97 | 582 |
| 0..30cm | silt | % | 18–27 | 2–40 | 582 |
| 0..30cm | bd.core | kg/m3 | 1370–1450 | 1080–1660 | 582 |
| 0..30cm | soc | g/kg | 2.2–6.8 | 0.7–13.9 | 582 |
| 0..30cm | ph.h2o | pH | 7.8–8.5 | 6.9–9.2 | 582 |
| 30..60cm | clay | % | 16–24 | 1–38 | 582 |
| 30..60cm | sand | % | 52–67 | 27–98 | 582 |
| 30..60cm | silt | % | 17–24 | 0–41 | 582 |
| 30..60cm | bd.core | kg/m3 | 1400–1590 | 1000–1850 | 582 |
| 30..60cm | soc | g/kg | 1.2–5.8 | 0–17 | 582 |
| 30..60cm | ph.h2o | pH | 7.8–8.5 | 6.5–9.4 | 582 |
| 60..100cm | clay | % | 17–24 | 1–38 | 582 |
| 60..100cm | sand | % | 52–67 | 25–98 | 582 |
| 60..100cm | silt | % | 16–24 | 0–42 | 582 |
| 60..100cm | bd.core | kg/m3 | 1350–1610 | 750–1900 | 582 |
| 60..100cm | soc | g/kg | 1.3–6.4 | 0.2–26.2 | 582 |
| 60..100cm | ph.h2o | pH | 7.7–8.6 | 6–9.5 | 582 |
