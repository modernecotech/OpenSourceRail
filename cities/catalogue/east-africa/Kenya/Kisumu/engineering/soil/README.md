# Kisumu civil soil screening

83 route/station sample locations; 81 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 81 |
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 81 |
| silt-moisture-frost-and-erosion-review | 25 |

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
| 0..30cm | clay | % | 31–43 | 18–52 | 81 |
| 0..30cm | sand | % | 23–45 | 10–65 | 81 |
| 0..30cm | silt | % | 24–35 | 12–48 | 81 |
| 0..30cm | bd.core | kg/m3 | 1060–1290 | 850–1490 | 81 |
| 0..30cm | soc | g/kg | 8.5–19.8 | 3.9–34.9 | 81 |
| 0..30cm | ph.h2o | pH | 5.5–6.1 | 5.1–7.2 | 81 |
| 30..60cm | clay | % | 32–44 | 17–55 | 81 |
| 30..60cm | sand | % | 22–43 | 8–65 | 81 |
| 30..60cm | silt | % | 25–35 | 9–54 | 81 |
| 30..60cm | bd.core | kg/m3 | 1110–1340 | 840–1620 | 81 |
| 30..60cm | soc | g/kg | 5.3–10.4 | 1.9–20 | 81 |
| 30..60cm | ph.h2o | pH | 5.5–6.2 | 5–7.3 | 81 |
| 60..100cm | clay | % | 31–44 | 18–55 | 81 |
| 60..100cm | sand | % | 22–43 | 6–68 | 81 |
| 60..100cm | silt | % | 25–35 | 4–55 | 81 |
| 60..100cm | bd.core | kg/m3 | 1150–1350 | 880–1660 | 81 |
| 60..100cm | soc | g/kg | 4.5–8.4 | 1.4–15.5 | 81 |
| 60..100cm | ph.h2o | pH | 5.5–6.3 | 5–7.7 | 81 |
