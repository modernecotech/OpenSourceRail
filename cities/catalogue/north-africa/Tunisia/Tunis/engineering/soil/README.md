# Tunis civil soil screening

410 route/station sample locations; 408 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 406 |
| granular-density-and-groundwater-tests | 141 |
| silt-moisture-frost-and-erosion-review | 56 |

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
| 0..30cm | clay | % | 19–38 | 3–46 | 408 |
| 0..30cm | sand | % | 26–58 | 5–90 | 408 |
| 0..30cm | silt | % | 22–37 | 5–52 | 408 |
| 0..30cm | bd.core | kg/m3 | 1290–1450 | 1050–1660 | 408 |
| 0..30cm | soc | g/kg | 4.1–11.1 | 1.9–22.3 | 408 |
| 0..30cm | ph.h2o | pH | 7.4–8 | 6.8–8.4 | 408 |
| 30..60cm | clay | % | 18–38 | 1–47 | 408 |
| 30..60cm | sand | % | 26–59 | 5–93 | 408 |
| 30..60cm | silt | % | 22–38 | 4–52 | 408 |
| 30..60cm | bd.core | kg/m3 | 1400–1590 | 1100–1810 | 408 |
| 30..60cm | soc | g/kg | 2.7–7.9 | 0.9–19.5 | 408 |
| 30..60cm | ph.h2o | pH | 7.6–8.2 | 6.6–8.7 | 408 |
| 60..100cm | clay | % | 18–38 | 1–47 | 408 |
| 60..100cm | sand | % | 27–59 | 5–93 | 408 |
| 60..100cm | silt | % | 22–38 | 1–53 | 408 |
| 60..100cm | bd.core | kg/m3 | 1370–1610 | 1050–1850 | 408 |
| 60..100cm | soc | g/kg | 1.9–6.2 | 0.6–25.1 | 408 |
| 60..100cm | ph.h2o | pH | 7.7–8.3 | 6.7–9 | 408 |
