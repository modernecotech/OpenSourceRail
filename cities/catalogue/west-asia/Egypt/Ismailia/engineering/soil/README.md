# Ismailia civil soil screening

1,778 route/station sample locations; 1,461 complete profiles; 317 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 88 |
| coverage-gap | 317 |
| fine-soil-plasticity-and-shrink-swell-tests | 686 |
| granular-density-and-groundwater-tests | 1461 |

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
| 0..30cm | clay | % | 7–23 | 0–40 | 1461 |
| 0..30cm | sand | % | 50–83 | 18–95 | 1461 |
| 0..30cm | silt | % | 10–27 | 3–43 | 1461 |
| 0..30cm | bd.core | kg/m3 | 1390–1530 | 1170–1720 | 1461 |
| 0..30cm | soc | g/kg | 1.7–8.7 | 0.6–23.4 | 1461 |
| 0..30cm | ph.h2o | pH | 7.6–8.8 | 6.4–9.5 | 1461 |
| 30..60cm | clay | % | 7–24 | 0–42 | 1461 |
| 30..60cm | sand | % | 50–85 | 19–96 | 1461 |
| 30..60cm | silt | % | 8–27 | 2–42 | 1461 |
| 30..60cm | bd.core | kg/m3 | 1480–1590 | 1230–1820 | 1461 |
| 30..60cm | soc | g/kg | 1–4.4 | 0–10.4 | 1461 |
| 30..60cm | ph.h2o | pH | 7.3–9.1 | 5.1–9.8 | 1461 |
| 60..100cm | clay | % | 6–24 | 0–41 | 1461 |
| 60..100cm | sand | % | 50–85 | 19–97 | 1461 |
| 60..100cm | silt | % | 8–27 | 1–43 | 1461 |
| 60..100cm | bd.core | kg/m3 | 1470–1620 | 1210–1930 | 1461 |
| 60..100cm | soc | g/kg | 0.8–3.2 | 0–8.2 | 1461 |
| 60..100cm | ph.h2o | pH | 7–9.1 | 3.3–9.8 | 1461 |
