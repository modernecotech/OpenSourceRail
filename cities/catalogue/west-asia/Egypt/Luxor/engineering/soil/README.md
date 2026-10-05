# Luxor civil soil screening

112 route/station sample locations; 103 complete profiles; 9 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 54 |
| coverage-gap | 9 |
| fine-soil-plasticity-and-shrink-swell-tests | 89 |
| granular-density-and-groundwater-tests | 103 |
| organic-content-and-compressibility-tests | 27 |

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
| 0..30cm | clay | % | 10–26 | 1–40 | 103 |
| 0..30cm | sand | % | 42–73 | 12–92 | 103 |
| 0..30cm | silt | % | 17–33 | 5–49 | 103 |
| 0..30cm | bd.core | kg/m3 | 1380–1500 | 1060–1720 | 103 |
| 0..30cm | soc | g/kg | 3.6–11.3 | 0.7–30.1 | 103 |
| 0..30cm | ph.h2o | pH | 6.9–8.1 | 5–9.3 | 103 |
| 30..60cm | clay | % | 12–28 | 1–44 | 103 |
| 30..60cm | sand | % | 40–72 | 8–92 | 103 |
| 30..60cm | silt | % | 17–32 | 4–47 | 103 |
| 30..60cm | bd.core | kg/m3 | 1400–1560 | 1160–1750 | 103 |
| 30..60cm | soc | g/kg | 2.2–16.9 | 0.4–80.5 | 103 |
| 30..60cm | ph.h2o | pH | 6.9–8.4 | 4.4–9.8 | 103 |
| 60..100cm | clay | % | 12–27 | 1–42 | 103 |
| 60..100cm | sand | % | 40–71 | 11–92 | 103 |
| 60..100cm | silt | % | 18–32 | 4–47 | 103 |
| 60..100cm | bd.core | kg/m3 | 1450–1630 | 1180–1900 | 103 |
| 60..100cm | soc | g/kg | 1.9–10.6 | 0.5–48.1 | 103 |
| 60..100cm | ph.h2o | pH | 6.6–8.4 | 3.5–9.8 | 103 |
