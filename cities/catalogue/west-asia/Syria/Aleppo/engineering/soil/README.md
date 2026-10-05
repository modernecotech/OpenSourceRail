# Aleppo civil soil screening

1,059 route/station sample locations; 1,059 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 1059 |
| granular-density-and-groundwater-tests | 423 |
| silt-moisture-frost-and-erosion-review | 78 |

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
| 0..30cm | clay | % | 22–30 | 8–42 | 1059 |
| 0..30cm | sand | % | 35–48 | 12–75 | 1059 |
| 0..30cm | silt | % | 29–36 | 11–53 | 1059 |
| 0..30cm | bd.core | kg/m3 | 1350–1480 | 1170–1650 | 1059 |
| 0..30cm | soc | g/kg | 2.9–9.4 | 1.2–17.5 | 1059 |
| 0..30cm | ph.h2o | pH | 7.5–8 | 6.9–8.5 | 1059 |
| 30..60cm | clay | % | 24–33 | 7–47 | 1059 |
| 30..60cm | sand | % | 34–50 | 10–81 | 1059 |
| 30..60cm | silt | % | 26–34 | 3–50 | 1059 |
| 30..60cm | bd.core | kg/m3 | 1420–1610 | 1250–1750 | 1059 |
| 30..60cm | soc | g/kg | 2.2–4.5 | 0.9–9.6 | 1059 |
| 30..60cm | ph.h2o | pH | 7.4–8 | 6.7–8.7 | 1059 |
| 60..100cm | clay | % | 25–35 | 9–53 | 1059 |
| 60..100cm | sand | % | 35–52 | 6–81 | 1059 |
| 60..100cm | silt | % | 23–32 | 2–53 | 1059 |
| 60..100cm | bd.core | kg/m3 | 1430–1640 | 1210–1930 | 1059 |
| 60..100cm | soc | g/kg | 1.9–3.5 | 0.5–7 | 1059 |
| 60..100cm | ph.h2o | pH | 7.4–8 | 6.7–8.8 | 1059 |
