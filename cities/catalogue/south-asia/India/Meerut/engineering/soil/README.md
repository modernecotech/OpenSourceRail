# Meerut civil soil screening

210 route/station sample locations; 210 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 10 |
| fine-soil-plasticity-and-shrink-swell-tests | 210 |
| granular-density-and-groundwater-tests | 177 |
| silt-moisture-frost-and-erosion-review | 29 |

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
| 0..30cm | clay | % | 22–28 | 7–43 | 210 |
| 0..30cm | sand | % | 41–52 | 13–81 | 210 |
| 0..30cm | silt | % | 26–34 | 12–52 | 210 |
| 0..30cm | bd.core | kg/m3 | 1370–1560 | 1180–1720 | 210 |
| 0..30cm | soc | g/kg | 2.7–7.8 | 0.6–19.1 | 210 |
| 0..30cm | ph.h2o | pH | 6.5–7.4 | 5.3–8 | 210 |
| 30..60cm | clay | % | 23–30 | 7–44 | 210 |
| 30..60cm | sand | % | 38–49 | 10–81 | 210 |
| 30..60cm | silt | % | 28–34 | 9–53 | 210 |
| 30..60cm | bd.core | kg/m3 | 1410–1640 | 1090–1780 | 210 |
| 30..60cm | soc | g/kg | 1.4–3.9 | 0.3–7.6 | 210 |
| 30..60cm | ph.h2o | pH | 6.5–7.5 | 5.4–8 | 210 |
| 60..100cm | clay | % | 23–30 | 6–46 | 210 |
| 60..100cm | sand | % | 37–49 | 8–83 | 210 |
| 60..100cm | silt | % | 27–34 | 7–55 | 210 |
| 60..100cm | bd.core | kg/m3 | 1500–1690 | 1110–1840 | 210 |
| 60..100cm | soc | g/kg | 1.1–2.8 | 0.2–6.3 | 210 |
| 60..100cm | ph.h2o | pH | 6.5–7.8 | 5.3–8.3 | 210 |
