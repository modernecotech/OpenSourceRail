# Morogoro civil soil screening

1,140 route/station sample locations; 1,140 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 813 |
| fine-soil-plasticity-and-shrink-swell-tests | 1120 |
| granular-density-and-groundwater-tests | 918 |
| organic-content-and-compressibility-tests | 8 |

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
| 0..30cm | clay | % | 21–43 | 10–56 | 1140 |
| 0..30cm | sand | % | 32–68 | 9–89 | 1140 |
| 0..30cm | silt | % | 7–28 | 0–41 | 1140 |
| 0..30cm | bd.core | kg/m3 | 1120–1420 | 920–1580 | 1140 |
| 0..30cm | soc | g/kg | 5.8–26.9 | 2.6–61.2 | 1140 |
| 0..30cm | ph.h2o | pH | 5.6–7.3 | 4.6–8.3 | 1140 |
| 30..60cm | clay | % | 21–44 | 10–56 | 1140 |
| 30..60cm | sand | % | 30–69 | 8–89 | 1140 |
| 30..60cm | silt | % | 7–27 | 0–42 | 1140 |
| 30..60cm | bd.core | kg/m3 | 1160–1450 | 960–1630 | 1140 |
| 30..60cm | soc | g/kg | 3.8–10.6 | 1.7–17.7 | 1140 |
| 30..60cm | ph.h2o | pH | 5.3–7.4 | 4.8–8.3 | 1140 |
| 60..100cm | clay | % | 21–44 | 10–55 | 1140 |
| 60..100cm | sand | % | 30–69 | 8–89 | 1140 |
| 60..100cm | silt | % | 7–28 | 0–43 | 1140 |
| 60..100cm | bd.core | kg/m3 | 1180–1470 | 980–1700 | 1140 |
| 60..100cm | soc | g/kg | 3.4–7.3 | 1.3–12.5 | 1140 |
| 60..100cm | ph.h2o | pH | 5.3–7.4 | 4.6–8.5 | 1140 |
