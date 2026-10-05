# Aleppo civil soil screening

621 route/station sample locations; 621 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 621 |
| granular-density-and-groundwater-tests | 217 |
| silt-moisture-frost-and-erosion-review | 48 |

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
| 0..30cm | clay | % | 22–30 | 8–43 | 621 |
| 0..30cm | sand | % | 35–48 | 12–75 | 621 |
| 0..30cm | silt | % | 29–36 | 11–53 | 621 |
| 0..30cm | bd.core | kg/m3 | 1350–1480 | 1180–1650 | 621 |
| 0..30cm | soc | g/kg | 2.9–9.4 | 1.2–17.5 | 621 |
| 0..30cm | ph.h2o | pH | 7.5–8 | 6.9–8.5 | 621 |
| 30..60cm | clay | % | 24–33 | 8–47 | 621 |
| 30..60cm | sand | % | 34–50 | 12–77 | 621 |
| 30..60cm | silt | % | 26–34 | 7–50 | 621 |
| 30..60cm | bd.core | kg/m3 | 1430–1610 | 1260–1750 | 621 |
| 30..60cm | soc | g/kg | 2.2–4.6 | 1–9.3 | 621 |
| 30..60cm | ph.h2o | pH | 7.4–8 | 6.7–8.7 | 621 |
| 60..100cm | clay | % | 25–35 | 9–52 | 621 |
| 60..100cm | sand | % | 35–52 | 11–80 | 621 |
| 60..100cm | silt | % | 23–32 | 2–53 | 621 |
| 60..100cm | bd.core | kg/m3 | 1430–1640 | 1210–1930 | 621 |
| 60..100cm | soc | g/kg | 1.9–3.7 | 0.4–7.9 | 621 |
| 60..100cm | ph.h2o | pH | 7.4–8 | 6.7–8.8 | 621 |
