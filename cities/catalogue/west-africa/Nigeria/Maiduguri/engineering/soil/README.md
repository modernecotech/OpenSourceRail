# Maiduguri civil soil screening

5,058 route/station sample locations; 5,058 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 4702 |
| fine-soil-plasticity-and-shrink-swell-tests | 4878 |
| granular-density-and-groundwater-tests | 5058 |

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
| 0..30cm | clay | % | 19–27 | 6–42 | 5058 |
| 0..30cm | sand | % | 47–65 | 20–86 | 5058 |
| 0..30cm | silt | % | 16–26 | 3–40 | 5058 |
| 0..30cm | bd.core | kg/m3 | 1410–1560 | 1160–1720 | 5058 |
| 0..30cm | soc | g/kg | 2.6–6.2 | 1.2–12.5 | 5058 |
| 0..30cm | ph.h2o | pH | 5.8–7.4 | 4.8–8.3 | 5058 |
| 30..60cm | clay | % | 19–28 | 4–48 | 5058 |
| 30..60cm | sand | % | 48–66 | 12–90 | 5058 |
| 30..60cm | silt | % | 15–25 | 0–42 | 5058 |
| 30..60cm | bd.core | kg/m3 | 1360–1530 | 1100–1750 | 5058 |
| 30..60cm | soc | g/kg | 2–3.4 | 0.8–7.1 | 5058 |
| 30..60cm | ph.h2o | pH | 5.7–7.7 | 4.4–8.7 | 5058 |
| 60..100cm | clay | % | 19–28 | 4–48 | 5058 |
| 60..100cm | sand | % | 47–66 | 11–91 | 5058 |
| 60..100cm | silt | % | 15–25 | 0–43 | 5058 |
| 60..100cm | bd.core | kg/m3 | 1330–1520 | 770–1760 | 5058 |
| 60..100cm | soc | g/kg | 1.6–2.9 | 0.5–7.6 | 5058 |
| 60..100cm | ph.h2o | pH | 5.8–7.9 | 4.4–8.8 | 5058 |
