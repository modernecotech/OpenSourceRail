# Aleppo civil soil screening

466 route/station sample locations; 465 complete profiles; 1 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 465 |
| granular-density-and-groundwater-tests | 145 |
| silt-moisture-frost-and-erosion-review | 54 |

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
| 0..30cm | clay | % | 23–30 | 9–42 | 465 |
| 0..30cm | sand | % | 34–47 | 12–76 | 465 |
| 0..30cm | silt | % | 30–37 | 13–53 | 465 |
| 0..30cm | bd.core | kg/m3 | 1350–1460 | 1170–1630 | 465 |
| 0..30cm | soc | g/kg | 2.9–9.4 | 1.2–17.5 | 465 |
| 0..30cm | ph.h2o | pH | 7.5–8 | 6.9–8.5 | 465 |
| 30..60cm | clay | % | 24–33 | 10–49 | 465 |
| 30..60cm | sand | % | 35–48 | 11–79 | 465 |
| 30..60cm | silt | % | 26–34 | 7–50 | 465 |
| 30..60cm | bd.core | kg/m3 | 1430–1580 | 1240–1750 | 465 |
| 30..60cm | soc | g/kg | 2.2–4.6 | 1–8.8 | 465 |
| 30..60cm | ph.h2o | pH | 7.4–8 | 6.7–8.7 | 465 |
| 60..100cm | clay | % | 25–34 | 9–53 | 465 |
| 60..100cm | sand | % | 35–51 | 11–79 | 465 |
| 60..100cm | silt | % | 23–32 | 2–52 | 465 |
| 60..100cm | bd.core | kg/m3 | 1430–1630 | 1220–1930 | 465 |
| 60..100cm | soc | g/kg | 2–3.5 | 0.5–7.8 | 465 |
| 60..100cm | ph.h2o | pH | 7.4–8 | 6.7–8.8 | 465 |
