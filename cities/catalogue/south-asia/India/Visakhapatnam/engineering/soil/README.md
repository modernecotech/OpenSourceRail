# Visakhapatnam civil soil screening

585 route/station sample locations; 578 complete profiles; 7 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 7 |
| fine-soil-plasticity-and-shrink-swell-tests | 578 |
| granular-density-and-groundwater-tests | 573 |

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
| 0..30cm | clay | % | 20–33 | 2–49 | 578 |
| 0..30cm | sand | % | 38–62 | 11–91 | 578 |
| 0..30cm | silt | % | 17–30 | 1–49 | 578 |
| 0..30cm | bd.core | kg/m3 | 1210–1500 | 910–1700 | 578 |
| 0..30cm | soc | g/kg | 5.1–13.9 | 1.4–30.2 | 578 |
| 0..30cm | ph.h2o | pH | 6.5–7.3 | 5.5–8.4 | 578 |
| 30..60cm | clay | % | 21–36 | 1–52 | 578 |
| 30..60cm | sand | % | 39–63 | 8–94 | 578 |
| 30..60cm | silt | % | 15–29 | 0–49 | 578 |
| 30..60cm | bd.core | kg/m3 | 1200–1520 | 750–1770 | 578 |
| 30..60cm | soc | g/kg | 2.8–9 | 0.9–28.7 | 578 |
| 30..60cm | ph.h2o | pH | 6.7–7.5 | 5.6–8.5 | 578 |
| 60..100cm | clay | % | 21–36 | 2–51 | 578 |
| 60..100cm | sand | % | 38–64 | 9–94 | 578 |
| 60..100cm | silt | % | 15–28 | 0–49 | 578 |
| 60..100cm | bd.core | kg/m3 | 1110–1540 | 460–1820 | 578 |
| 60..100cm | soc | g/kg | 2.1–8.3 | 0.7–25.4 | 578 |
| 60..100cm | ph.h2o | pH | 6.8–7.7 | 5.7–8.8 | 578 |
