# Waw civil soil screening

55 route/station sample locations; 55 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 51 |
| fine-soil-plasticity-and-shrink-swell-tests | 55 |
| granular-density-and-groundwater-tests | 55 |

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
| 0..30cm | clay | % | 21–26 | 8–40 | 55 |
| 0..30cm | sand | % | 50–59 | 23–83 | 55 |
| 0..30cm | silt | % | 19–25 | 4–40 | 55 |
| 0..30cm | bd.core | kg/m3 | 1410–1520 | 1200–1670 | 55 |
| 0..30cm | soc | g/kg | 4.4–7.2 | 1.6–13 | 55 |
| 0..30cm | ph.h2o | pH | 5.9–6.3 | 5.3–6.9 | 55 |
| 30..60cm | clay | % | 24–29 | 8–43 | 55 |
| 30..60cm | sand | % | 45–56 | 19–85 | 55 |
| 30..60cm | silt | % | 19–26 | 4–45 | 55 |
| 30..60cm | bd.core | kg/m3 | 1390–1510 | 1100–1670 | 55 |
| 30..60cm | soc | g/kg | 3.2–4.5 | 1–10.3 | 55 |
| 30..60cm | ph.h2o | pH | 6.1–6.4 | 5.4–7.3 | 55 |
| 60..100cm | clay | % | 24–30 | 6–46 | 55 |
| 60..100cm | sand | % | 44–56 | 15–87 | 55 |
| 60..100cm | silt | % | 19–26 | 0–49 | 55 |
| 60..100cm | bd.core | kg/m3 | 1430–1520 | 1150–1810 | 55 |
| 60..100cm | soc | g/kg | 2.6–3.7 | 0.8–7.6 | 55 |
| 60..100cm | ph.h2o | pH | 6.3–6.5 | 5–8.2 | 55 |
