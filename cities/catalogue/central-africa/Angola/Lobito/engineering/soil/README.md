# Lobito civil soil screening

1,119 route/station sample locations; 1,112 complete profiles; 7 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 95 |
| coverage-gap | 7 |
| fine-soil-plasticity-and-shrink-swell-tests | 826 |
| granular-density-and-groundwater-tests | 1112 |

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
| 0..30cm | clay | % | 17–29 | 0–44 | 1112 |
| 0..30cm | sand | % | 45–68 | 19–95 | 1112 |
| 0..30cm | silt | % | 15–27 | 0–42 | 1112 |
| 0..30cm | bd.core | kg/m3 | 1290–1450 | 940–1680 | 1112 |
| 0..30cm | soc | g/kg | 3.9–8.4 | 1.6–21 | 1112 |
| 0..30cm | ph.h2o | pH | 6.9–7.9 | 5.9–8.4 | 1112 |
| 30..60cm | clay | % | 17–30 | 0–45 | 1112 |
| 30..60cm | sand | % | 44–66 | 18–94 | 1112 |
| 30..60cm | silt | % | 15–26 | 0–47 | 1112 |
| 30..60cm | bd.core | kg/m3 | 1260–1510 | 950–1710 | 1112 |
| 30..60cm | soc | g/kg | 2.6–6.6 | 1.1–23.1 | 1112 |
| 30..60cm | ph.h2o | pH | 6.9–8 | 5.4–8.9 | 1112 |
| 60..100cm | clay | % | 18–30 | 0–46 | 1112 |
| 60..100cm | sand | % | 44–65 | 18–96 | 1112 |
| 60..100cm | silt | % | 15–26 | 0–47 | 1112 |
| 60..100cm | bd.core | kg/m3 | 1260–1530 | 790–1840 | 1112 |
| 60..100cm | soc | g/kg | 2–7.2 | 0.4–33 | 1112 |
| 60..100cm | ph.h2o | pH | 7–8 | 5.3–9.3 | 1112 |
