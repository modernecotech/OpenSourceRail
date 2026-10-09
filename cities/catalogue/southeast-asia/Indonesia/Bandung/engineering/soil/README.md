# Bandung civil soil screening

2,645 route/station sample locations; 2,645 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 2645 |
| fine-soil-plasticity-and-shrink-swell-tests | 2645 |
| granular-density-and-groundwater-tests | 322 |
| organic-content-and-compressibility-tests | 262 |
| silt-moisture-frost-and-erosion-review | 711 |

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
| 0..30cm | clay | % | 26–37 | 10–48 | 2645 |
| 0..30cm | sand | % | 28–51 | 2–85 | 2645 |
| 0..30cm | silt | % | 22–38 | 1–57 | 2645 |
| 0..30cm | bd.core | kg/m3 | 740–1320 | 310–1560 | 2645 |
| 0..30cm | soc | g/kg | 7.9–44.1 | 2.1–94.5 | 2645 |
| 0..30cm | ph.h2o | pH | 5.1–5.9 | 3.9–6.8 | 2645 |
| 30..60cm | clay | % | 28–43 | 7–57 | 2645 |
| 30..60cm | sand | % | 26–53 | 0–88 | 2645 |
| 30..60cm | silt | % | 19–34 | 0–55 | 2645 |
| 30..60cm | bd.core | kg/m3 | 810–1360 | 470–1680 | 2645 |
| 30..60cm | soc | g/kg | 4.6–25.6 | 1–75.8 | 2645 |
| 30..60cm | ph.h2o | pH | 5.2–5.9 | 4.2–6.9 | 2645 |
| 60..100cm | clay | % | 27–44 | 7–61 | 2645 |
| 60..100cm | sand | % | 23–53 | 1–87 | 2645 |
| 60..100cm | silt | % | 20–35 | 0–55 | 2645 |
| 60..100cm | bd.core | kg/m3 | 870–1420 | 330–1700 | 2645 |
| 60..100cm | soc | g/kg | 4.6–28.5 | 0.4–135.1 | 2645 |
| 60..100cm | ph.h2o | pH | 5.3–5.9 | 4.2–7.3 | 2645 |
