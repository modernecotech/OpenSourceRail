# Hyderabad-Pk civil soil screening

436 route/station sample locations; 426 complete profiles; 10 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 21 |
| coverage-gap | 10 |
| fine-soil-plasticity-and-shrink-swell-tests | 178 |
| granular-density-and-groundwater-tests | 426 |

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
| 0..30cm | clay | % | 13–22 | 0–34 | 426 |
| 0..30cm | sand | % | 50–69 | 29–93 | 426 |
| 0..30cm | silt | % | 18–28 | 3–40 | 426 |
| 0..30cm | bd.core | kg/m3 | 1430–1540 | 1250–1690 | 426 |
| 0..30cm | soc | g/kg | 1.9–5.3 | 0.6–11.5 | 426 |
| 0..30cm | ph.h2o | pH | 6.5–8.3 | 4.8–9.2 | 426 |
| 30..60cm | clay | % | 14–23 | 0–38 | 426 |
| 30..60cm | sand | % | 51–69 | 20–97 | 426 |
| 30..60cm | silt | % | 16–26 | 1–43 | 426 |
| 30..60cm | bd.core | kg/m3 | 1470–1570 | 1290–1750 | 426 |
| 30..60cm | soc | g/kg | 1.1–3.6 | 0–8.3 | 426 |
| 30..60cm | ph.h2o | pH | 6.4–8.8 | 4.3–9.6 | 426 |
| 60..100cm | clay | % | 15–24 | 0–40 | 426 |
| 60..100cm | sand | % | 51–69 | 19–97 | 426 |
| 60..100cm | silt | % | 16–26 | 0–47 | 426 |
| 60..100cm | bd.core | kg/m3 | 1470–1580 | 1240–1820 | 426 |
| 60..100cm | soc | g/kg | 1–3.4 | 0–7.5 | 426 |
| 60..100cm | ph.h2o | pH | 6.5–8.9 | 4.3–10.2 | 426 |
