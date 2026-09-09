# Kirkuk civil soil screening

270 route/station sample locations; 268 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 268 |
| granular-density-and-groundwater-tests | 82 |
| silt-moisture-frost-and-erosion-review | 236 |

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
| 0..30cm | clay | % | 20–33 | 9–43 | 268 |
| 0..30cm | sand | % | 21–46 | 3–69 | 268 |
| 0..30cm | silt | % | 34–46 | 17–60 | 268 |
| 0..30cm | bd.core | kg/m3 | 1360–1450 | 1120–1640 | 268 |
| 0..30cm | soc | g/kg | 2.6–7.2 | 0.9–11.9 | 268 |
| 0..30cm | ph.h2o | pH | 7.3–7.7 | 6.4–8.1 | 268 |
| 30..60cm | clay | % | 20–35 | 3–45 | 268 |
| 30..60cm | sand | % | 24–53 | 5–86 | 268 |
| 30..60cm | silt | % | 27–41 | 7–58 | 268 |
| 30..60cm | bd.core | kg/m3 | 1360–1550 | 1140–1740 | 268 |
| 30..60cm | soc | g/kg | 2.5–4.9 | 1.1–9 | 268 |
| 30..60cm | ph.h2o | pH | 7.2–7.7 | 6.4–8.6 | 268 |
| 60..100cm | clay | % | 22–37 | 3–48 | 268 |
| 60..100cm | sand | % | 25–54 | 6–86 | 268 |
| 60..100cm | silt | % | 23–37 | 3–58 | 268 |
| 60..100cm | bd.core | kg/m3 | 1340–1610 | 1090–1900 | 268 |
| 60..100cm | soc | g/kg | 2.3–3.1 | 0.5–6.8 | 268 |
| 60..100cm | ph.h2o | pH | 7.2–7.7 | 6.4–8.9 | 268 |
