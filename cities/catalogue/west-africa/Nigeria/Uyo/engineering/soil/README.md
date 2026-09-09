# Uyo civil soil screening

83 route/station sample locations; 83 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 83 |
| fine-soil-plasticity-and-shrink-swell-tests | 83 |
| granular-density-and-groundwater-tests | 82 |

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
| 0..30cm | clay | % | 24–33 | 8–46 | 83 |
| 0..30cm | sand | % | 44–63 | 18–89 | 83 |
| 0..30cm | silt | % | 13–23 | 0–43 | 83 |
| 0..30cm | bd.core | kg/m3 | 1230–1340 | 960–1550 | 83 |
| 0..30cm | soc | g/kg | 8.5–13.2 | 3.8–23.1 | 83 |
| 0..30cm | ph.h2o | pH | 5.2–5.4 | 4.5–6.3 | 83 |
| 30..60cm | clay | % | 24–35 | 8–49 | 83 |
| 30..60cm | sand | % | 41–64 | 13–88 | 83 |
| 30..60cm | silt | % | 12–25 | 0–46 | 83 |
| 30..60cm | bd.core | kg/m3 | 1210–1330 | 830–1600 | 83 |
| 30..60cm | soc | g/kg | 4.3–6.6 | 1.7–16 | 83 |
| 30..60cm | ph.h2o | pH | 5.1–5.3 | 4.5–6.2 | 83 |
| 60..100cm | clay | % | 25–35 | 8–49 | 83 |
| 60..100cm | sand | % | 41–64 | 14–88 | 83 |
| 60..100cm | silt | % | 11–24 | 0–47 | 83 |
| 60..100cm | bd.core | kg/m3 | 1260–1350 | 950–1630 | 83 |
| 60..100cm | soc | g/kg | 4.3–7.2 | 1.8–23.1 | 83 |
| 60..100cm | ph.h2o | pH | 5.2–5.4 | 4.6–6.3 | 83 |
