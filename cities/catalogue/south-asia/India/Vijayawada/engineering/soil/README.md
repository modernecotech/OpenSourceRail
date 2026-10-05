# Vijayawada civil soil screening

751 route/station sample locations; 742 complete profiles; 9 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 31 |
| coverage-gap | 9 |
| fine-soil-plasticity-and-shrink-swell-tests | 742 |
| granular-density-and-groundwater-tests | 731 |
| silt-moisture-frost-and-erosion-review | 18 |

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
| 0..30cm | clay | % | 20–33 | 4–50 | 742 |
| 0..30cm | sand | % | 36–61 | 8–91 | 742 |
| 0..30cm | silt | % | 20–31 | 3–49 | 742 |
| 0..30cm | bd.core | kg/m3 | 1190–1540 | 820–1720 | 742 |
| 0..30cm | soc | g/kg | 4.6–15.9 | 2–33.9 | 742 |
| 0..30cm | ph.h2o | pH | 6.2–7.4 | 5.2–8.3 | 742 |
| 30..60cm | clay | % | 22–35 | 4–52 | 742 |
| 30..60cm | sand | % | 35–57 | 7–89 | 742 |
| 30..60cm | silt | % | 21–32 | 0–51 | 742 |
| 30..60cm | bd.core | kg/m3 | 1310–1570 | 900–1830 | 742 |
| 30..60cm | soc | g/kg | 3.1–12.2 | 0.9–30.9 | 742 |
| 30..60cm | ph.h2o | pH | 6.4–7.6 | 5.3–8.4 | 742 |
| 60..100cm | clay | % | 22–34 | 3–52 | 742 |
| 60..100cm | sand | % | 35–57 | 7–92 | 742 |
| 60..100cm | silt | % | 21–31 | 0–51 | 742 |
| 60..100cm | bd.core | kg/m3 | 1340–1610 | 840–1920 | 742 |
| 60..100cm | soc | g/kg | 2.7–8.6 | 0.7–28.3 | 742 |
| 60..100cm | ph.h2o | pH | 6.6–7.8 | 5.1–8.6 | 742 |
