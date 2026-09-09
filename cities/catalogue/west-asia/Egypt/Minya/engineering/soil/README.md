# Minya civil soil screening

103 route/station sample locations; 93 complete profiles; 10 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 45 |
| coverage-gap | 10 |
| fine-soil-plasticity-and-shrink-swell-tests | 47 |
| granular-density-and-groundwater-tests | 93 |

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
| 0..30cm | clay | % | 12–24 | 0–39 | 93 |
| 0..30cm | sand | % | 48–72 | 13–93 | 93 |
| 0..30cm | silt | % | 16–29 | 5–47 | 93 |
| 0..30cm | bd.core | kg/m3 | 1400–1510 | 1110–1690 | 93 |
| 0..30cm | soc | g/kg | 2.5–5 | 0.6–11.6 | 93 |
| 0..30cm | ph.h2o | pH | 7.2–8.3 | 5.2–9.5 | 93 |
| 30..60cm | clay | % | 13–25 | 0–43 | 93 |
| 30..60cm | sand | % | 47–71 | 12–98 | 93 |
| 30..60cm | silt | % | 16–27 | 1–46 | 93 |
| 30..60cm | bd.core | kg/m3 | 1460–1580 | 1180–1740 | 93 |
| 30..60cm | soc | g/kg | 1.6–3.4 | 0.1–12.9 | 93 |
| 30..60cm | ph.h2o | pH | 7.1–8.7 | 5–9.8 | 93 |
| 60..100cm | clay | % | 13–26 | 0–42 | 93 |
| 60..100cm | sand | % | 46–70 | 13–96 | 93 |
| 60..100cm | silt | % | 16–28 | 2–45 | 93 |
| 60..100cm | bd.core | kg/m3 | 1500–1620 | 1240–1900 | 93 |
| 60..100cm | soc | g/kg | 1.4–2.8 | 0.1–12.8 | 93 |
| 60..100cm | ph.h2o | pH | 7.2–8.7 | 4.8–9.8 | 93 |
