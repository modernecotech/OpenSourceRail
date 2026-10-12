# Bloemfontein civil soil screening

2,330 route/station sample locations; 2,330 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 2151 |
| fine-soil-plasticity-and-shrink-swell-tests | 2330 |
| granular-density-and-groundwater-tests | 2297 |

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
| 0..30cm | clay | % | 25–40 | 12–51 | 2330 |
| 0..30cm | sand | % | 31–60 | 9–84 | 2330 |
| 0..30cm | silt | % | 15–30 | 0–45 | 2330 |
| 0..30cm | bd.core | kg/m3 | 1220–1430 | 960–1620 | 2330 |
| 0..30cm | soc | g/kg | 5.3–14.9 | 2.8–33.7 | 2330 |
| 0..30cm | ph.h2o | pH | 6.5–8.1 | 5.3–8.7 | 2330 |
| 30..60cm | clay | % | 27–42 | 8–57 | 2330 |
| 30..60cm | sand | % | 30–59 | 9–87 | 2330 |
| 30..60cm | silt | % | 14–29 | 0–44 | 2330 |
| 30..60cm | bd.core | kg/m3 | 1290–1510 | 940–1730 | 2330 |
| 30..60cm | soc | g/kg | 3–8.3 | 1.3–18.4 | 2330 |
| 30..60cm | ph.h2o | pH | 6.4–8.1 | 5.2–8.9 | 2330 |
| 60..100cm | clay | % | 27–41 | 9–56 | 2330 |
| 60..100cm | sand | % | 31–59 | 7–88 | 2330 |
| 60..100cm | silt | % | 14–28 | 0–43 | 2330 |
| 60..100cm | bd.core | kg/m3 | 1200–1570 | 370–1790 | 2330 |
| 60..100cm | soc | g/kg | 2–4.8 | 0.7–10.6 | 2330 |
| 60..100cm | ph.h2o | pH | 6.2–8.2 | 5–8.9 | 2330 |
