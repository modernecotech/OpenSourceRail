# Dodoma civil soil screening

324 route/station sample locations; 324 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 235 |
| fine-soil-plasticity-and-shrink-swell-tests | 324 |
| granular-density-and-groundwater-tests | 259 |

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
| 0..30cm | clay | % | 24–33 | 14–44 | 324 |
| 0..30cm | sand | % | 48–65 | 26–83 | 324 |
| 0..30cm | silt | % | 10–20 | 0–31 | 324 |
| 0..30cm | bd.core | kg/m3 | 1370–1480 | 1200–1610 | 324 |
| 0..30cm | soc | g/kg | 4.1–9.1 | 1.9–17.4 | 324 |
| 0..30cm | ph.h2o | pH | 5.4–6.9 | 4.7–8.6 | 324 |
| 30..60cm | clay | % | 27–38 | 14–51 | 324 |
| 30..60cm | sand | % | 41–60 | 14–86 | 324 |
| 30..60cm | silt | % | 13–22 | 0–36 | 324 |
| 30..60cm | bd.core | kg/m3 | 1400–1510 | 1200–1660 | 324 |
| 30..60cm | soc | g/kg | 2.8–7.1 | 1–15.5 | 324 |
| 30..60cm | ph.h2o | pH | 5.8–6.9 | 4.7–8.1 | 324 |
| 60..100cm | clay | % | 29–39 | 14–53 | 324 |
| 60..100cm | sand | % | 39–56 | 12–86 | 324 |
| 60..100cm | silt | % | 15–24 | 0–38 | 324 |
| 60..100cm | bd.core | kg/m3 | 1380–1530 | 1130–1730 | 324 |
| 60..100cm | soc | g/kg | 2.8–6.8 | 0.9–20.4 | 324 |
| 60..100cm | ph.h2o | pH | 6–7 | 4.8–8.4 | 324 |
