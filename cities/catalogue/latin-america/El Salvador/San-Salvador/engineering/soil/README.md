# San-Salvador civil soil screening

2,199 route/station sample locations; 2,199 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1901 |
| fine-soil-plasticity-and-shrink-swell-tests | 2084 |
| granular-density-and-groundwater-tests | 1439 |
| organic-content-and-compressibility-tests | 56 |
| silt-moisture-frost-and-erosion-review | 392 |

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
| 0..30cm | clay | % | 20–32 | 4–43 | 2199 |
| 0..30cm | sand | % | 37–54 | 12–88 | 2199 |
| 0..30cm | silt | % | 25–35 | 6–51 | 2199 |
| 0..30cm | bd.core | kg/m3 | 1010–1440 | 790–1640 | 2199 |
| 0..30cm | soc | g/kg | 5.8–32.8 | 2.4–85.2 | 2199 |
| 0..30cm | ph.h2o | pH | 5.5–6.9 | 4.8–8 | 2199 |
| 30..60cm | clay | % | 20–35 | 3–50 | 2199 |
| 30..60cm | sand | % | 36–54 | 8–88 | 2199 |
| 30..60cm | silt | % | 25–34 | 6–53 | 2199 |
| 30..60cm | bd.core | kg/m3 | 1050–1480 | 790–1650 | 2199 |
| 30..60cm | soc | g/kg | 3.6–9.7 | 1.1–22.5 | 2199 |
| 30..60cm | ph.h2o | pH | 5.6–7 | 4.9–8.1 | 2199 |
| 60..100cm | clay | % | 19–35 | 3–49 | 2199 |
| 60..100cm | sand | % | 33–54 | 7–87 | 2199 |
| 60..100cm | silt | % | 26–36 | 5–58 | 2199 |
| 60..100cm | bd.core | kg/m3 | 1070–1520 | 810–1730 | 2199 |
| 60..100cm | soc | g/kg | 2.6–7.5 | 0.7–26.5 | 2199 |
| 60..100cm | ph.h2o | pH | 5.7–7.2 | 4.8–8.4 | 2199 |
