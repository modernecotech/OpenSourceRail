# Mukalla civil soil screening

2,035 route/station sample locations; 1,272 complete profiles; 763 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 763 |
| fine-soil-plasticity-and-shrink-swell-tests | 11 |
| granular-density-and-groundwater-tests | 1272 |

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
| 0..30cm | clay | % | 10–18 | 0–30 | 1272 |
| 0..30cm | sand | % | 62–78 | 40–97 | 1272 |
| 0..30cm | silt | % | 12–21 | 1–33 | 1272 |
| 0..30cm | bd.core | kg/m3 | 1400–1520 | 1180–1710 | 1272 |
| 0..30cm | soc | g/kg | 1.9–7.1 | 0.5–24 | 1272 |
| 0..30cm | ph.h2o | pH | 8.2–8.7 | 7.7–9.5 | 1272 |
| 30..60cm | clay | % | 10–21 | 0–36 | 1272 |
| 30..60cm | sand | % | 56–78 | 28–98 | 1272 |
| 30..60cm | silt | % | 12–23 | 0–37 | 1272 |
| 30..60cm | bd.core | kg/m3 | 1460–1540 | 1270–1750 | 1272 |
| 30..60cm | soc | g/kg | 1–6.3 | 0–42 | 1272 |
| 30..60cm | ph.h2o | pH | 8.4–8.8 | 7.5–9.4 | 1272 |
| 60..100cm | clay | % | 10–21 | 0–35 | 1272 |
| 60..100cm | sand | % | 55–77 | 28–96 | 1272 |
| 60..100cm | silt | % | 12–24 | 0–40 | 1272 |
| 60..100cm | bd.core | kg/m3 | 1510–1590 | 1250–1790 | 1272 |
| 60..100cm | soc | g/kg | 0.8–4.5 | 0–31.2 | 1272 |
| 60..100cm | ph.h2o | pH | 8.3–8.8 | 7.6–9.5 | 1272 |
