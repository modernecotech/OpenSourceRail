# Raipur civil soil screening

492 route/station sample locations; 492 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 488 |
| fine-soil-plasticity-and-shrink-swell-tests | 492 |
| granular-density-and-groundwater-tests | 492 |
| silt-moisture-frost-and-erosion-review | 142 |

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
| 0..30cm | clay | % | 19–26 | 0–41 | 492 |
| 0..30cm | sand | % | 43–58 | 16–90 | 492 |
| 0..30cm | silt | % | 21–32 | 2–50 | 492 |
| 0..30cm | bd.core | kg/m3 | 1210–1370 | 890–1660 | 492 |
| 0..30cm | soc | g/kg | 4.2–7.4 | 1.1–23 | 492 |
| 0..30cm | ph.h2o | pH | 6.1–6.6 | 5.1–7.9 | 492 |
| 30..60cm | clay | % | 21–27 | 0–44 | 492 |
| 30..60cm | sand | % | 42–57 | 12–90 | 492 |
| 30..60cm | silt | % | 21–31 | 2–53 | 492 |
| 30..60cm | bd.core | kg/m3 | 1290–1480 | 880–1740 | 492 |
| 30..60cm | soc | g/kg | 2.7–4.7 | 0.7–13.2 | 492 |
| 30..60cm | ph.h2o | pH | 6.2–6.8 | 5.4–8 | 492 |
| 60..100cm | clay | % | 21–28 | 1–44 | 492 |
| 60..100cm | sand | % | 42–58 | 8–89 | 492 |
| 60..100cm | silt | % | 20–31 | 0–53 | 492 |
| 60..100cm | bd.core | kg/m3 | 1330–1550 | 690–1850 | 492 |
| 60..100cm | soc | g/kg | 2–3.5 | 0.5–9.5 | 492 |
| 60..100cm | ph.h2o | pH | 6.4–6.9 | 5.1–8.1 | 492 |
