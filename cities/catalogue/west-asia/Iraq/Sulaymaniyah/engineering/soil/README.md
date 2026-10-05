# Sulaymaniyah civil soil screening

230 route/station sample locations; 230 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 29 |
| fine-soil-plasticity-and-shrink-swell-tests | 230 |
| granular-density-and-groundwater-tests | 24 |
| silt-moisture-frost-and-erosion-review | 177 |

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
| 0..30cm | clay | % | 25–41 | 13–53 | 230 |
| 0..30cm | sand | % | 20–48 | 3–74 | 230 |
| 0..30cm | silt | % | 26–42 | 12–60 | 230 |
| 0..30cm | bd.core | kg/m3 | 1340–1430 | 1090–1640 | 230 |
| 0..30cm | soc | g/kg | 2.5–10.8 | 1–25.1 | 230 |
| 0..30cm | ph.h2o | pH | 6.6–7.5 | 5.4–8.1 | 230 |
| 30..60cm | clay | % | 26–41 | 4–55 | 230 |
| 30..60cm | sand | % | 22–53 | 4–86 | 230 |
| 30..60cm | silt | % | 22–40 | 6–53 | 230 |
| 30..60cm | bd.core | kg/m3 | 1380–1540 | 1090–1750 | 230 |
| 30..60cm | soc | g/kg | 2.5–6.8 | 0.9–15.3 | 230 |
| 30..60cm | ph.h2o | pH | 6.7–7.4 | 5.4–8.2 | 230 |
| 60..100cm | clay | % | 25–42 | 4–55 | 230 |
| 60..100cm | sand | % | 22–54 | 4–87 | 230 |
| 60..100cm | silt | % | 20–39 | 3–55 | 230 |
| 60..100cm | bd.core | kg/m3 | 1350–1610 | 980–1850 | 230 |
| 60..100cm | soc | g/kg | 2.1–5.4 | 0.5–9.7 | 230 |
| 60..100cm | ph.h2o | pH | 6.8–7.4 | 5.5–8.3 | 230 |
