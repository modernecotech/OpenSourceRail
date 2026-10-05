# Ismailia civil soil screening

145 route/station sample locations; 120 complete profiles; 25 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 6 |
| coverage-gap | 25 |
| fine-soil-plasticity-and-shrink-swell-tests | 47 |
| granular-density-and-groundwater-tests | 120 |

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
| 0..30cm | clay | % | 7–22 | 1–38 | 120 |
| 0..30cm | sand | % | 52–82 | 21–92 | 120 |
| 0..30cm | silt | % | 11–26 | 4–42 | 120 |
| 0..30cm | bd.core | kg/m3 | 1420–1540 | 1220–1700 | 120 |
| 0..30cm | soc | g/kg | 1.8–8.4 | 0.6–22.2 | 120 |
| 0..30cm | ph.h2o | pH | 7.6–8.7 | 6.4–9.4 | 120 |
| 30..60cm | clay | % | 7–23 | 0–41 | 120 |
| 30..60cm | sand | % | 52–84 | 22–96 | 120 |
| 30..60cm | silt | % | 9–25 | 2–42 | 120 |
| 30..60cm | bd.core | kg/m3 | 1490–1580 | 1290–1800 | 120 |
| 30..60cm | soc | g/kg | 1.1–4.6 | 0.1–10.1 | 120 |
| 30..60cm | ph.h2o | pH | 7.5–8.9 | 4.5–9.8 | 120 |
| 60..100cm | clay | % | 7–23 | 0–41 | 120 |
| 60..100cm | sand | % | 52–84 | 23–96 | 120 |
| 60..100cm | silt | % | 9–26 | 1–43 | 120 |
| 60..100cm | bd.core | kg/m3 | 1490–1610 | 1250–1920 | 120 |
| 60..100cm | soc | g/kg | 0.8–3.1 | 0–7.2 | 120 |
| 60..100cm | ph.h2o | pH | 7.3–9 | 3.5–9.8 | 120 |
