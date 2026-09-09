# Nairobi civil soil screening

1,025 route/station sample locations; 1,025 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 56 |
| fine-soil-plasticity-and-shrink-swell-tests | 963 |
| granular-density-and-groundwater-tests | 569 |
| silt-moisture-frost-and-erosion-review | 42 |

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
| 0..30cm | clay | % | 21–45 | 12–55 | 1025 |
| 0..30cm | sand | % | 17–59 | 3–75 | 1025 |
| 0..30cm | silt | % | 20–39 | 7–50 | 1025 |
| 0..30cm | bd.core | kg/m3 | 1090–1430 | 930–1580 | 1025 |
| 0..30cm | soc | g/kg | 4.2–22.8 | 1.9–42.2 | 1025 |
| 0..30cm | ph.h2o | pH | 5.8–7.6 | 4.9–8.5 | 1025 |
| 30..60cm | clay | % | 20–46 | 8–59 | 1025 |
| 30..60cm | sand | % | 17–62 | 2–82 | 1025 |
| 30..60cm | silt | % | 18–40 | 2–53 | 1025 |
| 30..60cm | bd.core | kg/m3 | 1180–1450 | 1010–1630 | 1025 |
| 30..60cm | soc | g/kg | 2.9–13.1 | 1–22 | 1025 |
| 30..60cm | ph.h2o | pH | 5.8–7.7 | 4.9–8.5 | 1025 |
| 60..100cm | clay | % | 19–45 | 7–59 | 1025 |
| 60..100cm | sand | % | 18–63 | 2–84 | 1025 |
| 60..100cm | silt | % | 18–40 | 1–54 | 1025 |
| 60..100cm | bd.core | kg/m3 | 1210–1490 | 920–1700 | 1025 |
| 60..100cm | soc | g/kg | 1.5–8 | 0.3–15.2 | 1025 |
| 60..100cm | ph.h2o | pH | 5.8–7.8 | 4.8–8.6 | 1025 |
