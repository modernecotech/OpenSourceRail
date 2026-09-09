# Lobito civil soil screening

84 route/station sample locations; 84 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 33 |
| fine-soil-plasticity-and-shrink-swell-tests | 53 |
| granular-density-and-groundwater-tests | 84 |

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
| 0..30cm | clay | % | 17–29 | 0–42 | 84 |
| 0..30cm | sand | % | 46–68 | 23–93 | 84 |
| 0..30cm | silt | % | 15–26 | 0–42 | 84 |
| 0..30cm | bd.core | kg/m3 | 1290–1450 | 1000–1650 | 84 |
| 0..30cm | soc | g/kg | 3.9–7.9 | 1.5–14 | 84 |
| 0..30cm | ph.h2o | pH | 7–7.9 | 5.9–8.5 | 84 |
| 30..60cm | clay | % | 18–30 | 1–44 | 84 |
| 30..60cm | sand | % | 45–66 | 20–94 | 84 |
| 30..60cm | silt | % | 16–26 | 0–45 | 84 |
| 30..60cm | bd.core | kg/m3 | 1270–1500 | 960–1680 | 84 |
| 30..60cm | soc | g/kg | 2.7–7.2 | 1.1–19.4 | 84 |
| 30..60cm | ph.h2o | pH | 7–7.9 | 5.4–8.8 | 84 |
| 60..100cm | clay | % | 18–30 | 0–44 | 84 |
| 60..100cm | sand | % | 45–65 | 20–94 | 84 |
| 60..100cm | silt | % | 17–26 | 0–45 | 84 |
| 60..100cm | bd.core | kg/m3 | 1300–1520 | 800–1830 | 84 |
| 60..100cm | soc | g/kg | 2.1–8.2 | 0.5–34 | 84 |
| 60..100cm | ph.h2o | pH | 7.1–7.9 | 5.3–8.9 | 84 |
