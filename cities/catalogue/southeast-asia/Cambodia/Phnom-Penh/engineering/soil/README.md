# Phnom-Penh civil soil screening

3,395 route/station sample locations; 3,352 complete profiles; 43 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 175 |
| coverage-gap | 43 |
| fine-soil-plasticity-and-shrink-swell-tests | 3352 |
| granular-density-and-groundwater-tests | 2606 |
| organic-content-and-compressibility-tests | 5 |
| silt-moisture-frost-and-erosion-review | 153 |

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
| 0..30cm | clay | % | 22–35 | 3–48 | 3352 |
| 0..30cm | sand | % | 27–55 | 5–90 | 3352 |
| 0..30cm | silt | % | 22–39 | 3–54 | 3352 |
| 0..30cm | bd.core | kg/m3 | 980–1470 | 680–1690 | 3352 |
| 0..30cm | soc | g/kg | 3.6–17.4 | 0.9–40.2 | 3352 |
| 0..30cm | ph.h2o | pH | 6.1–7.1 | 5.2–8.3 | 3352 |
| 30..60cm | clay | % | 24–36 | 3–51 | 3352 |
| 30..60cm | sand | % | 29–53 | 6–91 | 3352 |
| 30..60cm | silt | % | 22–36 | 1–51 | 3352 |
| 30..60cm | bd.core | kg/m3 | 970–1500 | 700–1750 | 3352 |
| 30..60cm | soc | g/kg | 2.7–16.9 | 0.8–39.6 | 3352 |
| 30..60cm | ph.h2o | pH | 6.3–7.4 | 5.5–8.4 | 3352 |
| 60..100cm | clay | % | 25–35 | 3–51 | 3352 |
| 60..100cm | sand | % | 30–52 | 6–91 | 3352 |
| 60..100cm | silt | % | 22–35 | 1–51 | 3352 |
| 60..100cm | bd.core | kg/m3 | 940–1530 | 490–1790 | 3352 |
| 60..100cm | soc | g/kg | 2.1–13.5 | 0.2–50.5 | 3352 |
| 60..100cm | ph.h2o | pH | 6.7–7.6 | 5.4–9 | 3352 |
