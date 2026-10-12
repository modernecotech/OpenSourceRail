# Mwanza civil soil screening

5,482 route/station sample locations; 5,472 complete profiles; 10 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 5420 |
| coverage-gap | 10 |
| fine-soil-plasticity-and-shrink-swell-tests | 5472 |
| granular-density-and-groundwater-tests | 4566 |

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
| 0..30cm | clay | % | 24–36 | 10–49 | 5472 |
| 0..30cm | sand | % | 37–60 | 13–84 | 5472 |
| 0..30cm | silt | % | 16–27 | 3–44 | 5472 |
| 0..30cm | bd.core | kg/m3 | 1170–1540 | 760–1720 | 5472 |
| 0..30cm | soc | g/kg | 6–16.8 | 2.1–32.1 | 5472 |
| 0..30cm | ph.h2o | pH | 5.7–6.9 | 4.8–7.9 | 5472 |
| 30..60cm | clay | % | 25–37 | 8–52 | 5472 |
| 30..60cm | sand | % | 39–60 | 14–89 | 5472 |
| 30..60cm | silt | % | 14–25 | 0–43 | 5472 |
| 30..60cm | bd.core | kg/m3 | 1180–1550 | 800–1740 | 5472 |
| 30..60cm | soc | g/kg | 4–13.5 | 1.5–32.4 | 5472 |
| 30..60cm | ph.h2o | pH | 5.8–6.9 | 4.8–8 | 5472 |
| 60..100cm | clay | % | 25–38 | 7–54 | 5472 |
| 60..100cm | sand | % | 39–61 | 12–89 | 5472 |
| 60..100cm | silt | % | 13–25 | 0–44 | 5472 |
| 60..100cm | bd.core | kg/m3 | 1160–1530 | 690–1780 | 5472 |
| 60..100cm | soc | g/kg | 3.6–13.1 | 1.2–47.7 | 5472 |
| 60..100cm | ph.h2o | pH | 5.9–7 | 4.7–8.4 | 5472 |
