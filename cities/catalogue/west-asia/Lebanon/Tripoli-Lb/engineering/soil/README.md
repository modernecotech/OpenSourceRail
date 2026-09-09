# Tripoli-Lb civil soil screening

92 route/station sample locations; 90 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 6 |
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 89 |
| granular-density-and-groundwater-tests | 64 |
| silt-moisture-frost-and-erosion-review | 6 |

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
| 0..30cm | clay | % | 22–30 | 5–46 | 90 |
| 0..30cm | sand | % | 35–54 | 9–85 | 90 |
| 0..30cm | silt | % | 22–35 | 1–50 | 90 |
| 0..30cm | bd.core | kg/m3 | 1260–1400 | 1020–1560 | 90 |
| 0..30cm | soc | g/kg | 5.7–16.6 | 2.1–32.6 | 90 |
| 0..30cm | ph.h2o | pH | 6.5–7.7 | 5.3–8.2 | 90 |
| 30..60cm | clay | % | 23–32 | 4–49 | 90 |
| 30..60cm | sand | % | 36–56 | 10–86 | 90 |
| 30..60cm | silt | % | 19–33 | 0–49 | 90 |
| 30..60cm | bd.core | kg/m3 | 1360–1540 | 1060–1720 | 90 |
| 30..60cm | soc | g/kg | 2.7–10.4 | 0.8–43.6 | 90 |
| 30..60cm | ph.h2o | pH | 6.6–7.6 | 5.4–8.4 | 90 |
| 60..100cm | clay | % | 24–33 | 4–50 | 90 |
| 60..100cm | sand | % | 35–56 | 11–85 | 90 |
| 60..100cm | silt | % | 19–33 | 0–53 | 90 |
| 60..100cm | bd.core | kg/m3 | 1360–1590 | 1020–1820 | 90 |
| 60..100cm | soc | g/kg | 1.8–9 | 0.4–47.8 | 90 |
| 60..100cm | ph.h2o | pH | 6.6–7.6 | 5.3–8.5 | 90 |
