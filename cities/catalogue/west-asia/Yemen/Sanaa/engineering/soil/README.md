# Sanaa civil soil screening

380 route/station sample locations; 380 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 380 |
| granular-density-and-groundwater-tests | 380 |

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
| 0..30cm | clay | % | 20–29 | 3–44 | 380 |
| 0..30cm | sand | % | 44–64 | 18–90 | 380 |
| 0..30cm | silt | % | 16–28 | 0–46 | 380 |
| 0..30cm | bd.core | kg/m3 | 1340–1530 | 1140–1730 | 380 |
| 0..30cm | soc | g/kg | 2.3–10.6 | 0.8–23.4 | 380 |
| 0..30cm | ph.h2o | pH | 7.5–8.5 | 6.5–9.4 | 380 |
| 30..60cm | clay | % | 21–31 | 5–45 | 380 |
| 30..60cm | sand | % | 44–65 | 16–92 | 380 |
| 30..60cm | silt | % | 14–27 | 0–47 | 380 |
| 30..60cm | bd.core | kg/m3 | 1360–1520 | 1080–1700 | 380 |
| 30..60cm | soc | g/kg | 1.8–5.8 | 0.4–12.6 | 380 |
| 30..60cm | ph.h2o | pH | 7.4–8.6 | 6.6–9.6 | 380 |
| 60..100cm | clay | % | 21–31 | 5–48 | 380 |
| 60..100cm | sand | % | 45–65 | 12–91 | 380 |
| 60..100cm | silt | % | 14–26 | 0–47 | 380 |
| 60..100cm | bd.core | kg/m3 | 1330–1520 | 920–1760 | 380 |
| 60..100cm | soc | g/kg | 1.2–6.1 | 0.1–14.2 | 380 |
| 60..100cm | ph.h2o | pH | 7.6–8.6 | 6.4–9.5 | 380 |
