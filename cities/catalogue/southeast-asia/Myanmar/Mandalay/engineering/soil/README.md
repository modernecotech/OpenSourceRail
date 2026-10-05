# Mandalay civil soil screening

1,917 route/station sample locations; 1,835 complete profiles; 82 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 312 |
| coverage-gap | 82 |
| fine-soil-plasticity-and-shrink-swell-tests | 1785 |
| granular-density-and-groundwater-tests | 1835 |
| silt-moisture-frost-and-erosion-review | 3 |

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
| 0..30cm | clay | % | 19–30 | 3–46 | 1835 |
| 0..30cm | sand | % | 42–66 | 11–92 | 1835 |
| 0..30cm | silt | % | 15–30 | 0–49 | 1835 |
| 0..30cm | bd.core | kg/m3 | 1280–1500 | 960–1700 | 1835 |
| 0..30cm | soc | g/kg | 4.4–15.5 | 1.9–36.8 | 1835 |
| 0..30cm | ph.h2o | pH | 6.1–7.4 | 5.2–8.3 | 1835 |
| 30..60cm | clay | % | 20–31 | 3–49 | 1835 |
| 30..60cm | sand | % | 42–64 | 9–93 | 1835 |
| 30..60cm | silt | % | 15–28 | 0–49 | 1835 |
| 30..60cm | bd.core | kg/m3 | 1330–1550 | 920–1800 | 1835 |
| 30..60cm | soc | g/kg | 3–10.2 | 0.9–31.7 | 1835 |
| 30..60cm | ph.h2o | pH | 6.3–7.4 | 5.3–8.4 | 1835 |
| 60..100cm | clay | % | 20–31 | 3–50 | 1835 |
| 60..100cm | sand | % | 42–65 | 7–92 | 1835 |
| 60..100cm | silt | % | 15–28 | 0–53 | 1835 |
| 60..100cm | bd.core | kg/m3 | 1370–1610 | 750–1860 | 1835 |
| 60..100cm | soc | g/kg | 2.3–8.5 | 0.7–32.8 | 1835 |
| 60..100cm | ph.h2o | pH | 6.5–7.6 | 5.1–8.4 | 1835 |
