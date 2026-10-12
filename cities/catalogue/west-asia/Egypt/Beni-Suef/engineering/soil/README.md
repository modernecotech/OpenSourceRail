# Beni-Suef civil soil screening

498 route/station sample locations; 461 complete profiles; 37 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 78 |
| coverage-gap | 37 |
| fine-soil-plasticity-and-shrink-swell-tests | 171 |
| granular-density-and-groundwater-tests | 461 |

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
| 0..30cm | clay | % | 14–23 | 1–39 | 461 |
| 0..30cm | sand | % | 49–68 | 13–90 | 461 |
| 0..30cm | silt | % | 19–29 | 6–47 | 461 |
| 0..30cm | bd.core | kg/m3 | 1360–1500 | 1140–1690 | 461 |
| 0..30cm | soc | g/kg | 2.4–5.8 | 0.6–14.4 | 461 |
| 0..30cm | ph.h2o | pH | 7.2–8.5 | 5.7–9.5 | 461 |
| 30..60cm | clay | % | 13–24 | 2–42 | 461 |
| 30..60cm | sand | % | 49–70 | 13–94 | 461 |
| 30..60cm | silt | % | 16–27 | 2–48 | 461 |
| 30..60cm | bd.core | kg/m3 | 1440–1560 | 1160–1780 | 461 |
| 30..60cm | soc | g/kg | 1.7–5.1 | 0–14.4 | 461 |
| 30..60cm | ph.h2o | pH | 7.4–8.6 | 5.1–9.8 | 461 |
| 60..100cm | clay | % | 13–24 | 1–42 | 461 |
| 60..100cm | sand | % | 48–71 | 14–96 | 461 |
| 60..100cm | silt | % | 16–27 | 2–46 | 461 |
| 60..100cm | bd.core | kg/m3 | 1460–1620 | 1210–1900 | 461 |
| 60..100cm | soc | g/kg | 1.4–4.6 | 0.1–13.2 | 461 |
| 60..100cm | ph.h2o | pH | 7.3–8.6 | 4.1–9.8 | 461 |
