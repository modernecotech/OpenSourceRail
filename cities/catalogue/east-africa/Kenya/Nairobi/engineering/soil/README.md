# Nairobi civil soil screening

21,011 route/station sample locations; 21,011 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1319 |
| fine-soil-plasticity-and-shrink-swell-tests | 19604 |
| granular-density-and-groundwater-tests | 11025 |
| silt-moisture-frost-and-erosion-review | 548 |

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
| 0..30cm | clay | % | 21–45 | 8–57 | 21011 |
| 0..30cm | sand | % | 17–59 | 3–82 | 21011 |
| 0..30cm | silt | % | 19–40 | 4–51 | 21011 |
| 0..30cm | bd.core | kg/m3 | 1080–1430 | 920–1610 | 21011 |
| 0..30cm | soc | g/kg | 4.2–25.8 | 1.9–47.4 | 21011 |
| 0..30cm | ph.h2o | pH | 5.6–7.7 | 4.9–8.5 | 21011 |
| 30..60cm | clay | % | 19–46 | 7–62 | 21011 |
| 30..60cm | sand | % | 17–63 | 2–86 | 21011 |
| 30..60cm | silt | % | 17–42 | 0–53 | 21011 |
| 30..60cm | bd.core | kg/m3 | 1150–1460 | 980–1660 | 21011 |
| 30..60cm | soc | g/kg | 2.7–13.3 | 1–22 | 21011 |
| 30..60cm | ph.h2o | pH | 5.7–7.8 | 4.8–8.5 | 21011 |
| 60..100cm | clay | % | 19–45 | 6–60 | 21011 |
| 60..100cm | sand | % | 17–62 | 2–87 | 21011 |
| 60..100cm | silt | % | 16–41 | 0–54 | 21011 |
| 60..100cm | bd.core | kg/m3 | 1190–1490 | 920–1710 | 21011 |
| 60..100cm | soc | g/kg | 1.6–8.4 | 0.3–16.2 | 21011 |
| 60..100cm | ph.h2o | pH | 5.7–7.8 | 4.6–8.6 | 21011 |
