# Uige civil soil screening

20 route/station sample locations; 20 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 20 |
| fine-soil-plasticity-and-shrink-swell-tests | 20 |
| granular-density-and-groundwater-tests | 1 |

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
| 0..30cm | clay | % | 33–37 | 20–50 | 20 |
| 0..30cm | sand | % | 37–46 | 18–70 | 20 |
| 0..30cm | silt | % | 20–26 | 3–42 | 20 |
| 0..30cm | bd.core | kg/m3 | 1140–1270 | 930–1480 | 20 |
| 0..30cm | soc | g/kg | 9.9–18.8 | 4.8–31.2 | 20 |
| 0..30cm | ph.h2o | pH | 5.5–5.7 | 4.8–6.3 | 20 |
| 30..60cm | clay | % | 38–41 | 23–54 | 20 |
| 30..60cm | sand | % | 35–42 | 11–65 | 20 |
| 30..60cm | silt | % | 20–25 | 3–43 | 20 |
| 30..60cm | bd.core | kg/m3 | 1130–1340 | 800–1590 | 20 |
| 30..60cm | soc | g/kg | 6.9–11.1 | 2.9–29.2 | 20 |
| 30..60cm | ph.h2o | pH | 5.4–5.8 | 4.9–6.4 | 20 |
| 60..100cm | clay | % | 39–43 | 22–58 | 20 |
| 60..100cm | sand | % | 32–41 | 9–65 | 20 |
| 60..100cm | silt | % | 20–25 | 3–46 | 20 |
| 60..100cm | bd.core | kg/m3 | 1030–1320 | 420–1600 | 20 |
| 60..100cm | soc | g/kg | 6.4–11.7 | 2–27.9 | 20 |
| 60..100cm | ph.h2o | pH | 5.5–5.8 | 4.9–6.5 | 20 |
