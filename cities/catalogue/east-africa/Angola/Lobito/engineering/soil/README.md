# Lobito civil soil screening

250 route/station sample locations; 244 complete profiles; 6 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 33 |
| coverage-gap | 6 |
| fine-soil-plasticity-and-shrink-swell-tests | 207 |
| granular-density-and-groundwater-tests | 244 |

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
| 0..30cm | clay | % | 18–27 | 0–40 | 244 |
| 0..30cm | sand | % | 49–67 | 25–93 | 244 |
| 0..30cm | silt | % | 15–24 | 0–39 | 244 |
| 0..30cm | bd.core | kg/m3 | 1290–1440 | 910–1670 | 244 |
| 0..30cm | soc | g/kg | 4–8.8 | 1.7–20.4 | 244 |
| 0..30cm | ph.h2o | pH | 7–7.9 | 5.9–8.6 | 244 |
| 30..60cm | clay | % | 18–28 | 2–44 | 244 |
| 30..60cm | sand | % | 49–65 | 18–94 | 244 |
| 30..60cm | silt | % | 15–23 | 0–43 | 244 |
| 30..60cm | bd.core | kg/m3 | 1260–1500 | 930–1670 | 244 |
| 30..60cm | soc | g/kg | 2.6–6.6 | 1.1–19.2 | 244 |
| 30..60cm | ph.h2o | pH | 7–8 | 5.4–8.8 | 244 |
| 60..100cm | clay | % | 18–28 | 1–44 | 244 |
| 60..100cm | sand | % | 49–63 | 18–94 | 244 |
| 60..100cm | silt | % | 15–24 | 0–46 | 244 |
| 60..100cm | bd.core | kg/m3 | 1250–1520 | 790–1830 | 244 |
| 60..100cm | soc | g/kg | 1.9–8.8 | 0.4–42 | 244 |
| 60..100cm | ph.h2o | pH | 7.1–7.9 | 5.3–9.1 | 244 |
