# Gulu civil soil screening

86 route/station sample locations; 86 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 59 |
| fine-soil-plasticity-and-shrink-swell-tests | 86 |
| granular-density-and-groundwater-tests | 86 |

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
| 0..30cm | clay | % | 25–33 | 12–47 | 86 |
| 0..30cm | sand | % | 41–55 | 12–83 | 86 |
| 0..30cm | silt | % | 20–27 | 5–44 | 86 |
| 0..30cm | bd.core | kg/m3 | 1180–1360 | 920–1590 | 86 |
| 0..30cm | soc | g/kg | 9.6–20 | 4.2–42.4 | 86 |
| 0..30cm | ph.h2o | pH | 6–6.3 | 5.2–7.1 | 86 |
| 30..60cm | clay | % | 26–35 | 8–50 | 86 |
| 30..60cm | sand | % | 40–54 | 10–87 | 86 |
| 30..60cm | silt | % | 19–26 | 1–45 | 86 |
| 30..60cm | bd.core | kg/m3 | 1330–1460 | 1100–1680 | 86 |
| 30..60cm | soc | g/kg | 4.9–9.1 | 2.3–15.2 | 86 |
| 30..60cm | ph.h2o | pH | 6–6.4 | 5.1–7.1 | 86 |
| 60..100cm | clay | % | 27–37 | 8–52 | 86 |
| 60..100cm | sand | % | 38–53 | 7–89 | 86 |
| 60..100cm | silt | % | 19–26 | 0–47 | 86 |
| 60..100cm | bd.core | kg/m3 | 1360–1490 | 1060–1780 | 86 |
| 60..100cm | soc | g/kg | 4.6–6.2 | 1.7–12.4 | 86 |
| 60..100cm | ph.h2o | pH | 6.1–6.6 | 5–7.6 | 86 |
