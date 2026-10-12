# Songea civil soil screening

76 route/station sample locations; 76 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 75 |
| fine-soil-plasticity-and-shrink-swell-tests | 76 |
| granular-density-and-groundwater-tests | 69 |

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
| 0..30cm | clay | % | 27–32 | 11–45 | 76 |
| 0..30cm | sand | % | 48–59 | 24–89 | 76 |
| 0..30cm | silt | % | 14–19 | 0–31 | 76 |
| 0..30cm | bd.core | kg/m3 | 1270–1380 | 1030–1520 | 76 |
| 0..30cm | soc | g/kg | 6.8–11.3 | 3.6–21.4 | 76 |
| 0..30cm | ph.h2o | pH | 5.5–6.1 | 5.1–6.8 | 76 |
| 30..60cm | clay | % | 35–39 | 19–53 | 76 |
| 30..60cm | sand | % | 39–50 | 14–76 | 76 |
| 30..60cm | silt | % | 16–22 | 1–39 | 76 |
| 30..60cm | bd.core | kg/m3 | 1260–1440 | 1060–1570 | 76 |
| 30..60cm | soc | g/kg | 4.3–5.7 | 2–10.3 | 76 |
| 30..60cm | ph.h2o | pH | 5.8–6.3 | 5.1–7 | 76 |
| 60..100cm | clay | % | 35–41 | 17–56 | 76 |
| 60..100cm | sand | % | 35–47 | 11–76 | 76 |
| 60..100cm | silt | % | 16–24 | 0–40 | 76 |
| 60..100cm | bd.core | kg/m3 | 1160–1450 | 830–1640 | 76 |
| 60..100cm | soc | g/kg | 3.2–4.5 | 1.4–8.2 | 76 |
| 60..100cm | ph.h2o | pH | 5.9–6.6 | 5.1–8 | 76 |
