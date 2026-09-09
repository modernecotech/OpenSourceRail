# Mukalla civil soil screening

156 route/station sample locations; 102 complete profiles; 54 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 54 |
| fine-soil-plasticity-and-shrink-swell-tests | 5 |
| granular-density-and-groundwater-tests | 102 |

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
| 0..30cm | clay | % | 10–17 | 0–28 | 102 |
| 0..30cm | sand | % | 64–76 | 41–94 | 102 |
| 0..30cm | silt | % | 13–20 | 3–31 | 102 |
| 0..30cm | bd.core | kg/m3 | 1420–1500 | 1180–1690 | 102 |
| 0..30cm | soc | g/kg | 2–6 | 0.6–23.9 | 102 |
| 0..30cm | ph.h2o | pH | 8.3–8.7 | 7.8–9.3 | 102 |
| 30..60cm | clay | % | 11–21 | 0–36 | 102 |
| 30..60cm | sand | % | 56–77 | 28–94 | 102 |
| 30..60cm | silt | % | 12–23 | 1–37 | 102 |
| 30..60cm | bd.core | kg/m3 | 1480–1540 | 1280–1730 | 102 |
| 30..60cm | soc | g/kg | 1–6.1 | 0–41.5 | 102 |
| 30..60cm | ph.h2o | pH | 8.4–8.8 | 8–9.3 | 102 |
| 60..100cm | clay | % | 11–21 | 0–35 | 102 |
| 60..100cm | sand | % | 55–76 | 28–95 | 102 |
| 60..100cm | silt | % | 13–24 | 1–40 | 102 |
| 60..100cm | bd.core | kg/m3 | 1530–1590 | 1300–1770 | 102 |
| 60..100cm | soc | g/kg | 0.9–4.4 | 0–30.8 | 102 |
| 60..100cm | ph.h2o | pH | 8.4–8.8 | 7.9–9.4 | 102 |
