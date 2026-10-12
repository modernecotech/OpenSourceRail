# Meru-Ke civil soil screening

663 route/station sample locations; 663 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 311 |
| fine-soil-plasticity-and-shrink-swell-tests | 663 |
| granular-density-and-groundwater-tests | 125 |
| organic-content-and-compressibility-tests | 43 |
| silt-moisture-frost-and-erosion-review | 37 |

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
| 0..30cm | clay | % | 23–40 | 11–53 | 663 |
| 0..30cm | sand | % | 27–56 | 6–78 | 663 |
| 0..30cm | silt | % | 20–33 | 8–48 | 663 |
| 0..30cm | bd.core | kg/m3 | 1040–1310 | 740–1490 | 663 |
| 0..30cm | soc | g/kg | 9.1–30 | 3.8–67 | 663 |
| 0..30cm | ph.h2o | pH | 5.5–6.9 | 4.6–8 | 663 |
| 30..60cm | clay | % | 25–41 | 10–54 | 663 |
| 30..60cm | sand | % | 25–52 | 6–77 | 663 |
| 30..60cm | silt | % | 23–35 | 7–50 | 663 |
| 30..60cm | bd.core | kg/m3 | 1090–1290 | 780–1470 | 663 |
| 30..60cm | soc | g/kg | 6.7–14.6 | 2.6–27.7 | 663 |
| 30..60cm | ph.h2o | pH | 5.5–6.9 | 4.7–8 | 663 |
| 60..100cm | clay | % | 26–41 | 11–54 | 663 |
| 60..100cm | sand | % | 25–49 | 4–73 | 663 |
| 60..100cm | silt | % | 25–35 | 7–51 | 663 |
| 60..100cm | bd.core | kg/m3 | 1100–1260 | 800–1530 | 663 |
| 60..100cm | soc | g/kg | 5.7–8.9 | 1.9–21.3 | 663 |
| 60..100cm | ph.h2o | pH | 5.6–6.9 | 4.5–8.1 | 663 |
