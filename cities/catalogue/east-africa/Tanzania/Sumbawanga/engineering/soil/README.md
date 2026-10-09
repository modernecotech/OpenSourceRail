# Sumbawanga civil soil screening

139 route/station sample locations; 139 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 119 |
| fine-soil-plasticity-and-shrink-swell-tests | 139 |
| granular-density-and-groundwater-tests | 95 |
| silt-moisture-frost-and-erosion-review | 44 |

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
| 0..30cm | clay | % | 25–34 | 12–44 | 139 |
| 0..30cm | sand | % | 37–54 | 16–81 | 139 |
| 0..30cm | silt | % | 19–29 | 7–42 | 139 |
| 0..30cm | bd.core | kg/m3 | 1160–1380 | 960–1580 | 139 |
| 0..30cm | soc | g/kg | 6.5–17.3 | 2.6–35.5 | 139 |
| 0..30cm | ph.h2o | pH | 5.6–6.3 | 5.1–7.2 | 139 |
| 30..60cm | clay | % | 27–37 | 11–49 | 139 |
| 30..60cm | sand | % | 28–47 | 8–82 | 139 |
| 30..60cm | silt | % | 23–35 | 2–49 | 139 |
| 30..60cm | bd.core | kg/m3 | 1160–1400 | 800–1590 | 139 |
| 30..60cm | soc | g/kg | 5.1–9.2 | 2–17.8 | 139 |
| 30..60cm | ph.h2o | pH | 5.8–6.5 | 5.1–7.5 | 139 |
| 60..100cm | clay | % | 28–38 | 10–50 | 139 |
| 60..100cm | sand | % | 25–45 | 5–82 | 139 |
| 60..100cm | silt | % | 25–38 | 1–52 | 139 |
| 60..100cm | bd.core | kg/m3 | 1050–1440 | 580–1640 | 139 |
| 60..100cm | soc | g/kg | 4.2–7.6 | 1.7–16.9 | 139 |
| 60..100cm | ph.h2o | pH | 6.1–6.8 | 5–7.9 | 139 |
