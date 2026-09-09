# Vijayawada civil soil screening

572 route/station sample locations; 566 complete profiles; 6 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 39 |
| coverage-gap | 6 |
| fine-soil-plasticity-and-shrink-swell-tests | 566 |
| granular-density-and-groundwater-tests | 562 |
| silt-moisture-frost-and-erosion-review | 14 |

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
| 0..30cm | clay | % | 22–33 | 5–50 | 566 |
| 0..30cm | sand | % | 37–56 | 11–91 | 566 |
| 0..30cm | silt | % | 21–31 | 0–49 | 566 |
| 0..30cm | bd.core | kg/m3 | 1320–1530 | 940–1700 | 566 |
| 0..30cm | soc | g/kg | 5–12.6 | 2–30.3 | 566 |
| 0..30cm | ph.h2o | pH | 6.3–7.3 | 5.2–8.3 | 566 |
| 30..60cm | clay | % | 23–34 | 4–51 | 566 |
| 30..60cm | sand | % | 36–54 | 7–91 | 566 |
| 30..60cm | silt | % | 21–31 | 0–51 | 566 |
| 30..60cm | bd.core | kg/m3 | 1380–1570 | 1040–1810 | 566 |
| 30..60cm | soc | g/kg | 3.3–9.8 | 0.9–27 | 566 |
| 30..60cm | ph.h2o | pH | 6.4–7.5 | 5.4–8.4 | 566 |
| 60..100cm | clay | % | 23–34 | 4–52 | 566 |
| 60..100cm | sand | % | 37–54 | 10–91 | 566 |
| 60..100cm | silt | % | 21–31 | 0–53 | 566 |
| 60..100cm | bd.core | kg/m3 | 1380–1600 | 740–1910 | 566 |
| 60..100cm | soc | g/kg | 2.7–8.4 | 0.6–26.8 | 566 |
| 60..100cm | ph.h2o | pH | 6.6–7.7 | 5.4–8.6 | 566 |
