# Ibb civil soil screening

446 route/station sample locations; 446 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 446 |
| granular-density-and-groundwater-tests | 269 |
| organic-content-and-compressibility-tests | 1 |
| silt-moisture-frost-and-erosion-review | 59 |

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
| 0..30cm | clay | % | 25–34 | 10–48 | 446 |
| 0..30cm | sand | % | 33–52 | 6–81 | 446 |
| 0..30cm | silt | % | 21–35 | 5–51 | 446 |
| 0..30cm | bd.core | kg/m3 | 1140–1420 | 940–1610 | 446 |
| 0..30cm | soc | g/kg | 4.8–24.6 | 2.8–51.5 | 446 |
| 0..30cm | ph.h2o | pH | 6.8–8 | 5.4–8.8 | 446 |
| 30..60cm | clay | % | 25–35 | 7–48 | 446 |
| 30..60cm | sand | % | 34–52 | 6–81 | 446 |
| 30..60cm | silt | % | 19–34 | 1–53 | 446 |
| 30..60cm | bd.core | kg/m3 | 1170–1450 | 900–1660 | 446 |
| 30..60cm | soc | g/kg | 3.6–9.7 | 1.3–22.7 | 446 |
| 30..60cm | ph.h2o | pH | 6.9–8.1 | 5.8–8.9 | 446 |
| 60..100cm | clay | % | 25–35 | 7–49 | 446 |
| 60..100cm | sand | % | 34–54 | 4–85 | 446 |
| 60..100cm | silt | % | 19–33 | 0–51 | 446 |
| 60..100cm | bd.core | kg/m3 | 1180–1470 | 880–1720 | 446 |
| 60..100cm | soc | g/kg | 2.5–8.5 | 1.1–30.5 | 446 |
| 60..100cm | ph.h2o | pH | 7–8.1 | 5.7–8.9 | 446 |
