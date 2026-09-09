# Ibb civil soil screening

203 route/station sample locations; 203 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 203 |
| granular-density-and-groundwater-tests | 166 |
| organic-content-and-compressibility-tests | 1 |
| silt-moisture-frost-and-erosion-review | 33 |

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
| 0..30cm | clay | % | 24–34 | 8–46 | 203 |
| 0..30cm | sand | % | 34–52 | 7–75 | 203 |
| 0..30cm | silt | % | 20–34 | 5–50 | 203 |
| 0..30cm | bd.core | kg/m3 | 1060–1430 | 780–1610 | 203 |
| 0..30cm | soc | g/kg | 5.2–22.9 | 2.7–51.5 | 203 |
| 0..30cm | ph.h2o | pH | 6.9–8 | 5.5–8.8 | 203 |
| 30..60cm | clay | % | 25–34 | 8–47 | 203 |
| 30..60cm | sand | % | 35–53 | 7–78 | 203 |
| 30..60cm | silt | % | 19–34 | 1–52 | 203 |
| 30..60cm | bd.core | kg/m3 | 1090–1450 | 730–1660 | 203 |
| 30..60cm | soc | g/kg | 4.1–9 | 1.6–19.7 | 203 |
| 30..60cm | ph.h2o | pH | 7–8.2 | 5.9–8.9 | 203 |
| 60..100cm | clay | % | 25–34 | 7–47 | 203 |
| 60..100cm | sand | % | 35–53 | 5–81 | 203 |
| 60..100cm | silt | % | 18–33 | 0–52 | 203 |
| 60..100cm | bd.core | kg/m3 | 1060–1460 | 690–1660 | 203 |
| 60..100cm | soc | g/kg | 2.7–7.9 | 1.1–18.8 | 203 |
| 60..100cm | ph.h2o | pH | 7–8.1 | 5.5–8.9 | 203 |
