# Fayoum civil soil screening

123 route/station sample locations; 112 complete profiles; 11 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 6 |
| coverage-gap | 11 |
| fine-soil-plasticity-and-shrink-swell-tests | 99 |
| granular-density-and-groundwater-tests | 112 |

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
| 0..30cm | clay | % | 14–24 | 4–43 | 112 |
| 0..30cm | sand | % | 46–66 | 10–89 | 112 |
| 0..30cm | silt | % | 19–30 | 7–48 | 112 |
| 0..30cm | bd.core | kg/m3 | 1420–1540 | 1210–1740 | 112 |
| 0..30cm | soc | g/kg | 3.3–6.3 | 1.1–16.3 | 112 |
| 0..30cm | ph.h2o | pH | 7.4–8.5 | 6.1–9.1 | 112 |
| 30..60cm | clay | % | 15–25 | 3–43 | 112 |
| 30..60cm | sand | % | 47–67 | 10–94 | 112 |
| 30..60cm | silt | % | 18–29 | 4–47 | 112 |
| 30..60cm | bd.core | kg/m3 | 1490–1590 | 1300–1800 | 112 |
| 30..60cm | soc | g/kg | 1.9–3.9 | 0.1–9.2 | 112 |
| 30..60cm | ph.h2o | pH | 7.5–8.7 | 5.6–9.6 | 112 |
| 60..100cm | clay | % | 15–25 | 3–41 | 112 |
| 60..100cm | sand | % | 47–68 | 14–94 | 112 |
| 60..100cm | silt | % | 18–28 | 4–46 | 112 |
| 60..100cm | bd.core | kg/m3 | 1510–1650 | 1280–1910 | 112 |
| 60..100cm | soc | g/kg | 1.5–2.8 | 0.1–7.1 | 112 |
| 60..100cm | ph.h2o | pH | 7.3–8.7 | 3.5–9.6 | 112 |
