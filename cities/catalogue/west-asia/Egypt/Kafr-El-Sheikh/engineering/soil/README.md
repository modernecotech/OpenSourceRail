# Kafr-El-Sheikh civil soil screening

47 route/station sample locations; 47 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 17 |
| fine-soil-plasticity-and-shrink-swell-tests | 46 |
| granular-density-and-groundwater-tests | 47 |
| organic-content-and-compressibility-tests | 5 |

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
| 0..30cm | clay | % | 19–25 | 6–40 | 47 |
| 0..30cm | sand | % | 47–59 | 18–87 | 47 |
| 0..30cm | silt | % | 22–28 | 8–44 | 47 |
| 0..30cm | bd.core | kg/m3 | 1100–1440 | 810–1630 | 47 |
| 0..30cm | soc | g/kg | 2.3–23.7 | 1–69.1 | 47 |
| 0..30cm | ph.h2o | pH | 7.6–8.3 | 6.7–8.9 | 47 |
| 30..60cm | clay | % | 20–26 | 6–41 | 47 |
| 30..60cm | sand | % | 47–59 | 17–85 | 47 |
| 30..60cm | silt | % | 21–27 | 5–43 | 47 |
| 30..60cm | bd.core | kg/m3 | 1230–1540 | 910–1760 | 47 |
| 30..60cm | soc | g/kg | 1.4–14.5 | 0–43.5 | 47 |
| 30..60cm | ph.h2o | pH | 7.2–8.3 | 5.2–9.1 | 47 |
| 60..100cm | clay | % | 20–26 | 6–40 | 47 |
| 60..100cm | sand | % | 47–59 | 17–87 | 47 |
| 60..100cm | silt | % | 21–27 | 4–43 | 47 |
| 60..100cm | bd.core | kg/m3 | 1260–1570 | 760–1900 | 47 |
| 60..100cm | soc | g/kg | 1.2–10.4 | 0.1–38.1 | 47 |
| 60..100cm | ph.h2o | pH | 6.8–8.3 | 3.3–9.4 | 47 |
