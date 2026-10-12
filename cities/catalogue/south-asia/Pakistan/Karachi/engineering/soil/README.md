# Karachi civil soil screening

12,716 route/station sample locations; 12,702 complete profiles; 14 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 3495 |
| coverage-gap | 14 |
| fine-soil-plasticity-and-shrink-swell-tests | 5830 |
| granular-density-and-groundwater-tests | 12702 |

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
| 0..30cm | clay | % | 9–23 | 0–39 | 12702 |
| 0..30cm | sand | % | 54–81 | 21–99 | 12702 |
| 0..30cm | silt | % | 10–23 | 0–41 | 12702 |
| 0..30cm | bd.core | kg/m3 | 1210–1550 | 820–1730 | 12702 |
| 0..30cm | soc | g/kg | 2.2–15.9 | 0.5–46.7 | 12702 |
| 0..30cm | ph.h2o | pH | 6.8–8.5 | 4.9–9.5 | 12702 |
| 30..60cm | clay | % | 11–25 | 0–43 | 12702 |
| 30..60cm | sand | % | 52–79 | 18–99 | 12702 |
| 30..60cm | silt | % | 9–23 | 0–41 | 12702 |
| 30..60cm | bd.core | kg/m3 | 1170–1590 | 810–1780 | 12702 |
| 30..60cm | soc | g/kg | 1.1–13.2 | 0–40.2 | 12702 |
| 30..60cm | ph.h2o | pH | 6.7–8.9 | 4.3–9.8 | 12702 |
| 60..100cm | clay | % | 12–25 | 0–45 | 12702 |
| 60..100cm | sand | % | 52–79 | 15–99 | 12702 |
| 60..100cm | silt | % | 9–22 | 0–44 | 12702 |
| 60..100cm | bd.core | kg/m3 | 1130–1590 | 750–1800 | 12702 |
| 60..100cm | soc | g/kg | 0.9–12.1 | 0–41.5 | 12702 |
| 60..100cm | ph.h2o | pH | 6.7–8.9 | 3.7–9.9 | 12702 |
