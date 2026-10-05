# Mandalay civil soil screening

596 route/station sample locations; 531 complete profiles; 65 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 75 |
| coverage-gap | 65 |
| fine-soil-plasticity-and-shrink-swell-tests | 508 |
| granular-density-and-groundwater-tests | 531 |
| silt-moisture-frost-and-erosion-review | 7 |

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
| 0..30cm | clay | % | 20–28 | 4–43 | 531 |
| 0..30cm | sand | % | 44–61 | 14–90 | 531 |
| 0..30cm | silt | % | 19–30 | 0–49 | 531 |
| 0..30cm | bd.core | kg/m3 | 1300–1500 | 950–1680 | 531 |
| 0..30cm | soc | g/kg | 4.6–15.1 | 1.8–33.3 | 531 |
| 0..30cm | ph.h2o | pH | 6.1–7.3 | 5.2–8.3 | 531 |
| 30..60cm | clay | % | 20–29 | 5–46 | 531 |
| 30..60cm | sand | % | 43–62 | 10–90 | 531 |
| 30..60cm | silt | % | 18–29 | 0–51 | 531 |
| 30..60cm | bd.core | kg/m3 | 1330–1560 | 940–1800 | 531 |
| 30..60cm | soc | g/kg | 3.1–9.8 | 0.9–31.7 | 531 |
| 30..60cm | ph.h2o | pH | 6.3–7.4 | 5.4–8.3 | 531 |
| 60..100cm | clay | % | 21–29 | 5–46 | 531 |
| 60..100cm | sand | % | 44–61 | 7–91 | 531 |
| 60..100cm | silt | % | 18–28 | 0–53 | 531 |
| 60..100cm | bd.core | kg/m3 | 1360–1610 | 860–1860 | 531 |
| 60..100cm | soc | g/kg | 2.5–8.4 | 0.2–26.2 | 531 |
| 60..100cm | ph.h2o | pH | 6.6–7.4 | 5.1–8.4 | 531 |
