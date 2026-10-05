# Jodhpur civil soil screening

1,799 route/station sample locations; 1,799 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 6 |
| fine-soil-plasticity-and-shrink-swell-tests | 1521 |
| granular-density-and-groundwater-tests | 1799 |

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
| 0..30cm | clay | % | 14–27 | 3–39 | 1799 |
| 0..30cm | sand | % | 45–70 | 16–91 | 1799 |
| 0..30cm | silt | % | 16–28 | 4–44 | 1799 |
| 0..30cm | bd.core | kg/m3 | 1440–1530 | 1240–1690 | 1799 |
| 0..30cm | soc | g/kg | 2.8–6.1 | 1–12.8 | 1799 |
| 0..30cm | ph.h2o | pH | 7.1–8.2 | 5.1–9 | 1799 |
| 30..60cm | clay | % | 16–28 | 3–44 | 1799 |
| 30..60cm | sand | % | 45–66 | 14–94 | 1799 |
| 30..60cm | silt | % | 17–28 | 1–45 | 1799 |
| 30..60cm | bd.core | kg/m3 | 1430–1540 | 1130–1760 | 1799 |
| 30..60cm | soc | g/kg | 2–3.3 | 0.5–7.5 | 1799 |
| 30..60cm | ph.h2o | pH | 7.2–8.5 | 5.1–9.5 | 1799 |
| 60..100cm | clay | % | 17–29 | 2–44 | 1799 |
| 60..100cm | sand | % | 45–64 | 13–92 | 1799 |
| 60..100cm | silt | % | 18–27 | 0–48 | 1799 |
| 60..100cm | bd.core | kg/m3 | 1420–1550 | 1100–1770 | 1799 |
| 60..100cm | soc | g/kg | 1.6–2.7 | 0.2–6.7 | 1799 |
| 60..100cm | ph.h2o | pH | 7.3–8.7 | 5.1–9.7 | 1799 |
