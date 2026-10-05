# Vijayawada civil soil screening

1,234 route/station sample locations; 1,222 complete profiles; 12 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 33 |
| coverage-gap | 12 |
| fine-soil-plasticity-and-shrink-swell-tests | 1222 |
| granular-density-and-groundwater-tests | 1204 |
| silt-moisture-frost-and-erosion-review | 52 |

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
| 0..30cm | clay | % | 20–33 | 4–50 | 1222 |
| 0..30cm | sand | % | 36–61 | 9–91 | 1222 |
| 0..30cm | silt | % | 20–31 | 3–48 | 1222 |
| 0..30cm | bd.core | kg/m3 | 1190–1540 | 820–1730 | 1222 |
| 0..30cm | soc | g/kg | 4.6–16.4 | 2–46.6 | 1222 |
| 0..30cm | ph.h2o | pH | 6.2–7.4 | 5.2–8.3 | 1222 |
| 30..60cm | clay | % | 22–35 | 4–52 | 1222 |
| 30..60cm | sand | % | 35–57 | 7–91 | 1222 |
| 30..60cm | silt | % | 21–32 | 0–51 | 1222 |
| 30..60cm | bd.core | kg/m3 | 1310–1570 | 900–1830 | 1222 |
| 30..60cm | soc | g/kg | 3.1–13.2 | 0.9–30.9 | 1222 |
| 30..60cm | ph.h2o | pH | 6.4–7.7 | 5.3–8.4 | 1222 |
| 60..100cm | clay | % | 22–34 | 3–52 | 1222 |
| 60..100cm | sand | % | 35–57 | 9–92 | 1222 |
| 60..100cm | silt | % | 20–31 | 0–51 | 1222 |
| 60..100cm | bd.core | kg/m3 | 1340–1610 | 840–1920 | 1222 |
| 60..100cm | soc | g/kg | 2.7–8.7 | 0.7–33 | 1222 |
| 60..100cm | ph.h2o | pH | 6.6–7.8 | 5.1–8.6 | 1222 |
