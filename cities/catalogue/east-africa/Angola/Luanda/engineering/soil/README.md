# Luanda civil soil screening

654 route/station sample locations; 648 complete profiles; 6 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 150 |
| coverage-gap | 6 |
| fine-soil-plasticity-and-shrink-swell-tests | 530 |
| granular-density-and-groundwater-tests | 643 |
| silt-moisture-frost-and-erosion-review | 1 |

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
| 0..30cm | clay | % | 18–34 | 2–46 | 648 |
| 0..30cm | sand | % | 38–67 | 16–94 | 648 |
| 0..30cm | silt | % | 12–28 | 0–41 | 648 |
| 0..30cm | bd.core | kg/m3 | 1240–1490 | 1020–1710 | 648 |
| 0..30cm | soc | g/kg | 3.7–12.9 | 1.5–39.1 | 648 |
| 0..30cm | ph.h2o | pH | 6.4–8 | 5.3–8.9 | 648 |
| 30..60cm | clay | % | 18–35 | 2–51 | 648 |
| 30..60cm | sand | % | 38–68 | 11–92 | 648 |
| 30..60cm | silt | % | 11–27 | 0–50 | 648 |
| 30..60cm | bd.core | kg/m3 | 1240–1510 | 950–1750 | 648 |
| 30..60cm | soc | g/kg | 2.5–8.5 | 0.7–26 | 648 |
| 30..60cm | ph.h2o | pH | 6.5–8.1 | 5.2–9.1 | 648 |
| 60..100cm | clay | % | 19–35 | 2–53 | 648 |
| 60..100cm | sand | % | 39–67 | 10–93 | 648 |
| 60..100cm | silt | % | 11–26 | 0–52 | 648 |
| 60..100cm | bd.core | kg/m3 | 1170–1520 | 790–1790 | 648 |
| 60..100cm | soc | g/kg | 1.9–6.7 | 0.2–26.6 | 648 |
| 60..100cm | ph.h2o | pH | 6.5–8 | 4.9–9.3 | 648 |
