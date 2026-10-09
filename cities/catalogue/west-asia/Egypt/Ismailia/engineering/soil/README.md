# Ismailia civil soil screening

535 route/station sample locations; 477 complete profiles; 58 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 50 |
| coverage-gap | 58 |
| fine-soil-plasticity-and-shrink-swell-tests | 255 |
| granular-density-and-groundwater-tests | 477 |

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
| 0..30cm | clay | % | 7–24 | 1–39 | 477 |
| 0..30cm | sand | % | 48–82 | 18–92 | 477 |
| 0..30cm | silt | % | 11–28 | 4–43 | 477 |
| 0..30cm | bd.core | kg/m3 | 1340–1540 | 1100–1730 | 477 |
| 0..30cm | soc | g/kg | 1.7–9.9 | 0.6–29.6 | 477 |
| 0..30cm | ph.h2o | pH | 7.4–8.7 | 6.3–9.4 | 477 |
| 30..60cm | clay | % | 7–24 | 0–42 | 477 |
| 30..60cm | sand | % | 49–84 | 16–96 | 477 |
| 30..60cm | silt | % | 9–27 | 2–42 | 477 |
| 30..60cm | bd.core | kg/m3 | 1470–1600 | 1220–1810 | 477 |
| 30..60cm | soc | g/kg | 1.1–5.7 | 0.1–19.7 | 477 |
| 30..60cm | ph.h2o | pH | 6.8–8.9 | 4.2–9.8 | 477 |
| 60..100cm | clay | % | 7–24 | 0–41 | 477 |
| 60..100cm | sand | % | 49–84 | 18–96 | 477 |
| 60..100cm | silt | % | 9–27 | 1–43 | 477 |
| 60..100cm | bd.core | kg/m3 | 1460–1630 | 1160–1930 | 477 |
| 60..100cm | soc | g/kg | 0.8–4.7 | 0–15.5 | 477 |
| 60..100cm | ph.h2o | pH | 6.4–9 | 3.3–9.8 | 477 |
