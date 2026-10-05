# Hyderabad-Pk civil soil screening

893 route/station sample locations; 883 complete profiles; 10 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 31 |
| coverage-gap | 10 |
| fine-soil-plasticity-and-shrink-swell-tests | 453 |
| granular-density-and-groundwater-tests | 883 |

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
| 0..30cm | clay | % | 13–22 | 0–34 | 883 |
| 0..30cm | sand | % | 49–68 | 29–94 | 883 |
| 0..30cm | silt | % | 19–29 | 4–41 | 883 |
| 0..30cm | bd.core | kg/m3 | 1420–1540 | 1240–1700 | 883 |
| 0..30cm | soc | g/kg | 2.2–5.8 | 0.6–12.8 | 883 |
| 0..30cm | ph.h2o | pH | 6.5–8.3 | 4.9–9.1 | 883 |
| 30..60cm | clay | % | 15–24 | 0–42 | 883 |
| 30..60cm | sand | % | 50–68 | 21–97 | 883 |
| 30..60cm | silt | % | 16–27 | 1–44 | 883 |
| 30..60cm | bd.core | kg/m3 | 1450–1570 | 1230–1750 | 883 |
| 30..60cm | soc | g/kg | 1.2–3.8 | 0–10.9 | 883 |
| 30..60cm | ph.h2o | pH | 6.3–8.8 | 4.3–9.6 | 883 |
| 60..100cm | clay | % | 16–24 | 0–42 | 883 |
| 60..100cm | sand | % | 51–68 | 17–96 | 883 |
| 60..100cm | silt | % | 16–26 | 0–44 | 883 |
| 60..100cm | bd.core | kg/m3 | 1450–1580 | 1240–1850 | 883 |
| 60..100cm | soc | g/kg | 1–3.2 | 0–7.8 | 883 |
| 60..100cm | ph.h2o | pH | 6.4–8.9 | 4.3–10.2 | 883 |
