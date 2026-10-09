# Sohag civil soil screening

340 route/station sample locations; 333 complete profiles; 7 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 103 |
| coverage-gap | 7 |
| fine-soil-plasticity-and-shrink-swell-tests | 329 |
| granular-density-and-groundwater-tests | 333 |
| organic-content-and-compressibility-tests | 21 |

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
| 0..30cm | clay | % | 14–26 | 0–40 | 333 |
| 0..30cm | sand | % | 43–68 | 13–91 | 333 |
| 0..30cm | silt | % | 19–32 | 6–49 | 333 |
| 0..30cm | bd.core | kg/m3 | 1380–1510 | 1060–1670 | 333 |
| 0..30cm | soc | g/kg | 3.3–10.2 | 0.9–31.1 | 333 |
| 0..30cm | ph.h2o | pH | 7–8.2 | 5–9.4 | 333 |
| 30..60cm | clay | % | 16–28 | 0–44 | 333 |
| 30..60cm | sand | % | 42–66 | 11–93 | 333 |
| 30..60cm | silt | % | 18–30 | 4–47 | 333 |
| 30..60cm | bd.core | kg/m3 | 1390–1570 | 1160–1760 | 333 |
| 30..60cm | soc | g/kg | 2–13.3 | 0.3–61.8 | 333 |
| 30..60cm | ph.h2o | pH | 7.2–8.5 | 4.9–9.8 | 333 |
| 60..100cm | clay | % | 16–28 | 0–44 | 333 |
| 60..100cm | sand | % | 42–65 | 11–92 | 333 |
| 60..100cm | silt | % | 19–31 | 4–46 | 333 |
| 60..100cm | bd.core | kg/m3 | 1440–1640 | 1210–1910 | 333 |
| 60..100cm | soc | g/kg | 1.8–7.8 | 0.2–41.5 | 333 |
| 60..100cm | ph.h2o | pH | 7.1–8.5 | 3.7–9.8 | 333 |
