# Buraidah civil soil screening

102 route/station sample locations; 83 complete profiles; 19 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 19 |
| fine-soil-plasticity-and-shrink-swell-tests | 64 |
| granular-density-and-groundwater-tests | 81 |
| silt-moisture-frost-and-erosion-review | 7 |

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
| 0..30cm | clay | % | 17–26 | 0–40 | 83 |
| 0..30cm | sand | % | 39–58 | 14–85 | 83 |
| 0..30cm | silt | % | 25–35 | 8–53 | 83 |
| 0..30cm | bd.core | kg/m3 | 1450–1500 | 1310–1690 | 83 |
| 0..30cm | soc | g/kg | 2.3–3.9 | 0.5–8.1 | 83 |
| 0..30cm | ph.h2o | pH | 8.2–8.4 | 7.5–9.3 | 83 |
| 30..60cm | clay | % | 18–27 | 1–43 | 83 |
| 30..60cm | sand | % | 39–58 | 14–92 | 83 |
| 30..60cm | silt | % | 23–33 | 3–50 | 83 |
| 30..60cm | bd.core | kg/m3 | 1420–1510 | 1210–1750 | 83 |
| 30..60cm | soc | g/kg | 1.7–2.7 | 0–11.8 | 83 |
| 30..60cm | ph.h2o | pH | 8.2–8.7 | 7.5–10 | 83 |
| 60..100cm | clay | % | 18–27 | 1–42 | 83 |
| 60..100cm | sand | % | 39–57 | 14–92 | 83 |
| 60..100cm | silt | % | 23–33 | 3–53 | 83 |
| 60..100cm | bd.core | kg/m3 | 1450–1550 | 1230–1820 | 83 |
| 60..100cm | soc | g/kg | 1.5–2.6 | 0–8.4 | 83 |
| 60..100cm | ph.h2o | pH | 8.2–8.8 | 7.5–10.1 | 83 |
