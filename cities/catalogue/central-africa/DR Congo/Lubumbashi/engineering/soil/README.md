# Lubumbashi civil soil screening

238 route/station sample locations; 238 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 238 |
| fine-soil-plasticity-and-shrink-swell-tests | 238 |
| granular-density-and-groundwater-tests | 193 |

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
| 0..30cm | clay | % | 27–38 | 13–51 | 238 |
| 0..30cm | sand | % | 38–56 | 14–83 | 238 |
| 0..30cm | silt | % | 17–24 | 1–37 | 238 |
| 0..30cm | bd.core | kg/m3 | 1280–1440 | 1110–1620 | 238 |
| 0..30cm | soc | g/kg | 4.9–14.6 | 1.9–27.2 | 238 |
| 0..30cm | ph.h2o | pH | 5.4–6.5 | 4.9–7.3 | 238 |
| 30..60cm | clay | % | 31–43 | 12–55 | 238 |
| 30..60cm | sand | % | 33–52 | 10–85 | 238 |
| 30..60cm | silt | % | 16–26 | 0–42 | 238 |
| 30..60cm | bd.core | kg/m3 | 1300–1490 | 1080–1660 | 238 |
| 30..60cm | soc | g/kg | 3.5–7 | 1.4–14.6 | 238 |
| 30..60cm | ph.h2o | pH | 5.6–6.5 | 4.9–7.6 | 238 |
| 60..100cm | clay | % | 33–44 | 13–58 | 238 |
| 60..100cm | sand | % | 30–50 | 10–85 | 238 |
| 60..100cm | silt | % | 16–27 | 0–45 | 238 |
| 60..100cm | bd.core | kg/m3 | 1250–1520 | 840–1730 | 238 |
| 60..100cm | soc | g/kg | 3.3–5.7 | 1.1–10.3 | 238 |
| 60..100cm | ph.h2o | pH | 5.9–6.8 | 4.9–8.1 | 238 |
