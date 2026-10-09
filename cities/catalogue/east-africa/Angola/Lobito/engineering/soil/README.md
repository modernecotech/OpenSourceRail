# Lobito civil soil screening

447 route/station sample locations; 441 complete profiles; 6 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 68 |
| coverage-gap | 6 |
| fine-soil-plasticity-and-shrink-swell-tests | 392 |
| granular-density-and-groundwater-tests | 441 |

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
| 0..30cm | clay | % | 17–28 | 0–43 | 441 |
| 0..30cm | sand | % | 49–67 | 22–93 | 441 |
| 0..30cm | silt | % | 14–24 | 0–43 | 441 |
| 0..30cm | bd.core | kg/m3 | 1280–1450 | 910–1680 | 441 |
| 0..30cm | soc | g/kg | 4.1–9.1 | 1.7–20.7 | 441 |
| 0..30cm | ph.h2o | pH | 6.8–7.9 | 5.5–8.6 | 441 |
| 30..60cm | clay | % | 18–30 | 2–44 | 441 |
| 30..60cm | sand | % | 49–65 | 18–94 | 441 |
| 30..60cm | silt | % | 15–24 | 0–46 | 441 |
| 30..60cm | bd.core | kg/m3 | 1240–1500 | 890–1670 | 441 |
| 30..60cm | soc | g/kg | 2.6–7.6 | 1.1–21.4 | 441 |
| 30..60cm | ph.h2o | pH | 6.9–8 | 5.4–8.8 | 441 |
| 60..100cm | clay | % | 18–31 | 1–45 | 441 |
| 60..100cm | sand | % | 48–64 | 18–94 | 441 |
| 60..100cm | silt | % | 15–24 | 0–46 | 441 |
| 60..100cm | bd.core | kg/m3 | 1250–1520 | 760–1830 | 441 |
| 60..100cm | soc | g/kg | 1.9–8.8 | 0.4–42 | 441 |
| 60..100cm | ph.h2o | pH | 7–7.9 | 5.3–9.1 | 441 |
