# Luxor civil soil screening

83 route/station sample locations; 65 complete profiles; 18 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 28 |
| coverage-gap | 18 |
| fine-soil-plasticity-and-shrink-swell-tests | 56 |
| granular-density-and-groundwater-tests | 65 |
| organic-content-and-compressibility-tests | 12 |

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
| 0..30cm | clay | % | 10–25 | 1–39 | 65 |
| 0..30cm | sand | % | 43–73 | 13–92 | 65 |
| 0..30cm | silt | % | 17–31 | 5–49 | 65 |
| 0..30cm | bd.core | kg/m3 | 1380–1500 | 1060–1720 | 65 |
| 0..30cm | soc | g/kg | 3.6–9.3 | 0.7–28.5 | 65 |
| 0..30cm | ph.h2o | pH | 7–8.1 | 5–9.3 | 65 |
| 30..60cm | clay | % | 12–27 | 1–43 | 65 |
| 30..60cm | sand | % | 43–72 | 9–92 | 65 |
| 30..60cm | silt | % | 17–31 | 4–47 | 65 |
| 30..60cm | bd.core | kg/m3 | 1390–1570 | 1160–1750 | 65 |
| 30..60cm | soc | g/kg | 2.2–16.9 | 0.4–80.5 | 65 |
| 30..60cm | ph.h2o | pH | 7.1–8.4 | 5–9.8 | 65 |
| 60..100cm | clay | % | 12–26 | 1–42 | 65 |
| 60..100cm | sand | % | 43–71 | 12–91 | 65 |
| 60..100cm | silt | % | 18–31 | 4–47 | 65 |
| 60..100cm | bd.core | kg/m3 | 1440–1650 | 1160–1900 | 65 |
| 60..100cm | soc | g/kg | 2–10.6 | 0.5–48.1 | 65 |
| 60..100cm | ph.h2o | pH | 6.9–8.4 | 3.5–9.8 | 65 |
