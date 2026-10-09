# Arua civil soil screening

557 route/station sample locations; 557 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 548 |
| fine-soil-plasticity-and-shrink-swell-tests | 557 |
| granular-density-and-groundwater-tests | 519 |

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
| 0..30cm | clay | % | 25–35 | 12–48 | 557 |
| 0..30cm | sand | % | 38–53 | 12–80 | 557 |
| 0..30cm | silt | % | 20–28 | 4–44 | 557 |
| 0..30cm | bd.core | kg/m3 | 1240–1420 | 1000–1600 | 557 |
| 0..30cm | soc | g/kg | 8.5–16.4 | 4.4–31.1 | 557 |
| 0..30cm | ph.h2o | pH | 5.9–6.6 | 5.1–7.5 | 557 |
| 30..60cm | clay | % | 27–35 | 12–49 | 557 |
| 30..60cm | sand | % | 38–51 | 11–82 | 557 |
| 30..60cm | silt | % | 19–27 | 1–47 | 557 |
| 30..60cm | bd.core | kg/m3 | 1300–1470 | 1110–1700 | 557 |
| 30..60cm | soc | g/kg | 4.2–7.5 | 2–13.8 | 557 |
| 30..60cm | ph.h2o | pH | 6–6.7 | 5.2–7.5 | 557 |
| 60..100cm | clay | % | 29–35 | 12–50 | 557 |
| 60..100cm | sand | % | 40–50 | 11–83 | 557 |
| 60..100cm | silt | % | 19–27 | 2–47 | 557 |
| 60..100cm | bd.core | kg/m3 | 1290–1520 | 1040–1760 | 557 |
| 60..100cm | soc | g/kg | 3.4–6.1 | 1.5–12 | 557 |
| 60..100cm | ph.h2o | pH | 6–6.8 | 4.8–8.2 | 557 |
