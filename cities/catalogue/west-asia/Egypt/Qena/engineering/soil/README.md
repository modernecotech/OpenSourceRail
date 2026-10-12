# Qena civil soil screening

742 route/station sample locations; 704 complete profiles; 38 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 294 |
| coverage-gap | 38 |
| fine-soil-plasticity-and-shrink-swell-tests | 546 |
| granular-density-and-groundwater-tests | 704 |
| organic-content-and-compressibility-tests | 236 |

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
| 0..30cm | clay | % | 13–24 | 0–40 | 704 |
| 0..30cm | sand | % | 46–66 | 12–90 | 704 |
| 0..30cm | silt | % | 21–31 | 6–49 | 704 |
| 0..30cm | bd.core | kg/m3 | 1360–1510 | 1030–1710 | 704 |
| 0..30cm | soc | g/kg | 3.5–10.9 | 1–34.6 | 704 |
| 0..30cm | ph.h2o | pH | 6.8–8.2 | 4.9–9.4 | 704 |
| 30..60cm | clay | % | 15–26 | 0–42 | 704 |
| 30..60cm | sand | % | 44–63 | 13–92 | 704 |
| 30..60cm | silt | % | 21–31 | 4–47 | 704 |
| 30..60cm | bd.core | kg/m3 | 1390–1590 | 1150–1780 | 704 |
| 30..60cm | soc | g/kg | 2.1–16.7 | 0.4–80.5 | 704 |
| 30..60cm | ph.h2o | pH | 7–8.4 | 4.3–9.8 | 704 |
| 60..100cm | clay | % | 15–25 | 0–42 | 704 |
| 60..100cm | sand | % | 44–64 | 12–92 | 704 |
| 60..100cm | silt | % | 21–31 | 4–49 | 704 |
| 60..100cm | bd.core | kg/m3 | 1440–1640 | 1140–1900 | 704 |
| 60..100cm | soc | g/kg | 2–10 | 0.3–49 | 704 |
| 60..100cm | ph.h2o | pH | 6.8–8.5 | 3.5–9.9 | 704 |
