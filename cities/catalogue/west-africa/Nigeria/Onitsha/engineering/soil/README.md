# Onitsha civil soil screening

369 route/station sample locations; 340 complete profiles; 29 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 340 |
| coverage-gap | 29 |
| fine-soil-plasticity-and-shrink-swell-tests | 340 |
| granular-density-and-groundwater-tests | 292 |

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
| 0..30cm | clay | % | 24–37 | 6–51 | 340 |
| 0..30cm | sand | % | 41–64 | 16–92 | 340 |
| 0..30cm | silt | % | 10–23 | 0–37 | 340 |
| 0..30cm | bd.core | kg/m3 | 1120–1480 | 760–1610 | 340 |
| 0..30cm | soc | g/kg | 4.9–15.9 | 1.7–32.3 | 340 |
| 0..30cm | ph.h2o | pH | 5.2–6.1 | 4.6–6.9 | 340 |
| 30..60cm | clay | % | 26–39 | 6–54 | 340 |
| 30..60cm | sand | % | 42–63 | 17–93 | 340 |
| 30..60cm | silt | % | 8–22 | 0–38 | 340 |
| 30..60cm | bd.core | kg/m3 | 1120–1490 | 660–1680 | 340 |
| 30..60cm | soc | g/kg | 2.6–11 | 0.8–33.8 | 340 |
| 30..60cm | ph.h2o | pH | 5.2–6.2 | 4.6–7 | 340 |
| 60..100cm | clay | % | 28–39 | 6–54 | 340 |
| 60..100cm | sand | % | 42–63 | 13–93 | 340 |
| 60..100cm | silt | % | 8–22 | 0–39 | 340 |
| 60..100cm | bd.core | kg/m3 | 1150–1510 | 590–1700 | 340 |
| 60..100cm | soc | g/kg | 2.5–10.8 | 0.5–48.2 | 340 |
| 60..100cm | ph.h2o | pH | 5.2–6.3 | 4.6–7.3 | 340 |
